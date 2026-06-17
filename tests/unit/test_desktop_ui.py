"""PC UI-automation tests — commit-guard on pc_click_text, with the uiautomation/
pyautogui helpers faked so no real screen is touched."""

from __future__ import annotations

from purple.tools import desktop_ui as du
from purple.tools import load_tools, registry


async def test_pc_click_text_confirms_on_commit(monkeypatch):
    load_tools()
    clicked: list = []

    async def fake_find(text):
        return ("Pay now", 100, 200)

    async def fake_shot():
        return "B64"

    async def fake_click_at(x, y):
        clicked.append((x, y))

    monkeypatch.setattr(du, "_find_point", fake_find)
    monkeypatch.setattr(du, "_screenshot_b64", fake_shot)
    monkeypatch.setattr(du, "_click_at", fake_click_at)

    asked: list = []

    async def approver(name, args):
        asked.append(args)
        return True

    res = await registry.execute("pc_click_text", {"text": "Pay"}, approver=approver)
    assert res["ok"] and asked and clicked == [(100, 200)]


async def test_pc_click_text_safe_skips_confirm(monkeypatch):
    load_tools()

    async def fake_find(text):
        return ("Search box", 10, 20)

    async def fake_click_at(x, y):
        return None

    monkeypatch.setattr(du, "_find_point", fake_find)
    monkeypatch.setattr(du, "_click_at", fake_click_at)

    asked: list = []

    async def approver(name, args):
        asked.append(args)
        return True

    res = await registry.execute("pc_click_text", {"text": "Search"}, approver=approver)
    assert res["ok"] and not asked


async def test_pc_click_text_cancel_blocks_click(monkeypatch):
    load_tools()
    clicked: list = []

    async def fake_find(text):
        return ("Confirm order", 5, 5)

    async def fake_shot():
        return None

    async def fake_click_at(x, y):
        clicked.append((x, y))

    monkeypatch.setattr(du, "_find_point", fake_find)
    monkeypatch.setattr(du, "_screenshot_b64", fake_shot)
    monkeypatch.setattr(du, "_click_at", fake_click_at)

    async def deny(name, args):
        return False

    res = await registry.execute("pc_click_text", {"text": "Confirm"}, approver=deny)
    assert res["ok"] and "cancelled" in res["result"] and not clicked
