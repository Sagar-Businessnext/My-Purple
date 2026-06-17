"""Vision tool tests — coordinate parsing and the look-and-click commit-guard, with the
VLM, screenshot and click all faked (no GPU/screen needed)."""

from __future__ import annotations

from purple.tools import desktop_ui as du
from purple.tools import load_tools, registry
from purple.tools import vision as vmod
from purple.vision.provider import provider


def test_parse_point():
    assert vmod.parse_point("click at 120, 340 please") == (120, 340)
    assert vmod.parse_point("none") is None


def _wire(monkeypatch, coords="100,200"):
    clicked: list = []

    async def fake_grab():
        return b"img"

    async def fake_look(image, prompt):
        return coords

    async def fake_click_at(x, y):
        clicked.append((x, y))

    monkeypatch.setattr(vmod, "_grab_screen", fake_grab)
    monkeypatch.setattr(provider, "look", fake_look)
    monkeypatch.setattr(du, "_click_at", fake_click_at)
    return clicked


async def test_look_and_click_confirms_on_commit(monkeypatch):
    load_tools()
    clicked = _wire(monkeypatch)
    asked: list = []

    async def approver(name, args):
        asked.append(args)
        return True

    res = await registry.execute("look_and_click", {"target": "Pay now"}, approver=approver)
    assert res["ok"] and clicked == [(100, 200)]
    assert asked and asked[0].get("screenshot_b64")  # screenshot attached to the prompt


async def test_look_and_click_safe_target_no_confirm(monkeypatch):
    load_tools()
    clicked = _wire(monkeypatch, "50,60")
    asked: list = []

    async def approver(name, args):
        asked.append(args)
        return True

    res = await registry.execute("look_and_click", {"target": "the search box"}, approver=approver)
    assert res["ok"] and not asked and clicked == [(50, 60)]


async def test_look_and_click_cancel_blocks_click(monkeypatch):
    load_tools()
    clicked = _wire(monkeypatch)

    async def deny(name, args):
        return False

    res = await registry.execute("look_and_click", {"target": "Confirm purchase"}, approver=deny)
    assert res["ok"] and "cancelled" in res["result"] and not clicked
