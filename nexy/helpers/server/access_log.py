"""One line per request, in the style of the Next.js dev server: `GET » /users 200 in 12ms`.

uvicorn's own access log carries no duration, so Nexy measures it here and turns uvicorn's off.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from rich.markup import escape

from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tag

# Framework and Vite URLs are not the application's requests: logging them buries the real ones.
_QUIET_PREFIXES = (
    "/_nexy/",
    "/__nexy__/",
    "/@vite/",
    "/@id/",
    "/@fs/",
    "/@react-refresh",
    "/node_modules/",
    "/assets/",
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
    """Rich markup for one request line; the verb has the colour of the status."""
    colour = _status_colour(status)
    duration_colour = "yellow" if seconds >= _SLOW_SECONDS else "dim"
    return (
        f"{tag(escape(method), colour)} {escape(path)} [{colour}]{status}[/{colour}]"
        f" [dim]in[/dim] [{duration_colour}]{format_duration(seconds)}[/{duration_colour}]"
    )


_SOCKET = "SOCKET"
_ACCEPTED = 101
_REFUSED = 403
_CRASHED = 500


class _Exchange:
    """One request or socket being timed: it remembers the status and reports exactly once."""

    def __init__(self, scope: Any, log: Callable[[str], None]) -> None:
        self._scope = scope
        self._log = log
        self._started = time.perf_counter()
        self._reported = False
        self.status = _CRASHED

    @property
    def verb(self) -> str:
        return _SOCKET if self._scope["type"] == "websocket" else self._scope["method"]

    def observe(self, message: Any) -> None:
        """Take the status from the first message that announces it."""
        kind = message["type"]
        if kind == "http.response.start":
            self.status = message["status"]
        elif kind == "websocket.accept":
            self.status = _ACCEPTED
        elif kind == "websocket.close" and self.status == _CRASHED:
            self.status = _REFUSED
        else:
            return
        self.report()

    def report(self) -> None:
        if self._reported:
            return
        self._reported = True
        elapsed = time.perf_counter() - self._started
        self._log(format_request(self.verb, self._scope["path"], self.status, elapsed))


class AccessLogMiddleware:
    """Pure ASGI middleware logging each HTTP request and WebSocket when its answer starts."""

    def __init__(self, app: Any, log: Callable[[str], None] = console.print) -> None:
        self.app = app
        self._log = log

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] not in ("http", "websocket") or scope["path"].startswith(_QUIET_PREFIXES):
            await self.app(scope, receive, send)
            return

        exchange = _Exchange(scope, self._log)

        async def observed_send(message: Any) -> None:
            exchange.observe(message)
            await send(message)

        try:
            await self.app(scope, receive, observed_send)
        finally:
            exchange.report()
