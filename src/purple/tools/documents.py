"""Knowledge-base tools — let Purple learn your documents and manage what she's ingested.
Retrieval (search_documents) is wired in the next slice; this is the write/manage side."""

from __future__ import annotations

from pathlib import Path

from purple.runtime import get_memory
from purple.tools.registry import registry


@registry.tool(
    name="ingest_documents",
    description="Learn a document or a whole folder into Purple's knowledge base so she can "
    "answer from it later. Accepts a file (PDF/Word/Markdown/text) or a folder path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "A file or folder path to ingest."},
            "force": {"type": "boolean", "description": "Re-ingest even if unchanged."},
        },
        "required": ["path"],
    },
)
async def ingest_documents(path: str, force: bool = False) -> str:
    mem = get_memory()
    p = Path(path).expanduser()
    if p.is_dir():
        r = await mem.ingest_folder(path, force=force)
        if not r.get("ok"):
            return r.get("error", "couldn't read that folder")
        return (
            f"Learned {r['ingested']} file(s) ({r['chunks']} passages); "
            f"skipped {r['skipped']} unchanged of {r['files']} supported."
        )
    r = await mem.ingest_file(path, force=force)
    if not r.get("ok"):
        return r.get("error", "couldn't read that file")
    if r.get("skipped"):
        return f"'{r['document']}' is already up to date."
    return f"Learned '{r['document']}' ({r['chunks']} passages)."


@registry.tool(
    name="search_documents",
    description="Search the user's ingested documents and return the most relevant passages "
    "with their source. Use this to answer questions about their files, notes, or docs, and "
    "cite the source document in your reply.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "What to look for."},
            "k": {"type": "integer", "description": "How many passages (default 5)."},
        },
        "required": ["query"],
    },
)
async def search_documents(query: str, k: int = 5) -> list[dict] | str:
    hits = await get_memory().search_documents(query, k)
    return hits or "Nothing relevant in your documents (or none ingested yet)."


@registry.tool(
    name="list_documents",
    description="List the documents in Purple's knowledge base.",
    parameters={"type": "object", "properties": {}, "required": []},
)
async def list_documents() -> list[dict] | str:
    docs = await get_memory().list_documents()
    return docs or "No documents ingested yet — point me at a file or folder."


@registry.tool(
    name="remove_document",
    description="Remove a document (and its passages) from the knowledge base by its id.",
    parameters={
        "type": "object",
        "properties": {"document_id": {"type": "integer", "description": "The document's id."}},
        "required": ["document_id"],
    },
)
async def remove_document(document_id: int) -> str:
    ok = await get_memory().remove_document(document_id)
    return f"Removed document #{document_id}." if ok else f"No document #{document_id}."
