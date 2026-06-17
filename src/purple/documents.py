"""Document parsing + chunking for the knowledge base (RAG).

extract_text() reads PDF / Word / Markdown / text into plain text (parser libs are
imported lazily so importing this module stays cheap and the chunker is pure + testable).
chunk_text() splits text into overlapping windows for embedding. All local — no network.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from purple.utils.logging import get_logger

log = get_logger("documents")

SUPPORTED = (".pdf", ".docx", ".md", ".markdown", ".txt", ".text")


def chunk_text(text: str, size_words: int = 220, overlap_words: int = 40) -> list[str]:
    """Split text into overlapping word-windows. Pure + deterministic."""
    words = text.split()
    if not words:
        return []
    if len(words) <= size_words:
        return [" ".join(words)]
    step = max(1, size_words - overlap_words)
    chunks: list[str] = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start : start + size_words]))
        if start + size_words >= len(words):
            break
    return chunks


def is_supported(path: str | Path) -> bool:
    return Path(path).suffix.lower() in SUPPORTED


def title_for(path: str | Path) -> str:
    return Path(path).stem.replace("_", " ").replace("-", " ").strip() or Path(path).name


def file_sha(path: str | Path) -> str:
    """SHA-256 of the file's bytes — used to skip re-ingesting unchanged files."""
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def extract_text(path: str | Path) -> str:
    """Best-effort plain text from a supported file. Returns "" on failure/unsupported."""
    p = Path(path)
    suffix = p.suffix.lower()
    try:
        if suffix == ".pdf":
            from pypdf import PdfReader

            reader = PdfReader(str(p))
            return "\n".join((page.extract_text() or "") for page in reader.pages).strip()
        if suffix == ".docx":
            import docx

            doc = docx.Document(str(p))
            return "\n".join(para.text for para in doc.paragraphs).strip()
        if suffix in (".md", ".markdown", ".txt", ".text"):
            return p.read_text(encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        log.warning("extract_failed", path=str(p), error=str(exc))
    return ""
