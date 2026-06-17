"""Vision tools — let Purple see and act on anything on screen.

Complements pc_ui (which reads accessible UI elements): these work on pixels, so they
cover games, canvas/Electron apps, images, video — anything visible. The model returns
click coordinates, which feed straight into the same click layer as the rest of the PC
tools. look_and_click is commit-guarded like every other click path.
"""

from __future__ import annotations

import asyncio
import base64
import re

from purple.safety import confirm, is_commit_label
from purple.tools.registry import registry
from purple.vision.provider import provider


async def _grab_screen() -> bytes:
    def _do() -> bytes:
        import io

        import pyautogui

        buf = io.BytesIO()
        pyautogui.screenshot().save(buf, format="PNG")
        return buf.getvalue()

    return await asyncio.to_thread(_do)


def parse_point(text: str) -> tuple[int, int] | None:
    """Pull an 'x,y' pixel coordinate out of the model's reply, if present."""
    m = re.search(r"(\d{1,5})\s*,\s*(\d{1,5})", text)
    return (int(m.group(1)), int(m.group(2))) if m else None


@registry.tool(
    "see_screen",
    "Look at the screen and answer a question about it — read text, describe the UI, "
    "understand an image, a game, or any app pc_ui can't read as elements.",
    {"type": "object", "properties": {"question": {"type": "string"}}, "required": ["question"]},
)
async def see_screen(question: str) -> str:
    img = await _grab_screen()
    return await provider.look(img, question)


@registry.tool(
    "find_on_screen",
    "Find where something is on screen by description; returns pixel coordinates to click.",
    {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]},
)
async def find_on_screen(target: str) -> dict | str:
    img = await _grab_screen()
    ans = await provider.look(
        img,
        f"Look at this screenshot. Respond ONLY with the pixel coordinates as 'x,y' of: "
        f"{target}. If it is not visible, respond exactly 'none'.",
    )
    pt = parse_point(ans)
    return {"x": pt[0], "y": pt[1]} if pt else f"not found on screen ({ans[:60]})"


@registry.tool(
    "look_and_click",
    "Find something on screen by description and click it. For things pc_click_text can't "
    "reach (games, canvas, images). Commit-like targets (Pay, Buy, Confirm...) are "
    "screenshotted and confirmed first.",
    {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]},
)
async def look_and_click(target: str) -> str:
    img = await _grab_screen()
    ans = await provider.look(
        img,
        f"Respond ONLY with the pixel coordinates as 'x,y' of: {target}. "
        f"If not visible, respond exactly 'none'.",
    )
    pt = parse_point(ans)
    if not pt:
        return f"couldn't find '{target}' on screen"
    if is_commit_label(target):
        shot = base64.b64encode(img).decode()
        if not await confirm(f"Click '{target}' on screen?", screenshot_b64=shot):
            return "cancelled — you didn't confirm this commit"
    from purple.tools.desktop_ui import _click_at

    await _click_at(*pt)
    return f"clicked '{target}' at {pt}"
