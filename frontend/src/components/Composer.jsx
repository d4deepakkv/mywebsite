import { useRef, useState } from "react";

// Pill-style composer with an auto-growing textarea and an inline send button.
export default function Composer({ onSend, disabled }) {
  const [value, setValue] = useState("");
  const ref = useRef(null);

  function autoGrow(el) {
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 180) + "px";
  }

  function submit() {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
    if (ref.current) ref.current.style.height = "auto";
  }

  return (
    <div className={`composer ${disabled ? "is-disabled" : ""}`}>
      <textarea
        ref={ref}
        value={value}
        rows={1}
        placeholder={disabled ? "Assistant is replying…" : "Type your answer…"}
        onChange={(e) => {
          setValue(e.target.value);
          autoGrow(e.target);
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit();
          }
        }}
        disabled={disabled}
      />
      <button
        className="send-btn"
        onClick={submit}
        disabled={disabled || !value.trim()}
        aria-label="Send"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path
            d="M3 11.5 21 3l-8.5 18-2.2-7.3L3 11.5Z"
            fill="currentColor"
          />
        </svg>
      </button>
    </div>
  );
}
