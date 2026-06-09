"""Render a requirements summary (Markdown) into a polished PDF document.

Uses ``markdown`` to convert to HTML and ``xhtml2pdf`` (pure-Python, no system
libraries required) to render the HTML to a PDF byte string.
"""
from __future__ import annotations

import io
from datetime import datetime
from html import escape

import markdown as md
from xhtml2pdf import pisa

# xhtml2pdf supports a practical subset of CSS. Keep the styling simple and
# print-friendly: a cover heading, clear section headers, and readable body.
_CSS = """
@page {
    size: a4;
    margin: 2.2cm 2cm 2.4cm 2cm;
    @frame footer { -pdf-frame-content: footerContent; bottom: 1.1cm;
                    margin-left: 2cm; margin-right: 2cm; height: 1cm; }
}
body { font-family: Helvetica, Arial, sans-serif; font-size: 10.5pt;
       color: #222; line-height: 1.5; }
.cover { border-bottom: 2pt solid #4f46e5; padding-bottom: 10pt;
         margin-bottom: 18pt; }
.cover h1 { color: #312e81; font-size: 20pt; margin: 0 0 4pt 0; }
.cover .meta { color: #6b7280; font-size: 9pt; }
h2 { color: #4f46e5; font-size: 13pt; margin: 16pt 0 4pt 0;
     border-bottom: 0.6pt solid #e5e7eb; padding-bottom: 2pt; }
h3 { color: #374151; font-size: 11pt; margin: 10pt 0 2pt 0; }
p { margin: 4pt 0; }
ul, ol { margin: 4pt 0 4pt 0; }
li { margin: 2pt 0; }
code { background: #f3f4f6; font-family: Courier, monospace; font-size: 9.5pt; }
strong { color: #111827; }
.footer { color: #9ca3af; font-size: 8pt; text-align: center; }
"""


def render_summary_pdf(
    markdown_text: str,
    *,
    title: str = "Discovery Requirements",
    subtitle: str | None = None,
    generated_at: datetime | None = None,
) -> bytes:
    """Convert a Markdown requirements summary into PDF bytes."""
    body_html = md.markdown(
        markdown_text, extensions=["extra", "sane_lists", "nl2br"]
    )
    when = (generated_at or datetime.utcnow()).strftime("%d %b %Y, %H:%M UTC")
    meta_line = escape(subtitle) + " &middot; " if subtitle else ""

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{_CSS}</style></head>
<body>
  <div id="footerContent" class="footer">
    {escape(title)} — generated {when}
  </div>
  <div class="cover">
    <h1>{escape(title)}</h1>
    <div class="meta">{meta_line}Generated {when}</div>
  </div>
  {body_html}
</body></html>"""

    buffer = io.BytesIO()
    result = pisa.CreatePDF(src=html, dest=buffer, encoding="utf-8")
    if result.err:
        raise RuntimeError("Failed to render the requirements PDF")
    return buffer.getvalue()
