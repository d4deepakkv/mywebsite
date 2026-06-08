import ReactMarkdown from "react-markdown";

export default function SummaryPanel({ summary, onClose }) {
  function copy() {
    navigator.clipboard?.writeText(summary.content_markdown);
  }

  function download() {
    const blob = new Blob([summary.content_markdown], {
      type: "text/markdown",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "requirements.md";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <aside className="summary-pane">
      <div className="summary-header">
        <h2>Requirements summary</h2>
        <div className="summary-actions">
          <button className="btn ghost small" onClick={copy}>
            Copy
          </button>
          <button className="btn ghost small" onClick={download}>
            Download
          </button>
          <button className="btn ghost small" onClick={onClose}>
            ✕
          </button>
        </div>
      </div>
      <div className="summary-body markdown">
        <ReactMarkdown>{summary.content_markdown}</ReactMarkdown>
      </div>
    </aside>
  );
}
