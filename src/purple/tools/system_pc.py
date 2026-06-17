"""PC system control (Windows): windows, media/volume, clipboard, power.

OS-specific libraries (pygetwindow, pyautogui, pyperclip) are imported lazily inside
handlers so this module loads anywhere. Power-off actions are confirmation-gated.
"""

from __future__ import annotations

import asyncio

from purple.tools.registry import registry

_EMPTY = {"type": "object", "properties": {}, "required": []}


# --- windows ---
@registry.tool("list_windows", "List the titles of currently open windows.", _EMPTY)
async def list_windows() -> list[str] | str:
    def _do() -> list[str]:
        import pygetwindow as gw

        return [t for t in gw.getAllTitles() if t.strip()][:60]

    return await asyncio.to_thread(_do)


@registry.tool(
    "focus_window",
    "Bring a window to the front by (partial) title.",
    {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]},
)
async def focus_window(title: str) -> str:
    def _do() -> str:
        import pygetwindow as gw

        wins = gw.getWindowsWithTitle(title)
        if not wins:
            return f"no window matching '{title}'"
        wins[0].activate()
        return f"focused '{wins[0].title}'"

    return await asyncio.to_thread(_do)


@registry.tool(
    "close_window",
    "Close a window by (partial) title.",
    {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]},
)
async def close_window(title: str) -> str:
    def _do() -> str:
        import pygetwindow as gw

        wins = gw.getWindowsWithTitle(title)
        if not wins:
            return f"no window matching '{title}'"
        t = wins[0].title
        wins[0].close()
        return f"closed '{t}'"

    return await asyncio.to_thread(_do)


# --- media / volume ---
_MEDIA = {
    "volume_up": "volumeup",
    "volume_down": "volumedown",
    "mute": "volumemute",
    "play_pause": "playpause",
    "next": "nexttrack",
    "previous": "prevtrack",
}


@registry.tool(
    "media_control",
    "Control audio/media playback and volume.",
    {
        "type": "object",
        "properties": {"action": {"type": "string", "enum": list(_MEDIA.keys())}},
        "required": ["action"],
    },
)
async def media_control(action: str) -> str:
    key = _MEDIA.get(action)
    if not key:
        return f"unknown action '{action}' (use one of: {', '.join(_MEDIA)})"

    def _do() -> str:
        import pyautogui

        pyautogui.press(key)
        return f"{action} done"

    return await asyncio.to_thread(_do)


# --- clipboard ---
@registry.tool("clipboard_get", "Read the current clipboard text.", _EMPTY)
async def clipboard_get() -> str:
    def _do() -> str:
        import pyperclip

        return pyperclip.paste()

    return await asyncio.to_thread(_do)


@registry.tool(
    "clipboard_set",
    "Set the clipboard text.",
    {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
)
async def clipboard_set(text: str) -> str:
    def _do() -> str:
        import pyperclip

        pyperclip.copy(text)
        return "clipboard set"

    return await asyncio.to_thread(_do)


# --- power ---
async def _power(cmd: str) -> str:
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.wait()
    return f"ok (rc={proc.returncode})"


@registry.tool("lock_screen", "Lock the PC.", _EMPTY)
async def lock_screen() -> str:
    return await _power("rundll32.exe user32.dll,LockWorkStation")


@registry.tool("sleep_pc", "Put the PC to sleep.", _EMPTY)
async def sleep_pc() -> str:
    return await _power("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")


@registry.tool("shutdown_pc", "Shut down the PC.", _EMPTY, requires_confirmation=True)
async def shutdown_pc() -> str:
    return await _power("shutdown /s /t 0")


@registry.tool("restart_pc", "Restart the PC.", _EMPTY, requires_confirmation=True)
async def restart_pc() -> str:
    return await _power("shutdown /r /t 0")
