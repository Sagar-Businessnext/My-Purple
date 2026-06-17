"""Global push-to-talk hotkey (system-wide) via pynput.

Pressing the hotkey anywhere fires `on_trigger` — wired to the voice loop's one-shot
capture. pynput is imported lazily so this module loads on any platform.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from purple.utils.logging import get_logger

log = get_logger("desktop.hotkey")


class PushToTalk:
    def __init__(self, hotkey: str, on_trigger: Callable[[], None]) -> None:
        # hotkey uses pynput syntax, e.g. "<ctrl>+<alt>+space"
        self.hotkey = hotkey
        self.on_trigger = on_trigger
        self._listener: Any | None = None

    def start(self) -> None:
        from pynput import keyboard

        self._listener = keyboard.GlobalHotKeys({self.hotkey: self._fire})
        self._listener.start()
        log.info("ptt_listening", hotkey=self.hotkey)

    def _fire(self) -> None:
        try:
            self.on_trigger()
        except Exception as exc:
            log.warning("ptt_trigger_failed", error=str(exc))

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
