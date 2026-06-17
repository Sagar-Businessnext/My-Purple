"""Tests for the PC file tools (cross-platform, real temp dirs) and that delete is
confirmation-gated. System tools (windows/media/clipboard/power) are import-checked."""

from __future__ import annotations

from purple.tools import load_tools, registry


async def _allow(_n, _a):
    return True


async def test_file_lifecycle(tmp_path):
    load_tools()
    f = tmp_path / "note.txt"

    r = await registry.execute(
        "write_text_file", {"path": str(f), "content": "hello world"}, approver=_allow
    )
    assert r["ok"] and f.read_text() == "hello world"

    r = await registry.execute("read_text_file", {"path": str(f)}, approver=_allow)
    assert "hello world" in r["result"]

    r = await registry.execute("list_dir", {"path": str(tmp_path)}, approver=_allow)
    assert any("note.txt" in x for x in r["result"])

    r = await registry.execute(
        "search_files", {"query": "*.txt", "root": str(tmp_path)}, approver=_allow
    )
    assert any("note.txt" in x for x in r["result"])

    sub = tmp_path / "sub"
    await registry.execute("make_dir", {"path": str(sub)}, approver=_allow)
    assert sub.is_dir()

    await registry.execute(
        "move_path", {"src": str(f), "dst": str(sub / "note.txt")}, approver=_allow
    )
    assert (sub / "note.txt").exists() and not f.exists()


async def test_delete_is_confirmation_gated(tmp_path):
    load_tools()
    f = tmp_path / "x.txt"
    f.write_text("bye")

    async def deny(_n, _a):
        return False

    r = await registry.execute("delete_path", {"path": str(f)}, approver=deny)
    assert r["ok"] is False and f.exists()  # blocked, file untouched

    r = await registry.execute("delete_path", {"path": str(f)}, approver=_allow)
    assert r["ok"] and not f.exists()  # confirmed, gone


async def test_media_control_rejects_unknown_action():
    load_tools()
    r = await registry.execute("media_control", {"action": "explode"}, approver=_allow)
    assert r["ok"] and "unknown" in r["result"]


def test_system_pc_module_imports():
    import purple.tools.system_pc as sp

    assert hasattr(sp, "media_control") and hasattr(sp, "lock_screen")
