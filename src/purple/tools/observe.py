"""Observe tool — let the user toggle screen-context observation by voice or chat.

This is a capability toggle (not a per-task tool): "start observing" / "keep an eye on my
screen" turns it on; "stop observing" turns it off. Off by default; auto-disables after a
safety window (see purple.observe). No screenshots — only the active window title.
"""

from __future__ import annotations

from purple import observe
from purple.tools.registry import registry


@registry.tool(
    name="set_observing",
    description=(
        "Turn screen-context observation on or off. When ON, you can see the title of the "
        "window the user is currently looking at, to ground vague requests. Turn ON when the "
        "user says things like 'start observing', 'watch my screen', 'keep an eye on what I'm "
        "doing'; turn OFF for 'stop observing', 'stop watching'. It is private and off by "
        "default. After toggling, briefly confirm the new state to the user."
    ),
    parameters={
        "type": "object",
        "properties": {
            "on": {"type": "boolean", "description": "true to start observing, false to stop"}
        },
        "required": ["on"],
    },
)
async def set_observing(on: bool) -> dict:
    state = observe.set_observing(on)
    return {
        "observing": state,
        "message": (
            "Okay — I'm now watching your screen context (just the active window). "
            "Say 'stop observing' anytime."
            if state
            else "Done — I've stopped observing your screen."
        ),
    }


@registry.tool(
    name="observation_status",
    description="Check whether screen-context observation is currently on, and since when.",
    parameters={"type": "object", "properties": {}},
)
async def observation_status() -> dict:
    return observe.status()
