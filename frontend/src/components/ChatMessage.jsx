import ReactMarkdown from "react-markdown";

// `streaming` = waiting for the first token (show animated dots).
// `caret`     = tokens are arriving (show a blinking caret after the text).
export default function ChatMessage({ role, content, streaming, caret }) {
  const isUser = role === "user";
  return (
    <div className={`message-row ${isUser ? "user" : "assistant"}`}>
      <div className="avatar">{isUser ? "You" : "AI"}</div>
      <div className="bubble">
        {streaming ? (
          <span className="dots">
            <span></span>
            <span></span>
            <span></span>
          </span>
        ) : isUser ? (
          <p>{content}</p>
        ) : (
          <>
            <ReactMarkdown>{content}</ReactMarkdown>
            {caret && <span className="caret" />}
          </>
        )}
      </div>
    </div>
  );
}
