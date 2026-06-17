"""Tests for the commit-confirmation safety layer and the screenshot-confirm tap."""

from __future__ import annotations

from purple import safety
from purple.phone import adb
from purple.tools import load_tools, registry


def test_is_commit_label():
    assert safety.is_commit_label("Pay now")
    assert safety.is_commit_label("Place order")
    assert safety.is_commit_label("Send")
    assert not safety.is_commit_label("Search")
    assert not safety.is_commit_label("")


async def test_confirm_denies_without_approver(monkeypatch):
    monkeypatch.setattr(safety.settings, "require_confirmation", True)
    # no approver set in this context -> must deny a sensitive action
    assert await safety.confirm("pay $50?") is False


async def test_confirm_passes_screenshot_to_approver():
    captured: dict = {}

    async def approver(name, args):
        captured.update(args)
        return True

    token = safety.set_current_approver(approver)
    try:
        ok = await safety.confirm("Tap Pay?", screenshot_b64="ABC123")
    finally:
        safety.reset_current_approver(token)
    assert ok is True
    assert captured.get("screenshot_b64") == "ABC123"


async def test_tap_text_confirms_on_commit(monkeypatch):
    load_tools()
    xml = '<hierarchy><node text="Pay now" clickable="true" bounds="[0,0][100,100]"/></hierarchy>'

    async def fake_ui_dump():
        return (0, xml)

    async def fake_run(args, timeout=30.0):
        return (0, "")

    async def fake_screenshot(path):
        return (1, "no screen")  # force screenshot_b64=None, still confirms

    monkeypatch.setattr(adb, "ui_dump", fake_ui_dump)
    monkeypatch.setattr(adb, "run_adb", fake_run)
    monkeypatch.setattr(adb, "screenshot", fake_screenshot)

    asked: list = []

    async def approver(name, args):
        asked.append(name)
        return True

    res = await registry.execute("phone_tap_text", {"text": "Pay"}, approver=approver)
    assert res["ok"] and asked  # a confirmation WAS requested before tapping


async def test_tap_text_skips_confirm_on_safe(monkeypatch):
    load_tools()
    xml = '<hierarchy><node text="Search" clickable="true" bounds="[0,0][100,100]"/></hierarchy>'

    async def fake_ui_dump():
        return (0, xml)

    async def fake_run(args, timeout=30.0):
        return (0, "")

    monkeypatch.setattr(adb, "ui_dump", fake_ui_dump)
    monkeypatch.setattr(adb, "run_adb", fake_run)

    asked: list = []

    async def approver(name, args):
        asked.append(name)
        return True

    res = await registry.execute("phone_tap_text", {"text": "Search"}, approver=approver)
    assert res["ok"] and not asked  # safe label -> no confirmation needed


def test_desktop_modules_import():
    import purple.desktop.hotkey
    import purple.desktop.tray

    assert hasattr(purple.desktop.hotkey, "PushToTalk")
    assert hasattr(purple.desktop.tray, "Tray")
