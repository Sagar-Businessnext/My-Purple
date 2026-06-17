"""Structured logging setup. Call configure_logging() once at startup.

structlog is routed through the stdlib logging root, so the same records reach both the
console and a rotating file (logs/purple.log) — persistent logs that survive restarts.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog


def configure_logging(level: str = "INFO") -> None:
    from purple.config import settings

    lvl = getattr(logging, level.upper(), logging.INFO)
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if settings.log_to_file:
        log_dir = Path(settings.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                log_dir / "purple.log",
                maxBytes=settings.log_max_bytes,
                backupCount=settings.log_backups,
                encoding="utf-8",
            )
        )
    logging.basicConfig(format="%(message)s", level=lvl, handlers=handlers, force=True)
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.dev.ConsoleRenderer(colors=False),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(lvl),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    return structlog.get_logger(name)
