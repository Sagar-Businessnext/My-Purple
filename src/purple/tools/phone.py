"""Android phone bridge tools (ADB, over USB or Wi-Fi).

Two layers:
  - Curated, typed tools for common/risky actions (launch, dial, SMS) — reliable, and
    commits (call/send/pay) are *prepared* so the user taps the final button.
  - Generic UI primitives (tap, swipe, type, key, ui) so the agent can operate ANY app
    by reading the screen and acting — no need to hand-write a function per task.

Setup: install Android platform-tools, enable USB + Wireless debugging, then connect.
"""

from __future__ import annotations

import base64
from pathlib import Path

from purple.config import settings
from purple.phone import adb
from purple.safety import confirm, is_commit_label
from purple.tools.registry import registry

_EMPTY = {"type": "object", "properties": {}, "required": []}


# --- connection ---
@registry.tool(
    "phone_connect",
    "Connect to the phone over Wi-Fi (ADB). Uses the saved address if none is given.",
    {"type": "object", "properties": {"address": {"type": "string"}}, "required": []},
)
async def phone_connect(address: str | None = None) -> str:
    rc, out = await adb.connect_wireless(address)
    return out.strip() or ("connected" if rc == 0 else f"failed (rc={rc})")


@registry.tool(
    "phone_pair",
    "Pair with the phone over Wi-Fi (Android 11+, one-time). Use the IP:port and code "
    "shown under Wireless debugging > Pair device with pairing code.",
    {
        "type": "object",
        "properties": {"address": {"type": "string"}, "code": {"type": "string"}},
        "required": ["address", "code"],
    },
)
async def phone_pair(address: str, code: str) -> str:
    rc, out = await adb.pair_wireless(address, code)
    return out.strip() or ("paired" if rc == 0 else f"failed (rc={rc})")


@registry.tool("phone_status", "Check which Android phone(s) are connected (USB or Wi-Fi).", _EMPTY)
async def phone_status() -> str:
    devices = await adb.list_devices()
    if devices:
        return "Connected: " + ", ".join(devices)
    return "No phone connected. Pair/connect over Wi-Fi or plug in with USB debugging on."


# --- curated actions ---
@registry.tool(
    "launch_phone_app",
    "Launch an app by package name (e.g. com.android.chrome, com.spotify.music).",
    {"type": "object", "properties": {"package": {"type": "string"}}, "required": ["package"]},
)
async def launch_phone_app(package: str) -> str:
    rc, out = await adb.run_adb(adb.cmd_launch(package))
    return "launched" if rc == 0 else (out.strip() or f"failed (rc={rc})")


