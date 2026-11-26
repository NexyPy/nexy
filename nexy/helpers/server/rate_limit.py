"""Answer 429 to a client that calls too often (`useRateLimit`, #465).

Requests are counted per client address in a fixed window of `per` seconds. The window is shared by
all clients and the counts are cleared at each rollover, so memory only holds the clients of the
current window and no cleanup task is needed. A client over `requests` in one window gets a 429
with `Retry-After`, and the request never reaches the application.

The counts live in the memory of one process: each worker keeps its own, so with several workers
the real limit is `requests` times the number of workers.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


def _is_number(value: object) -> bool:
    """True for an int or a float; a bool is an int to Python, not a count to a person."""
    return isinstance(value, int | float) and not isinstance(value, bool)


def _validate(requests: int, per: float, paths: list[str] | None) -> None:
    """Raise ValueError, naming `useRateLimit`, when a setting cannot work."""
    if not (_is_number(requests) and isinstance(requests, int) and requests >= 1):
        raise ValueError(
            f"useRateLimit: 'requests' must be an integer of at least 1, got {requests!r}"
        )
    if not (_is_number(per) and math.isfinite(per) and per > 0):
        raise ValueError(f"useRateLimit: 'per' must be a number of seconds above 0, got {per!r}")
    if paths is not None and not _is_prefix_list(paths):
        raise ValueError(f"useRateLimit: 'paths' must be a list of path prefixes, got {paths!r}")


def _is_prefix_list(paths: object) -> bool:
    """True for a non-empty list or tuple of strings."""
    if not isinstance(paths, list | tuple) or not paths:
        return False
    return all(isinstance(path, str) for path in paths)


class RateLimitMiddleware:
    """Pure ASGI middleware: a 429 once a client sends more than `requests` per `per` seconds."""

    def __init__(
        self,
        app: ASGIApp,
        requests: int,
        per: float,
        paths: list[str] | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Wrap *app*.

        Args:
            app: The application behind the limit.
            requests: How many requests one client may send in one window (at least 1).
            per: The length of the window, in seconds (above 0).
            paths: Path prefixes to limit. None limits every path.
            clock: A function returning seconds, injected so a test controls time.

        Raises:
            ValueError: When `requests` or `per` is not usable.
        """
        _validate(requests, per, paths)
        self.app = app
        self.requests = requests
        self.per = per
        self.paths = None if paths is None else tuple(paths)
        self._clock = clock
        self._window = -1
        self._counts: dict[str, int] = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not self._is_counted(scope):
            await self.app(scope, receive, send)
            return
        now = self._clock()
        window = int(now // self.per)
        if self._count(scope, window) > self.requests:
            await self._refuse(window, now)(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    def _is_counted(self, scope: Scope) -> bool:
        """True for an HTTP request on a limited path."""
        if scope["type"] != "http":
            return False
        return self.paths is None or scope["path"].startswith(self.paths)

    def _count(self, scope: Scope, window: int) -> int:
        """Add one request of this client to the window and return its count."""
        if window != self._window:
            self._counts.clear()
            self._window = window
        client = scope.get("client")
        key = client[0] if client else ""
        self._counts[key] = self._counts.get(key, 0) + 1
        return self._counts[key]

    def _refuse(self, window: int, now: float) -> JSONResponse:
        seconds = max(1, math.ceil((window + 1) * self.per - now))
        headers = {"retry-after": str(seconds), "cache-control": "no-store"}
        return JSONResponse({"detail": "Too many requests"}, 429, headers=headers)
