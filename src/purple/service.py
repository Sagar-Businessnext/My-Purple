"""Always-on service runtime.

Acquires a single-instance lock (so two Purples never run at once), then runs the
server. Crash recovery is provided by the OS-level Scheduled Task (scripts/install_
service.ps1), which relaunches this on exit; background loops self-restart inside the app.

    purple-service        # or: python -m purple.service
"""

from __future__ import annotations

from collections.abc import Callable
import contextlib
import os
from pathlib import Path

from purple.config import settings
from purple.utils.logging import configure_logging, get_logger

log = get_logger("service")


class SingleInstance:
    """PID-file lock. acquire() returns False if another live instance holds it."""

    def __init__(self, lock_path: Path, pid_alive: Callable[[int], bool] | None = None) -> None:
        self.lock_path = lock_path
        self._pid_alive = pid_alive
        self._held = False

    def _alive(self, pid: int) -> bool:
        if self._pid_alive is not None:
            return self._pid_alive(pid)
        import psutil

        return psutil.pid_exists(pid)

    def acquire(self) -> bool:
        if self.lock_path.exists():
            try:
                pid = int(self.lock_path.read_text().strip())
            except (ValueError, OSError):
                pid = -1
            if pid > 0 and self._alive(pid):
                return False  # another live instance holds the lock
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_path.write_text(str(os.getpid()))
        self._held = True
        return True

    def release(self) -> None:
        if self._held:
            with contextlib.suppress(OSError):
                self.lock_path.unlink()
            self._held = False


def main() -> None:
    configure_logging(settings.log_level)
    settings.ensure_dirs()
    lock = SingleInstance(settings.data_dir / "purple.lock")
    if not lock.acquire():
        log.warning("already_running")
        print("Purple is already running.")
        raise SystemExit(1)
    try:
        import uvicorn

        log.info("service_starting", host=settings.host, port=settings.port)
        uvicorn.run("purple.app:app", host=settings.host, port=settings.port, reload=False)
    finally:
        lock.release()


if __name__ == "__main__":
    main()
