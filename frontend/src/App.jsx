import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import ChatMessage from "./components/ChatMessage.jsx";
import SummaryPanel from "./components/SummaryPanel.jsx";
import Composer from "./components/Composer.jsx";

const STREAM_ID = "__assistant_streaming__";

export default function App() {
  const [bot, setBot] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const [booting, setBooting] = useState(true);
  const [error, setError] = useState("");

  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);

  const scrollRef = useRef(null);

  // Load bot metadata and start a fresh conversation on first mount.
  useEffect(() => {
    (async () => {
      try {
        setBot(await api.getBot());
        const conv = await api.createConversation();
        setConversationId(conv.id);
        setMessages(conv.messages || []);
      } catch (e) {
        setError(e.message);
      } finally {
        setBooting(false);
      }
    })();
  }, []);

  // Auto-scroll to the newest content as it streams in.
  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  async function handleSend(text) {
    const content = text.trim();
    if (!content || streaming || !conversationId) return;
    setError("");

    // Optimistically render the user's message + an empty streaming bubble.
    setMessages((m) => [
      ...m,
      { id: `user-${Date.now()}`, role: "user", content },
      { id: STREAM_ID, role: "assistant", content: "", streaming: true },
    ]);
    setStreaming(true);

    await api.streamMessage(conversationId, content, {
      onDelta: (chunk) =>
        setMessages((m) =>
          m.map((msg) =>
            msg.id === STREAM_ID
              ? { ...msg, content: msg.content + chunk }
              : msg
          )
        ),
      onDone: (message) =>
        setMessages((m) =>
          m.map((msg) => (msg.id === STREAM_ID ? message : msg))
        ),
      onError: (detail) => {
        setError(detail);
        // Drop the empty streaming bubble on failure.
        setMessages((m) => m.filter((msg) => msg.id !== STREAM_ID));
      },
    });
    setStreaming(false);
  }

  async function handleSummary() {
    if (!conversationId) return;
    setSummaryLoading(true);
    setError("");
    try {
      setSummary(await api.generateSummary(conversationId));
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
        <div className="brand">
          <div className="brand-mark">{(bot?.name || "D")[0]}</div>
          <div>
            <h1>
              {bot?.name || "Discovery Assistant"}
              <span className="status-dot" title="Online" />
            </h1>
            {bot?.description && <p className="subtitle">{bot.description}</p>}
          </div>
        </div>
        <div className="header-actions">
          <button
            className="btn primary"
            onClick={handleSummary}
            disabled={!hasUserMessages || summaryLoading || streaming}
            title="Summarise everything captured so far"
          >
            {summaryLoading ? (
              <span className="spinner" />
            ) : (
              <>📋 Requirements</>
            )}
          </button>
          <button className="btn ghost" onClick={handleRestart} title="Start over">
            ＋ New
          </button>
        </div>
      </header>

      <div className="layout">
        <main className="chat-pane">
          <div className="messages" ref={scrollRef}>
            {booting && (
              <div className="boot">
                <span className="spinner" /> Preparing your session…
              </div>
            )}
            {messages.map((m) => (
              <ChatMessage
                key={m.id}
                role={m.role}
                content={m.content}
                streaming={m.streaming && m.content.length === 0}
                caret={m.streaming && m.content.length > 0}
              />
            ))}
          </div>

          {error && (
            <div className="error-banner" role="alert">
              <span>⚠️ {error}</span>
              <button onClick={() => setError("")} aria-label="Dismiss">
                ✕
              </button>
            </div>
          )}

          <Composer onSend={handleSend} disabled={streaming || !conversationId} />
          <p className="composer-hint">
            The assistant asks one question at a time. When you're done, hit{" "}
            <strong>Requirements</strong> to get a summary and PDF.
          </p>
        </main>

        {summary && (
          <SummaryPanel
            summary={summary}
            conversationId={conversationId}
            onError={setError}
            onClose={() => setSummary(null)}
          />
        )}
      </div>
    </div>
  );
}
