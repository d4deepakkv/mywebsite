import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { api } from "../api";

export default function SummaryPanel({
  summary,
  conversationId,
  onClose,
  onError,
}) {
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);

  function copy() {
    navigator.clipboard?.writeText(summary.content_markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  function downloadMarkdown() {
    const blob = new Blob([summary.content_markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "requirements.md";
    a.click();
    URL.revokeObjectURL(url);
  }

  async function downloadPdf() {
    setDownloading(true);
    try {
      await api.downloadSummaryPdf(conversationId);
    } catch (e) {
      onError?.(e.message);
    } finally {
      setDownloading(false);
    }
  }

  return (
    <>
      <div className="scrim" onClick={onClose} />
      <aside className="summary-pane" role="dialog" aria-label="Requirements summary">
        <div className="summary-header">
          <div>
            <h2>Requirements summary</h2>
            <span className="summary-sub">Captured from your conversation</span>
          </div>
          <button className="icon-btn" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <div className="summary-toolbar">
          <button className="btn primary" onClick={downloadPdf} disabled={downloading}>
            {downloading ? <span className="spinner" /> : <>⬇ PDF</>}
          </button>
          <button className="btn ghost small" onClick={downloadMarkdown}>
            .md
          </button>
          <button className="btn ghost small" onClick={copy}>
            {copied ? "Copied!" : "Copy"}
          </button>
        </div>

        <div className="summary-body markdown">
          <ReactMarkdown>{summary.content_markdown}</ReactMarkdown>
        </div>
      </aside>
    </>
  );
}
