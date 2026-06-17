"""File-system tools — let Purple find, read, write, and organise files on the PC.

Paths accept ~ and environment variables. Destructive actions (delete) are
confirmation-gated; delete prefers the Recycle Bin when send2trash is available.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil

from purple.tools.registry import registry


def _expand(p: str) -> Path:
    return Path(os.path.expandvars(p)).expanduser().resolve()


@registry.tool(
    "list_dir",
    "List the files and folders in a directory (default: home).",
    {"type": "object", "properties": {"path": {"type": "string"}}, "required": []},
)
async def list_dir(path: str = "~") -> list[str] | str:
    d = _expand(path)
    if not d.is_dir():
        return f"not a directory: {d}"
    items = [("[dir] " if e.is_dir() else "") + e.name for e in sorted(d.iterdir())]
    return items[:200] or "(empty)"


@registry.tool(
    "search_files",
    "Find files by name/glob (e.g. '*.pdf', 'invoice*') under a folder.",
    {
        "type": "object",
        "properties": {"query": {"type": "string"}, "root": {"type": "string"}},
        "required": ["query"],
    },
)
async def search_files(query: str, root: str = "~") -> list[str] | str:
    base = _expand(root)
    if not base.is_dir():
        return f"not a directory: {base}"
    hits: list[str] = []
    for p in base.rglob(query):
        hits.append(str(p))
        if len(hits) >= 100:
            break
    return hits or f"no files matching '{query}' under {base}"


@registry.tool(
    "read_text_file",
    "Read a text file's contents (first ~8000 characters).",
    {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
)
async def read_text_file(path: str) -> str:
    f = _expand(path)
    if not f.is_file():
        return f"not a file: {f}"
    try:
        return f.read_text(encoding="utf-8", errors="replace")[:8000]
    except Exception as exc:
        return f"error reading: {exc}"


@registry.tool(
    "write_text_file",
    "Create or overwrite a text file with the given content.",
    {
        "type": "object",
        "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
        "required": ["path", "content"],
    },
)
async def write_text_file(path: str, content: str) -> str:
    f = _expand(path)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    return f"wrote {len(content)} chars to {f}"


@registry.tool(
    "make_dir",
    "Create a folder (and any missing parent folders).",
    {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
)
async def make_dir(path: str) -> str:
    d = _expand(path)
    d.mkdir(parents=True, exist_ok=True)
    return f"created {d}"


@registry.tool(
    "move_path",
    "Move or rename a file or folder.",
    {
        "type": "object",
        "properties": {"src": {"type": "string"}, "dst": {"type": "string"}},
        "required": ["src", "dst"],
    },
)
async def move_path(src: str, dst: str) -> str:
    s, d = _expand(src), _expand(dst)
    shutil.move(str(s), str(d))
    return f"moved to {d}"


@registry.tool(
    "copy_path",
    "Copy a file or folder.",
    {
        "type": "object",
        "properties": {"src": {"type": "string"}, "dst": {"type": "string"}},
        "required": ["src", "dst"],
    },
)
async def copy_path(src: str, dst: str) -> str:
    s, d = _expand(src), _expand(dst)
    if s.is_dir():
        shutil.copytree(s, d)
    else:
        shutil.copy2(s, d)
    return f"copied to {d}"


@registry.tool(
    "open_path",
    "Open a file or folder with its default application.",
    {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
)
async def open_path(path: str) -> str:
    p = _expand(path)
    try:
        if hasattr(os, "startfile"):
            os.startfile(str(p))  # type: ignore[attr-defined]  # Windows
        else:
            import subprocess

            subprocess.Popen(["xdg-open", str(p)])
        return f"opened {p}"
    except Exception as exc:
        return f"error: {exc}"


@registry.tool(
    "delete_path",
    "Delete a file or folder (sent to the Recycle Bin when possible).",
    {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    requires_confirmation=True,
)
async def delete_path(path: str) -> str:
    p = _expand(path)
    if not p.exists():
        return f"does not exist: {p}"
    try:
        from send2trash import send2trash

        send2trash(str(p))
        return f"sent to Recycle Bin: {p}"
    except Exception:
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return f"deleted {p}"
