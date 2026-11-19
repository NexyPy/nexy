"""One line per request, in the style of the Next.js dev server: `GET » /users 200 in 12ms`.

uvicorn's own access log carries no duration, so Nexy measures it here and turns uvicorn's off.
"""

from __future__ import annotations

import asyncio
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
    "/assets/",
)
_SLOW_SECONDS = 1.0

# Chrome DevTools asks for this path on every page it inspects. The dev server never serves it, so
# the answer is a 404 and the line is noise in a log that is meant to stay clean (#82).
DEVTOOLS_PROBE = "/.well-known/appspecific/com.chrome.devtools.json"


def format_duration(seconds: float) -> str:
    """``12ms`` below one second, ``1.2s`` from there."""
    if seconds < 1.0 and round(seconds * 1000) < 1000:
        return f"{round(seconds * 1000)}ms"
    return f"{seconds:.1f}s" if seconds >= 1.0 else "1000ms"


def _is_control(char: str) -> bool:
    code = ord(char)
    return code < 0x20 or 0x7F <= code <= 0x9F


def printable_path(path: str) -> str:
    """*path* with its control characters percent-encoded, as they came in the URL.

    uvicorn hands the path decoded, so `/%1b[2J` or `/%0aGET%20/admin` would write a real escape or
    a real new line into the log: a cleared terminal, or a forged request line.
    """
    # Every control character is unprintable: one check in C for the usual path.
    if path.isprintable():
        return path
    return "".join(f"%{ord(char):02X}" if _is_control(char) else char for char in path)


def _status_colour(status: int) -> str:
    if status >= 500:
        return "red"
    if status >= 400:
        return "yellow"
    if status >= 300:
        return "cyan"
    return "green"


Paint = Callable[[str, str | None], str]

_ANSI = {"red": "\033[31m", "yellow": "\033[33m", "cyan": "\033[36m", "green": "\033[32m"}
_ANSI["dim"] = "\033[2m"
_RESET = "\033[0m"
_ARROW = "\u00bb"


def paint_markup(text: str, colour: str | None) -> str:
    """Rich markup, for a log that goes through ``console.print``."""
    return f"[{colour}]{escape(text)}[/{colour}]" if colour else escape(text)


def paint_ansi(text: str, colour: str | None) -> str:
    """The escape codes Rich would write for *colour*, without parsing any markup."""
    return f"{_ANSI[colour]}{text}{_RESET}" if colour else text


def paint_plain(text: str, colour: str | None) -> str:  # noqa: ARG001 - same shape as a Paint
    """No colour: what Rich writes when the output is not a terminal."""
    return text


def format_request(
    method: str, path: str, status: int, seconds: float, paint: Paint = paint_markup
) -> str:
    """One request line; the verb has the colour of the status."""
    colour = _status_colour(status)
    duration_colour = "yellow" if seconds >= _SLOW_SECONDS else "dim"
    return (
        f"{paint(method, colour)} {paint(_ARROW, 'dim')} {paint(printable_path(path), None)}"
        f" {paint(str(status), colour)} {paint('in', 'dim')}"
        f" {paint(format_duration(seconds), duration_colour)}"
    )


def _console_paint() -> Paint:
    """ANSI when the console shows colours, plain text when it does not, as Rich decides."""
    return paint_ansi if console.color_system else paint_plain


_pending: list[str] = []
# The loop that will write the waiting lines; None when nothing is waiting for a write.
_flushing: dict[str, asyncio.AbstractEventLoop | None] = {"loop": None}


def _flush_pending() -> None:
    """Write the waiting lines in one call, then flush: they show at once, even in a pipe."""
    _flushing["loop"] = None
    stream = console.file
    stream.write("".join(_pending))
    _pending.clear()
    stream.flush()


def _write_line(line: str) -> None:
    """Write *line* by the next turn of the event loop, with the other lines of this turn.

    A busy server answers many requests in one turn; one write for all of them saves a system
    call per request. Outside an event loop, the line is written at once.
    """
    _pending.append(line + "\n")
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        _flush_pending()
        return
    if _flushing["loop"] is not loop:
        _flushing["loop"] = loop
        loop.call_soon(_flush_pending)


_SOCKET = "SOCKET"
_ACTION = "ACTION"
Names = Callable[[str], str | None]


def _no_name(_path: str) -> str | None:
    return None


_ACCEPTED = 101
_REFUSED = 403
_CRASHED = 500


class _Exchange:
    """One request or socket being timed: it remembers the status and reports exactly once."""

    def __init__(self, scope: Any, log: Callable[[str], None], paint: Paint, names: Names) -> None:
        self._scope = scope
        self._log = log
        self._paint = paint
        self._names = names
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
        verb, shown = self._shown()
        self._log(format_request(verb, shown, self.status, elapsed, self._paint))

    def _shown(self) -> tuple[str, str]:
        """An action reads by its function name, not by its hashed URL: `ACTION » ping`."""
        path = self._scope["path"]
        name = self._names(path) if self._scope["type"] == "http" else None
        return (_ACTION, name) if name else (self.verb, path)


class AccessLogMiddleware:
    """Pure ASGI middleware logging each HTTP request and WebSocket when its answer starts."""

    def __init__(
        self,
        app: Any,
        log: Callable[[str], None] | None = None,
        quiet: tuple[str, ...] = (),
        names: Names = _no_name,
    ) -> None:
        self.app = app
        # The action served at a path, so its line names it; no name keeps the path.
        self._names = names
        # A given log receives markup; the default one writes the finished line itself.
        self._log = log or _write_line
        self._paint = paint_markup if log else _console_paint()
        self._quiet = _QUIET_PREFIXES + quiet

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] not in ("http", "websocket") or scope["path"].startswith(self._quiet):
            await self.app(scope, receive, send)
            return

        exchange = _Exchange(scope, self._log, self._paint, self._names)

        async def observed_send(message: Any) -> None:
            exchange.observe(message)
            await send(message)

        try:
            await self.app(scope, receive, observed_send)
        finally:
            exchange.report()
