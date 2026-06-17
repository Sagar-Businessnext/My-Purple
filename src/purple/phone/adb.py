"""Async ADB wrapper — works over USB and over Wi-Fi.

ADB supports both: plug in once (or pair over Wi-Fi on Android 11+) and every command
here works the same. Command *builders* are pure functions (unit-tested); the runners
execute them. Device-targeted commands honour PURPLE_PHONE_SERIAL; connection commands
(connect/pair/devices) are global and must not carry a serial.

Setup: install Android platform-tools, enable USB debugging (and Wireless debugging on
Android 11+), then either `adb connect <ip>:<port>` or pair once.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from purple.config import settings
from purple.utils.logging import get_logger

log = get_logger("phone.adb")


def _global_base() -> list[str]:
    return [settings.adb_path]


def _base() -> list[str]:
    cmd = [settings.adb_path]
    if settings.phone_serial:
        cmd += ["-s", settings.phone_serial]
    return cmd


# --- device-targeted command builders (testable) ---
def cmd_devices() -> list[str]:
    return ["devices"]


def cmd_open_url(url: str) -> list[str]:
    return ["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url]


def cmd_launch(package: str) -> list[str]:
    return ["shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"]


def cmd_dial(number: str) -> list[str]:
    return ["shell", "am", "start", "-a", "android.intent.action.DIAL", "-d", f"tel:{number}"]


def cmd_compose_sms(number: str, body: str) -> list[str]:
    return [
        "shell",
        "am",
        "start",
        "-a",
        "android.intent.action.SENDTO",
        "-d",
        f"sms:{number}",
        "--es",
        "sms_body",
        body,
    ]


def cmd_notifications() -> list[str]:
    return ["shell", "dumpsys", "notification", "--noredact"]


def cmd_call_state() -> list[str]:
    return ["shell", "dumpsys", "telephony.registry"]


def cmd_contacts() -> list[str]:
    return [
        "shell",
        "content",
        "query",
        "--uri",
        "content://com.android.contacts/data/phones",
        "--projection",
        "data1",
    ]


def cmd_tap(x: int, y: int) -> list[str]:
    return ["shell", "input", "tap", str(x), str(y)]


def cmd_swipe(x1: int, y1: int, x2: int, y2: int, ms: int = 300) -> list[str]:
    return ["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(ms)]


def cmd_text(text: str) -> list[str]:
    return ["shell", "input", "text", text.replace(" ", "%s")]


def cmd_key(keycode: int) -> list[str]:
    return ["shell", "input", "keyevent", str(keycode)]


# --- connection command builders (global; no -s serial) ---
def cmd_connect(address: str) -> list[str]:
    return ["connect", address]


def cmd_pair(address: str, code: str) -> list[str]:
    return ["pair", address, code]


def cmd_tcpip(port: int = 5555) -> list[str]:
    return ["tcpip", str(port)]


# --- execution ---
async def _run(base: list[str], args: list[str], timeout: float) -> tuple[int, str]:
    cmd = base + args
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return (proc.returncode or 0), (out.decode(errors="replace") if out else "")
    except FileNotFoundError:
        return 127, "adb not found — install Android platform-tools and add it to PATH"
    except TimeoutError:
        return 124, "adb command timed out"


async def run_adb(args: list[str], timeout: float = 30.0) -> tuple[int, str]:
    return await _run(_base(), args, timeout)


async def run_adb_global(args: list[str], timeout: float = 30.0) -> tuple[int, str]:
    return await _run(_global_base(), args, timeout)


async def screenshot(path: str) -> tuple[int, str]:
    cmd = [*_base(), "exec-out", "screencap", "-p"]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, err = await proc.communicate()
    except FileNotFoundError:
        return 127, "adb not found"
    if proc.returncode == 0 and out:
        with Path(path).open("wb") as fh:
            fh.write(out)
        return 0, path
    return (proc.returncode or 1), (err.decode(errors="replace") if err else "screenshot failed")


async def connect_wireless(address: str | None = None) -> tuple[int, str]:
    addr = address or settings.wireless_address
    if not addr:
        return 1, "No wireless address set (e.g. 192.168.1.50:5555)."
    return await run_adb_global(cmd_connect(addr))


async def pair_wireless(address: str, code: str) -> tuple[int, str]:
    return await run_adb_global(cmd_pair(address, code))


async def ui_dump() -> tuple[int, str]:
    rc, out = await run_adb(["shell", "uiautomator", "dump", "/sdcard/purple_ui.xml"])
    if rc != 0:
        return rc, out
    return await run_adb(["shell", "cat", "/sdcard/purple_ui.xml"])


async def list_devices() -> list[str]:
    _rc, out = await run_adb_global(cmd_devices())
    return parse_devices(out)


# --- pure parsers (testable) ---
def parse_devices(adb_devices_output: str) -> list[str]:
    devices = []
    for line in adb_devices_output.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices


def normalize_number(number: str) -> str:
    """Strip formatting to bare digits, keep the last 10 so +1 / spaces / dashes match."""
    digits = re.sub(r"\D", "", number or "")
    return digits[-10:] if len(digits) >= 10 else digits


def parse_call_state(dumpsys_output: str) -> tuple[int, str]:
    """(state, incoming_number) from `dumpsys telephony.registry`.

    state: 0 idle, 1 ringing, 2 off-hook. Multi-SIM phones report one per subscription;
    a ringing line on any SIM wins. The number is blank unless a call is ringing.
    """
    states = [int(s) for s in re.findall(r"mCallState=(\d+)", dumpsys_output)]
    if 1 in states:
        state = 1
    elif 2 in states:
        state = 2
    else:
        state = 0
    numbers = [n for n in re.findall(r"mCallIncomingNumber=(\S+)", dumpsys_output) if n]
    return state, (numbers[0] if numbers else "")


def parse_contacts(content_query_output: str) -> list[str]:
    """Normalized phone numbers from `content query ... --projection data1`."""
    seen: set[str] = set()
    out: list[str] = []
    for raw in re.findall(r"data1=(.*)", content_query_output):
        n = normalize_number(raw)
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def parse_notifications(dumpsys_output: str, limit: int = 10) -> list[str]:
    titles = re.findall(r"android\.title=String \((.*?)\)", dumpsys_output)
    texts = re.findall(r"android\.text=String \((.*?)\)", dumpsys_output)
    out: list[str] = []
    for i, title in enumerate(titles):
        text = texts[i] if i < len(texts) else ""
        out.append(f"{title}: {text}".strip(": ").strip())
    return out[:limit]


def parse_ui_hierarchy(xml_text: str, limit: int = 40) -> list[dict]:
    """Compact list of on-screen elements with text/label and a tappable center point,
    so the agent can 'see' the screen and decide where to tap — no per-app function."""
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return []
    items: list[dict] = []
    for node in root.iter("node"):
        label = (node.get("text") or node.get("content-desc") or "").strip()
        clickable = node.get("clickable") == "true"
        if not label and not clickable:
            continue
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.get("bounds") or "")
        if not m:
            continue
        x1, y1, x2, y2 = map(int, m.groups())
        items.append(
            {
                "label": label,
                "id": (node.get("resource-id") or "").split("/")[-1],
                "x": (x1 + x2) // 2,
                "y": (y1 + y2) // 2,
                "clickable": clickable,
            }
        )
        if len(items) >= limit:
            break
    return items
