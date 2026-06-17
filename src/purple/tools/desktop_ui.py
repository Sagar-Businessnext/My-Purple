"""Generic Windows UI automation — drive ANY desktop app.

Reads the foreground window's UI Automation tree (names + click points), takes
screenshots, and clicks/types/hotkeys via pyautogui. This is the PC analog of the
phone's phone_ui/phone_tap_text, so Purple can operate apps it has no specific tool for.

Clicking by name is commit-guarded (Pay/Buy/Confirm... -> screenshot + confirm).
Windows libraries (uiautomation, pyautogui) are imported lazily.
"""

from __future__ import annotations

import asyncio

from purple.safety import confirm, is_commit_label
from purple.tools.registry import registry

_EMPTY = {"type": "object", "properties": {}, "required": []}


# --- helpers (monkeypatchable / lazy) ---
async def _find_point(text: str) -> tuple[str, int, int] | None:
    def _do() -> str:
        import uiautomation as auto

        win = auto.GetForegroundControl()
        for ctrl, _depth in auto.WalkControl(win, maxDepth=14):
            name = (ctrl.Name or "").strip()
            if name and text.lower() in name.lower():
                r = ctrl.BoundingRectangle
                if r.right > r.left and r.bottom > r.top:
                    return name, (r.left + r.right) // 2, (r.top + r.bottom) // 2
        return None

    return await asyncio.to_thread(_do)


async def _click_at(x: int, y: int) -> None:
    def _do() -> None:
        import pyautogui

        pyautogui.click(x, y)

    await asyncio.to_thread(_do)


async def _screenshot_b64() -> str | None:
    def _do() -> list[dict]:
        import base64
        import io

        import pyautogui

        buf = io.BytesIO()
        pyautogui.screenshot().save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    try:
        return await asyncio.to_thread(_do)
    except Exception:
        return None


# --- tools ---
@registry.tool("pc_screenshot", "Take a screenshot of the screen; returns the saved path.", _EMPTY)
async def pc_screenshot() -> str:
    def _do() -> str:
        import pyautogui

        from purple.config import settings

        settings.ensure_dirs()
        path = str(settings.data_dir / "pc_screen.png")
        pyautogui.screenshot(path)
        return path

    return f"Saved screenshot to {await asyncio.to_thread(_do)}"


@registry.tool(
    "pc_ui",
    "Read the on-screen UI elements of the foreground window (name, type, click point), "
    "so you can decide what to click next in an app without a dedicated tool.",
    {"type": "object", "properties": {"limit": {"type": "integer"}}, "required": []},
)
async def pc_ui(limit: int = 50) -> list[dict] | str:
    def _do() -> list[dict]:
        import uiautomation as auto

        win = auto.GetForegroundControl()
        out: list[dict] = []
        for ctrl, _depth in auto.WalkControl(win, maxDepth=14):
            name = (ctrl.Name or "").strip()
            if not name:
                continue
            try:
                r = ctrl.BoundingRectangle
                if r.right <= r.left or r.bottom <= r.top:
                    continue
                out.append(
                    {
                        "name": name[:80],
                        "type": ctrl.ControlTypeName,
                        "x": (r.left + r.right) // 2,
                        "y": (r.top + r.bottom) // 2,
                    }
                )
            except Exception:
                continue
            if len(out) >= limit:
                break
        return out

    return await asyncio.to_thread(_do) or "no readable elements"


@registry.tool(
    "pc_click",
    "Click the mouse at screen coordinates (from pc_ui or a screenshot).",
    {
        "type": "object",
        "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}},
        "required": ["x", "y"],
    },
)
async def pc_click(x: int, y: int) -> str:
    await _click_at(x, y)
    return f"clicked ({x}, {y})"


@registry.tool(
    "pc_click_text",
    "Click the on-screen element whose name matches `text`. Commit-like names (Pay, Buy, "
    "Confirm, Place order...) are screenshotted and confirmed before clicking.",
    {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
)
async def pc_click_text(text: str) -> str:
    found = await _find_point(text)
    if not found:
        return f"no on-screen element matching '{text}'"
    name, x, y = found
    if is_commit_label(name) and not await confirm(
        f"Click '{name}' on screen?", screenshot_b64=await _screenshot_b64()
    ):
        return "cancelled — you didn't confirm this commit"
    await _click_at(x, y)
    return f"clicked '{name}'"


@registry.tool(
    "pc_type",
    "Type text via the keyboard into the focused field.",
    {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
)
async def pc_type(text: str) -> str:
    def _do() -> None:
        import pyautogui

        pyautogui.typewrite(text, interval=0.01)

    await asyncio.to_thread(_do)
    return "typed"


@registry.tool(
    "pc_hotkey",
    "Press a key combination, e.g. ['ctrl','c'], ['alt','tab'], ['win','d'].",
    {
        "type": "object",
        "properties": {"keys": {"type": "array", "items": {"type": "string"}}},
        "required": ["keys"],
    },
)
async def pc_hotkey(keys: list[str]) -> str:
    def _do() -> None:
        import pyautogui

        pyautogui.hotkey(*keys)

    await asyncio.to_thread(_do)
    return "+".join(keys)


@registry.tool(
    "pc_scroll",
    "Scroll the mouse wheel. Positive scrolls up, negative scrolls down.",
    {"type": "object", "properties": {"amount": {"type": "integer"}}, "required": ["amount"]},
)
async def pc_scroll(amount: int) -> str:
    def _do() -> None:
        import pyautogui

        pyautogui.scroll(amount)

    await asyncio.to_thread(_do)
    return "scrolled"
