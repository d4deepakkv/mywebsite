// Tiny API helper around the FastAPI backend. All paths are relative so the
// Vite dev proxy (or same-origin deploy) handles routing to the backend.

async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch {
      /* ignore non-JSON error bodies */
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  getBot: () => request("/bot"),

  createConversation: (info = {}) =>
    request("/conversations", { method: "POST", body: JSON.stringify(info) }),

  getConversation: (id) => request(`/conversations/${id}`),

  generateSummary: (id) =>
    request(`/conversations/${id}/summary`, { method: "POST" }),

  // Stream the assistant's reply over SSE. Calls onDelta(text) as chunks
  // arrive, onDone(message) with the final persisted message, onError(detail).
  async streamMessage(id, content, { onDelta, onDone, onError }) {
    let res;
    try {
      res = await fetch(`/api/conversations/${id}/messages/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
      });
    } catch (e) {
      onError?.(e.message || "Network error");
      return;
    }
    if (!res.ok || !res.body) {
      let detail = `Request failed (${res.status})`;
      try {
        detail = (await res.json()).detail || detail;
      } catch {
        /* ignore */
      }
      onError?.(detail);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      // SSE events are separated by a blank line.
      const events = buffer.split("\n\n");
      buffer = events.pop() ?? "";
      for (const event of events) {
        const dataLine = event
          .split("\n")
          .find((l) => l.startsWith("data: "));
        if (!dataLine) continue;
        let obj;
        try {
          obj = JSON.parse(dataLine.slice(6));
        } catch {
          continue;
        }
        if (obj.type === "delta") onDelta?.(obj.text);
        else if (obj.type === "done") onDone?.(obj.message);
        else if (obj.type === "error") onError?.(obj.detail);
      }
    }
  },

  // Fetch the requirements PDF as a blob and trigger a browser download.
  async downloadSummaryPdf(id, { regenerate = false } = {}) {
    const url = `/api/conversations/${id}/summary.pdf${
      regenerate ? "?regenerate=true" : ""
    }`;
    const res = await fetch(url);
    if (!res.ok) {
      let detail = `Could not generate PDF (${res.status})`;
      try {
        detail = (await res.json()).detail || detail;
      } catch {
        /* ignore */
      }
      throw new Error(detail);
    }
    const blob = await res.blob();
    const href = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = href;
    a.download = "requirements.pdf";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(href);
  },
};
