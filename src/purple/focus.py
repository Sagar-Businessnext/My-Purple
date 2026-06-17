"""GPU Focus mode — yield the GPU to the user's heavy tasks (gaming, rendering).

When focus is active, Purple's GPU-heavy *background* work (proactive LLM/vision) should
defer rather than fight the user's game for VRAM. Interactive, user-initiated requests
are not gated here — if you ask Purple something while gaming, it still answers.

Focus is active when any of: a runtime toggle is on, settings.focus_mode is on, or
auto_focus is on and the GPU is currently busy.
"""

from __future__ import annotations

from purple import gpu
from purple.config import settings

_manual_override = False  # set at runtime via /focus


def set_focus(on: bool) -> None:
    global _manual_override
    _manual_override = on


def should_yield_gpu() -> bool:
    if _manual_override or settings.focus_mode:
        return True
    return bool(settings.auto_focus and gpu.gpu_busy())


def state() -> dict:
    return {
        "manual": _manual_override or settings.focus_mode,
        "auto_focus": settings.auto_focus,
        "gpu": gpu.status(),
        "yielding": should_yield_gpu(),
    }
