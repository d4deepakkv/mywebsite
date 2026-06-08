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

  sendMessage: (id, content) =>
    request(`/conversations/${id}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),

  generateSummary: (id) =>
    request(`/conversations/${id}/summary`, { method: "POST" }),
};
