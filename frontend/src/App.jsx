import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import ChatMessage from "./components/ChatMessage.jsx";
import SummaryPanel from "./components/SummaryPanel.jsx";

export default function App() {
  const [bot, setBot] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);

  const scrollRef = useRef(null);

  // Load bot metadata and start a fresh conversation on first mount.
  useEffect(() => {
    (async () => {
      try {
        const botInfo = await api.getBot();
        setBot(botInfo);
        const conv = await api.createConversation();
        setConversationId(conv.id);
        setMessages(conv.messages || []);
      } catch (e) {
        setError(e.message);
      }
    })();
  }, []);

  // Auto-scroll to the newest message.
  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, sending]);

  async function handleSend(e) {
    e?.preventDefault();
    const text = input.trim();
    if (!text || sending || !conversationId) return;

    setError("");
    setInput("");
    // Optimistically render the user's message.
    setMessages((m) => [
      ...m,
      { id: `tmp-${Date.now()}`, role: "user", content: text },
    ]);
    setSending(true);
    try {
      const { message } = await api.sendMessage(conversationId, text);
      setMessages((m) => [...m, message]);
    } catch (e) {
      setError(e.message);
    } finally {
      setSending(false);
    }
  }

  async function handleSummary() {
    if (!conversationId) return;
    setSummaryLoading(true);
    setError("");
    try {
      const req = await api.generateSummary(conversationId);
      setSummary(req);
    } catch (e) {
      setError(e.message);
    } finally {
      setSummaryLoading(false);
    }
  }

  async function handleRestart() {
    setSummary(null);
    setError("");
    try {
      const conv = await api.createConversation();
      setConversationId(conv.id);
      setMessages(conv.messages || []);
    } catch (e) {
      setError(e.message);
    }
  }

  const hasUserMessages = messages.some((m) => m.role === "user");

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>{bot?.name || "Discovery Assistant"}</h1>
          {bot?.description && <p className="subtitle">{bot.description}</p>}
        </div>
        <div className="header-actions">
          <button
            className="btn ghost"
            onClick={handleSummary}
            disabled={!hasUserMessages || summaryLoading}
            title="Generate a requirements summary from this conversation"
          >
            {summaryLoading ? "Summarising…" : "Generate requirements"}
          </button>
          <button className="btn ghost" onClick={handleRestart}>
            New session
          </button>
        </div>
      </header>

      <div className="layout">
        <main className="chat-pane">
          <div className="messages" ref={scrollRef}>
            {messages.map((m) => (
              <ChatMessage key={m.id} role={m.role} content={m.content} />
            ))}
            {sending && (
              <ChatMessage role="assistant" content="…" typing />
            )}
          </div>

          {error && <div className="error-banner">{error}</div>}

          <form className="composer" onSubmit={handleSend}>
            <textarea
              value={input}
              placeholder="Type your answer…"
              rows={1}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) handleSend(e);
              }}
              disabled={sending || !conversationId}
            />
            <button
              className="btn primary"
              type="submit"
              disabled={sending || !input.trim()}
            >
              Send
            </button>
          </form>
        </main>

        {summary && (
          <SummaryPanel
            summary={summary}
            onClose={() => setSummary(null)}
          />
        )}
      </div>
    </div>
  );
}
