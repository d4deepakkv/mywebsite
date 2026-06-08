import ReactMarkdown from "react-markdown";

export default function ChatMessage({ role, content, typing = false }) {
  const isUser = role === "user";
  return (
    <div className={`message-row ${isUser ? "user" : "assistant"}`}>
      <div className="avatar">{isUser ? "You" : "AI"}</div>
      <div className={`bubble ${typing ? "typing" : ""}`}>
        {typing ? (
          <span className="dots">
            <span></span>
            <span></span>
            <span></span>
          </span>
        ) : isUser ? (
          <p>{content}</p>
        ) : (
          <ReactMarkdown>{content}</ReactMarkdown>
        )}
      </div>
    </div>
  );
}
