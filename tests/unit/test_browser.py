"""Browser tool tests — focus on the commit-guard (click confirmation), with the
controller's network methods faked so no real browser is launched."""

from __future__ import annotations

from purple.browser.controller import browser
from purple.tools import load_tools, registry


async def test_browser_click_confirms_on_commit(monkeypatch):
    load_tools()

    async def fake_shot():
        return "B64DATA"

    async def fake_click(text):
        return f"clicked {text}"

    monkeypatch.setattr(browser, "screenshot_b64", fake_shot)
    monkeypatch.setattr(browser, "click_text", fake_click)

    asked: list = []

    async def approver(name, args):
        asked.append(args)
        return True

    res = await registry.execute("browser_click", {"text": "Buy now"}, approver=approver)
    assert res["ok"] and asked and asked[0].get("screenshot_b64") == "B64DATA"


async def test_browser_click_skips_confirm_on_safe(monkeypatch):
    load_tools()

    async def fake_click(text):
        return f"clicked {text}"

    monkeypatch.setattr(browser, "click_text", fake_click)

    asked: list = []

    async def approver(name, args):
        asked.append(args)
        return True

    res = await registry.execute("browser_click", {"text": "Search"}, approver=approver)
    assert res["ok"] and not asked


async def test_browser_click_cancelled_does_not_click(monkeypatch):
    load_tools()
    clicked = {"v": False}

    async def fake_shot():
        return None

    async def fake_click(text):
        clicked["v"] = True
        return "clicked"

    monkeypatch.setattr(browser, "screenshot_b64", fake_shot)
    monkeypatch.setattr(browser, "click_text", fake_click)

    async def deny(name, args):
        return False

    res = await registry.execute("browser_click", {"text": "Pay"}, approver=deny)
    assert res["ok"] and "cancelled" in res["result"] and clicked["v"] is False
