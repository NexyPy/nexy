"""The log of the uvicorn server: quiet about startup, one labelled line per message."""

from __future__ import annotations

import logging
from typing import Any

_DIM, _RED, _RESET = "\033[2m", "\033[31m", "\033[0m"

IGNORED_MESSAGES = [
    "Started server process",
    "Started parent process",
    "Waiting for application startup",
    "Application startup complete",
    "Uvicorn running on",
    "Finished server process",
    "Stopping reloader process",
    "Will watch for changes",
    "Shutting down",
    # The crash handler already reported it, with the exception and where it came from.
    "Exception in ASGI application",
    "connection closed",
    "connection open",
    "Waiting for application shutdown",
    "Application shutdown complete",
    "/_nexy/hmr",
    # The browser's HMR sockets (Vite's and Nexy's) open and close all day: not worth a line.
    "WebSocket /",
    # A stale browser tab keeps reconnecting its Vite socket: it says nothing about the app.
    "connection rejected",
]

# Shutdown (Ctrl+C, a deploy, a dev restart) must not wait for a browser that keeps a socket open.
# The Server header names the software to anyone who asks: not worth sending.
SERVE_LIMITS: dict[str, Any] = {"server_header": False, "timeout_graceful_shutdown": 10}
DEV_SERVE_LIMITS: dict[str, Any] = {"server_header": False, "timeout_graceful_shutdown": 2}


class NexyFilter(logging.Filter):
    """Drops the startup and shutdown messages that say nothing the banner does not."""

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return not any(ignored in message for ignored in IGNORED_MESSAGES)


class NexyDefaultFormatter(logging.Formatter):
    """``Level » message``, red for errors, with the traceback when the record has one."""

    def format(self, record: logging.LogRecord) -> str:
        colour = _RED if record.levelno >= logging.ERROR else _DIM
        text = f"{colour}{record.levelname.capitalize()}{_RESET} » {record.getMessage()}"
        if record.exc_info:
            text += "\n" + self.formatException(record.exc_info)
        return text


def _logger(handler: str) -> dict[str, Any]:
    return {"handlers": [handler], "level": "INFO", "propagate": False}


NEXY_LOG_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"nexy_filter": {"()": NexyFilter}},
    "formatters": {"default": {"()": NexyDefaultFormatter}},
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["nexy_filter"],
        },
    },
    "loggers": {
        "uvicorn": _logger("default"),
        "uvicorn.error": _logger("default"),
        "uvicorn.access": _logger("default"),
    },
}
