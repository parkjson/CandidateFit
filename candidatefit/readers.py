"""
readers.py
====================================
Turns resume and posting files into plain text.

Supported: .txt / .md (as-is), .html / .htm (a saved job page; on a LinkedIn
page only the job description is kept), and .pdf (needs ``pip install
candidatefit[pdf]``).
"""

from pathlib import Path


def html_to_text(html):
    """Visible text of an HTML page, keeping line breaks between blocks."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    # LinkedIn job pages: keep just the description, not nav and sidebars.
    desc = soup.find("div", {"class": "jobs-description"})
    return (desc or soup).get_text("\n", strip=True)


def pdf_to_text(path):
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise SystemExit(
            "Reading PDFs needs pypdf: pip install 'candidatefit[pdf]'"
        ) from e
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


def read_text(path):
    """Reads ``path`` as plain text based on its extension."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return pdf_to_text(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    if suffix in (".html", ".htm"):
        return html_to_text(text)
    return text
