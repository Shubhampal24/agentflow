"""
AgentFlow — Structured JSON Logging
Provides a configured logger with request_id context support.
"""
from __future__ import annotations

import logging
import sys
from typing import Optional

from pythonjsonlogger import jsonlogger

from app.core.config import settings


def setup_logging() -> None:
    """Configure root logger with JSON formatting."""
    log_level = logging.DEBUG if not settings.is_production else logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)


class RequestLogger:
    """Context-aware logger that auto-includes request_id in every log record."""

    def __init__(self, name: str, request_id: Optional[str] = None):
        self._logger = logging.getLogger(name)
        self._request_id = request_id

    def _extra(self, extra: Optional[dict] = None) -> dict:
        base = {"request_id": self._request_id} if self._request_id else {}
        if extra:
            base.update(extra)
        return base

    def info(self, msg: str, **kwargs: object) -> None:
        self._logger.info(msg, extra=self._extra(kwargs or None))

    def warning(self, msg: str, **kwargs: object) -> None:
        self._logger.warning(msg, extra=self._extra(kwargs or None))

    def error(self, msg: str, **kwargs: object) -> None:
        self._logger.error(msg, extra=self._extra(kwargs or None))

    def debug(self, msg: str, **kwargs: object) -> None:
        self._logger.debug(msg, extra=self._extra(kwargs or None))

    def exception(self, msg: str, **kwargs: object) -> None:
        self._logger.exception(msg, extra=self._extra(kwargs or None))
