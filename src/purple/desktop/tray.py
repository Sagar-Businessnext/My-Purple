"""System-tray icon (pystray) so Purple lives quietly in the tray while the backend runs.

Menu: Open Purple, Quit. pystray/Pillow are imported lazily. The icon runs in its own
daemon thread.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from purple.utils.logging import get_logger

log = get_logger("desktop.tray")


class Tray:
    def __init__(
        self,
        on_open: Callable[[], None] | None = None,
        on_quit: Callable[[], None] | None = None,
    ) -> None:
        self.on_open = on_open
        self.on_quit = on_quit
        self._icon: Any | None = None

    def _build_menu(self) -> Any:
        import pystray

        return pystray.Menu(
            pystray.MenuItem("Open Purple", lambda *_: self.on_open and self.on_open()),
            pystray.MenuItem("Quit", lambda *_: self._quit()),
        )

    def start(self) -> None:
        import threading

        from PIL import Image
        import pystray

        image = Image.new("RGB", (64, 64), (127, 119, 221))  # Purple
        self._icon = pystray.Icon("purple", image, "Purple", self._build_menu())
        threading.Thread(target=self._icon.run, name="tray", daemon=True).start()
        log.info("tray_started")

    def _quit(self) -> None:
        self.stop()
        if self.on_quit:
            self.on_quit()

    def stop(self) -> None:
        if self._icon is not None:
            self._icon.stop()
            self._icon = None