@registry.tool(
    "phone_open_url",
    "Open a URL in the phone's browser.",
    {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
)
async def phone_open_url(url: str) -> str:
    rc, out = await adb.run_adb(adb.cmd_open_url(url))
    return "opened on phone" if rc == 0 else (out.strip() or f"failed (rc={rc})")


@registry.tool(
    "phone_dial",
    "Open the dialer pre-filled with a number. The user presses call to connect.",
    {"type": "object", "properties": {"number": {"type": "string"}}, "required": ["number"]},
)
async def phone_dial(number: str) -> str:
    rc, out = await adb.run_adb(adb.cmd_dial(number))
    return (
        f"Dialer open for {number} — press call on your phone to connect."
        if rc == 0
        else out.strip() or f"failed (rc={rc})"
    )


@registry.tool(
    "phone_compose_sms",
    "Open the SMS composer pre-filled. The user presses send.",
    {
        "type": "object",
        "properties": {"number": {"type": "string"}, "body": {"type": "string"}},
        "required": ["number", "body"],
    },
)
async def phone_compose_sms(number: str, body: str) -> str:
    rc, out = await adb.run_adb(adb.cmd_compose_sms(number, body))
    return (
        f"SMS to {number} drafted — review and press send on your phone."
        if rc == 0
        else out.strip() or f"failed (rc={rc})"
    )


@registry.tool(
    "phone_notifications",
    "Read recent notifications from the phone.",
    {"type": "object", "properties": {"limit": {"type": "integer"}}, "required": []},
)
async def phone_notifications(limit: int = 10) -> list[str] | str:
    _rc, out = await adb.run_adb(adb.cmd_notifications())
    return adb.parse_notifications(out, limit) or "No notifications found."


@registry.tool(
    "phone_screenshot", "Screenshot the phone screen; returns the saved file path.", _EMPTY
)
async def phone_screenshot() -> str:
    settings.ensure_dirs()
    path = str(settings.data_dir / "phone_screen.png")
    rc, result = await adb.screenshot(path)
    return f"Saved screenshot to {result}" if rc == 0 else result


# --- generic UI automation (drive any app) ---
@registry.tool(
    "phone_ui",
    "Read the on-screen elements (labels + tap coordinates) so you can decide what to "
    "tap next. Use before phone_tap when navigating an app you don't have a tool for.",
    _EMPTY,
)
async def phone_ui() -> list[dict] | str:
    rc, xml = await adb.ui_dump()
    if rc != 0:
        return xml.strip() or f"failed (rc={rc})"
    return adb.parse_ui_hierarchy(xml) or "No readable UI elements."


@registry.tool(
    "phone_tap",
    "Tap the screen at pixel coordinates (from phone_ui or a screenshot).",
    {
        "type": "object",
        "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}},
        "required": ["x", "y"],
    },
)
async def phone_tap(x: int, y: int) -> str:
    rc, out = await adb.run_adb(adb.cmd_tap(x, y))
    return "tapped" if rc == 0 else (out.strip() or f"failed (rc={rc})")


async def _screenshot_b64() -> str | None:
    import tempfile

    fh = tempfile.NamedTemporaryFile(suffix=".png", delete=False)  # noqa: SIM115
    fh.close()
    rc, _ = await adb.screenshot(fh.name)
    if rc != 0:
        return None
    with Path(fh.name).open("rb") as f:
        return base64.b64encode(f.read()).decode()


@registry.tool(
    "phone_tap_text",
    "Tap the on-screen element whose label matches `text` (find it via phone_ui). If the "
    "label looks like a commit (Pay, Send, Confirm, Place order...), Purple screenshots "
    "the screen and asks you before tapping.",
    {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
)
async def phone_tap_text(text: str) -> str:
    rc, xml = await adb.ui_dump()
    if rc != 0:
        return xml.strip() or "couldn't read the screen"
    match = next(
        (e for e in adb.parse_ui_hierarchy(xml, limit=200) if text.lower() in e["label"].lower()),
        None,
    )
    if not match:
        return f"no on-screen element matching '{text}'"
    if is_commit_label(match["label"]):
        shot = await _screenshot_b64()
        if not await confirm(f"Tap '{match['label']}' on your phone?", screenshot_b64=shot):
            return "cancelled — you didn't confirm this commit"
    rc, out = await adb.run_adb(adb.cmd_tap(match["x"], match["y"]))
    return f"tapped '{match['label']}'" if rc == 0 else (out.strip() or f"failed (rc={rc})")


@registry.tool(
    "phone_swipe",
    "Swipe from (x1,y1) to (x2,y2). Use for scrolling or gestures.",
    {
        "type": "object",
        "properties": {
            "x1": {"type": "integer"},
            "y1": {"type": "integer"},
            "x2": {"type": "integer"},
            "y2": {"type": "integer"},
            "ms": {"type": "integer"},
        },
        "required": ["x1", "y1", "x2", "y2"],
    },
)
async def phone_swipe(x1: int, y1: int, x2: int, y2: int, ms: int = 300) -> str:
    rc, out = await adb.run_adb(adb.cmd_swipe(x1, y1, x2, y2, ms))
    return "swiped" if rc == 0 else (out.strip() or f"failed (rc={rc})")


@registry.tool(
    "phone_type",
    "Type text into the focused field on the phone.",
    {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
)
async def phone_type(text: str) -> str:
    rc, out = await adb.run_adb(adb.cmd_text(text))
    return "typed" if rc == 0 else (out.strip() or f"failed (rc={rc})")


@registry.tool(
    "phone_key",
    "Press a hardware/navigation key by Android keycode (HOME=3, BACK=4, ENTER=66, "
    "APP_SWITCH=187, VOLUME_UP=24, VOLUME_DOWN=25).",
    {"type": "object", "properties": {"keycode": {"type": "integer"}}, "required": ["keycode"]},
)
async def phone_key(keycode: int) -> str:
    rc, out = await adb.run_adb(adb.cmd_key(keycode))
    return "pressed" if rc == 0 else (out.strip() or f"failed (rc={rc})")


@registry.tool(
    "phone_shell",
    "Run a raw `adb shell` command on the phone. Powerful — only when no other tool fits.",
    {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
    requires_confirmation=True,
)
async def phone_shell(command: str) -> str:
    rc, out = await adb.run_adb(["shell", command])
    return f"rc={rc}\n{out.strip()[:3000]}"
