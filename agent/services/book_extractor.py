"""Book text extraction: PDF and EPUB → plain text chunks."""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MAX_TOKENS_PER_CHUNK = 8000
AVG_CHARS_PER_TOKEN = 4


def extract_pdf(path: str) -> str:
    """Extract all text from a PDF file. Raises ValueError if no text layer found."""
    try:
        from pypdf import PdfReader
    except ImportError:
        raise RuntimeError("pypdf not installed. Run: pip install pypdf>=4.0.0")

    reader = PdfReader(path)
    pages_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages_text.append(f"[Page {i + 1}]\n{text.strip()}")

    if not pages_text:
        raise ValueError(
            "No text layer found in PDF. This may be a scanned image PDF. "
            "Please run OCR (e.g. ocrmypdf) before using this tool."
        )

    full_text = "\n\n".join(pages_text)
    logger.info("Extracted %d pages from PDF: %s", len(pages_text), path)
    return full_text


def extract_epub(path: str) -> str:
    """Extract all chapter text from an EPUB file."""
    try:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup
    except ImportError:
        raise RuntimeError(
            "ebooklib/beautifulsoup4 not installed. "
            "Run: pip install ebooklib>=0.18 beautifulsoup4>=4.12.0"
        )

    book = epub.read_epub(path)
    chapters = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        if text.strip():
            chapters.append(text)

    if not chapters:
        raise ValueError("No readable content found in EPUB.")

    full_text = "\n\n---\n\n".join(chapters)
    logger.info("Extracted %d chapters from EPUB: %s", len(chapters), path)
    return full_text


def extract_book(path: str) -> str:
    """Dispatch to PDF or EPUB extractor based on file extension."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = p.suffix.lower()
    if ext == ".pdf":
        return extract_pdf(path)
    elif ext == ".epub":
        return extract_epub(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use .pdf or .epub")


def chunk_text(text: str, max_tokens: int = MAX_TOKENS_PER_CHUNK) -> list[str]:
    """Split text into chunks suitable for Gemini context window."""
    max_chars = max_tokens * AVG_CHARS_PER_TOKEN
    if len(text) <= max_chars:
        return [text]

    chunks = []
    paragraphs = text.split("\n\n")
    current = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para)
        if current_len + para_len > max_chars and current:
            chunks.append("\n\n".join(current))
            current = [para]
            current_len = para_len
        else:
            current.append(para)
            current_len += para_len

    if current:
        chunks.append("\n\n".join(current))

    logger.info("Split text into %d chunks (max %d tokens each)", len(chunks), max_tokens)
    return chunks
