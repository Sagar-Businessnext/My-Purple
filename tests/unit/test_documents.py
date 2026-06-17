"""Document chunking + text extraction tests (pure parts; no DB / no parser libs needed)."""

from __future__ import annotations

from purple import documents


def test_chunk_empty():
    assert documents.chunk_text("") == []
    assert documents.chunk_text("   ") == []


def test_chunk_short_is_single():
    assert documents.chunk_text("hello there friend") == ["hello there friend"]


def test_chunk_long_overlaps_and_covers():
    words = [f"w{i}" for i in range(500)]
    text = " ".join(words)
    chunks = documents.chunk_text(text, size_words=100, overlap_words=20)
    assert len(chunks) > 1
    # each chunk is at most size_words long
    assert all(len(c.split()) <= 100 for c in chunks)
    # overlap: chunk 2 starts 80 words in (step = 100-20)
    assert chunks[1].split()[0] == "w80"
    # full coverage: last word present in the final chunk
    assert "w499" in chunks[-1]


def test_chunk_step_never_zero():
    # overlap >= size shouldn't cause an infinite loop / zero step
    chunks = documents.chunk_text(" ".join(str(i) for i in range(50)), size_words=10, overlap_words=20)
    assert len(chunks) >= 1


def test_is_supported_and_title():
    assert documents.is_supported("a/b/report.PDF") is True
    assert documents.is_supported("notes.md") is True
    assert documents.is_supported("photo.png") is False
    assert documents.title_for("/x/quarterly_report-2026.pdf") == "quarterly report 2026"


def test_extract_text_txt_and_md(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("# Title\n\nSome body text.", encoding="utf-8")
    assert "Some body text." in documents.extract_text(f)
    assert documents.extract_text(tmp_path / "missing.txt") == ""  # never raises


def test_extract_text_unsupported_returns_empty(tmp_path):
    f = tmp_path / "img.png"
    f.write_bytes(b"\x89PNG")
    assert documents.extract_text(f) == ""


def test_file_sha_changes_with_content(tmp_path):
    a = tmp_path / "a.txt"
    a.write_text("one", encoding="utf-8")
    sha1 = documents.file_sha(a)
    a.write_text("two", encoding="utf-8")
    assert documents.file_sha(a) != sha1
