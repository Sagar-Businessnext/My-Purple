"""Tests for the Android phone bridge: ADB parsing, command builders, and tools
(with a fake adb runner — no device needed)."""

from __future__ import annotations

from purple.phone import adb
from purple.tools import load_tools, registry


def test_parse_devices_skips_header_and_offline():
    out = "List of devices attached\nABC123\tdevice\nXYZ789\toffline\n"
    assert adb.parse_devices(out) == ["ABC123"]


def test_command_builders():
    assert adb.cmd_open_url("https://x.com")[-1] == "https://x.com"
    assert adb.cmd_dial("12345")[-1] == "tel:12345"
    sms = adb.cmd_compose_sms("12345", "hi there")
    assert "sms:12345" in sms and "hi there" in sms
    assert adb.cmd_launch("com.android.chrome")[3] == "com.android.chrome"


def test_parse_notifications():
    dump = (
        "android.title=String (WhatsApp) extra android.text=String (Hi there) more "
        "android.title=String (Gmail) android.text=String (Team meeting at 3)"
    )
    notes = adb.parse_notifications(dump)
    assert "WhatsApp: Hi there" in notes
    assert any("Gmail" in n for n in notes)


async def test_phone_dial_prepares_not_calls(monkeypatch):
    load_tools()

    async def fake_run(args, timeout=30.0):
        return (0, "")

    monkeypatch.setattr(adb, "run_adb", fake_run)

    async def allow(_n, _a):
        return True

    res = await registry.execute("phone_dial", {"number": "555123"}, approver=allow)
    assert res["ok"] and "555123" in res["result"] and "press call" in res["result"].lower()


async def test_phone_shell_is_confirmation_gated(monkeypatch):
    load_tools()

    async def fake_run(args, timeout=30.0):
        return (0, "ran")

    monkeypatch.setattr(adb, "run_adb", fake_run)

    async def deny(_n, _a):
        return False

    res = await registry.execute("phone_shell", {"command": "reboot"}, approver=deny)
    assert res["ok"] is False  # blocked because the user didn't confirm


def test_connection_builders():
    assert adb.cmd_connect("192.168.1.50:5555") == ["connect", "192.168.1.50:5555"]
    assert adb.cmd_pair("192.168.1.50:37000", "123456") == [
        "pair",
        "192.168.1.50:37000",
        "123456",
    ]


def test_ui_command_builders():
    assert adb.cmd_tap(10, 20) == ["shell", "input", "tap", "10", "20"]
    assert adb.cmd_swipe(1, 2, 3, 4, 500)[-1] == "500"
    assert adb.cmd_text("hi there") == ["shell", "input", "text", "hi%sthere"]
    assert adb.cmd_key(4) == ["shell", "input", "keyevent", "4"]


def test_parse_ui_hierarchy_extracts_labels_and_centers():
    xml = (
        "<hierarchy>"
        '<node text="Send" resource-id="com.app:id/send_btn" clickable="true" bounds="[100,200][300,260]"/>'
        '<node text="" content-desc="Back" clickable="true" bounds="[0,0][80,80]"/>'
        '<node text="ignored" clickable="false" bounds="[0,0][0,0]"/>'
        "</hierarchy>"
    )
    els = adb.parse_ui_hierarchy(xml)
    labels = {e["label"] for e in els}
    assert "Send" in labels and "Back" in labels
    send = next(e for e in els if e["label"] == "Send")
    assert send["x"] == 200 and send["y"] == 230 and send["id"] == "send_btn"
