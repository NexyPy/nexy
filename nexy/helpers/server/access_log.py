"""One line per request, in the style of the Next.js dev server: `GET /users 200 in 12ms`.

uvicorn's own access log carries no duration, so Nexy measures it here and turns uvicorn's off.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from rich.markup import escape

from nexy.helpers.common.console import console

# Framework and Vite URLs are not the application's requests: logging them buries the real ones.
_QUIET_PREFIXES = (
    "/_nexy/",
    "/__nexy__/",
    "/@vite/",
    "/@id/",
    "/@fs/",
    "/@react-refresh",
    "/node_modules/",
)
_SLOW_SECONDS = 1.0


def format_duration(seconds: float) -> str:
    """``12ms`` below one second, ``1.2s`` from there."""
    if seconds < 1.0 and round(seconds * 1000) < 1000:
        return f"{round(seconds * 1000)}ms"
    return f"{seconds:.1f}s" if seconds >= 1.0 else "1000ms"


def _status_colour(status: int) -> str:
    if status >= 500:
        return "red"
    if status >= 400:
        return "yellow"
    if status >= 300:
        return "cyan"
    return "green"


def format_request(method: str, path: str, status: int, seconds: float) -> str:
    """Rich markup for one request line."""
    colour = _status_colour(status)
    duration_colour = "yellow" if seconds >= _SLOW_SECONDS else "dim"
    return (
        f" [bold]{escape(method)}[/bold] {escape(path)} [{colour}]{status}[/{colour}]"
        f" [dim]in[/dim] [{duration_colour}]{format_duration(seconds)}[/{duration_colour}]"
    )


class AccessLogMiddleware:
    """Pure ASGI middleware logging each HTTP request when its response starts."""

    def __init__(self, app: Any, log: Callable[[str], None] = console.print) -> None:
        self.app = app
        self._log = log

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http" or scope["path"].startswith(_QUIET_PREFIXES):
            await self.app(scope, receive, send)
            return

        started = time.perf_counter()
        status = 500
        logged = False

        def emit() -> None:
            nonlocal logged
            if not logged:
                logged = True
                elapsed = time.perf_counter() - started
                self._log(format_request(scope["method"], scope["path"], status, elapsed))

        async def traced_send(message: Any) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                emit()
            await send(message)

        try:
            await self.app(scope, receive, traced_send)
        finally:
            emit()
