"""Refuse a request body over a size limit, so one request cannot fill a worker's memory."""

from __future__ import annotations

import contextlib

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

DEFAULT_LIMIT = 1024 * 1024


class BodyTooLargeError(Exception):
    """Raised by the counting `receive` when the body goes over the limit."""


def _declared_length(scope: Scope) -> int | None:
    """The Content-Length of the request; None without one; ValueError when it is not a number."""
    for name, value in scope.get("headers", []):
        if name == b"content-length":
            return int(value)
    return None


def _length_unknown(scope: Scope) -> bool:
    """True for a body read without a declared length: chunked, or HTTP/2 and later.

    An HTTP/1 request with neither Content-Length nor Transfer-Encoding has no body (RFC 9112,
    6.3), and the server never reads past a declared Content-Length, so only these need counting.
    """
    if not str(scope.get("http_version", "1.1")).startswith("1"):
        return True
    return any(name == b"transfer-encoding" for name, _value in scope.get("headers", []))


class _Guard:
    """The `receive` and `send` of one request: count the body, hold back what follows overflow."""

    def __init__(self, receive: Receive, send: Send, limit: int) -> None:
        self._receive, self._send, self._limit = receive, send, limit
        self.read = 0
        self.over = False
        self.started = False

    async def receive(self) -> Message:
        message = await self._receive()
        self.read += len(message.get("body", b""))
        if self.read > self._limit:
            self.over = True
            raise BodyTooLargeError
        return message

    async def send(self, message: Message) -> None:
        # The error page the application sends for the exception becomes the 413.
        if self.over:
            return
        self.started = self.started or message["type"] == "http.response.start"
        await self._send(message)


class BodyLimitMiddleware:
    """Pure ASGI middleware: a 413 for a body over `limit` bytes, declared or streamed."""

    def __init__(self, app: ASGIApp, limit: int | None = DEFAULT_LIMIT) -> None:
        self.app = app
        self.limit = limit

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or self.limit is None:
            await self.app(scope, receive, send)
            return
        try:
            declared = _declared_length(scope)
        except ValueError:
            await JSONResponse({"detail": "Bad Content-Length"}, 400)(scope, receive, send)
            return
        if declared is not None and declared > self.limit:
            await self._refuse(scope, receive, send)
        elif declared is None and _length_unknown(scope):
            await self._counted(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    async def _counted(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Run the application with a `receive` that stops once the body is over the limit."""
        guard = _Guard(receive, send, self.limit or 0)
        with contextlib.suppress(BodyTooLargeError):
            await self.app(scope, guard.receive, guard.send)
        if guard.over and not guard.started:
            await self._refuse(scope, receive, send)

    async def _refuse(self, scope: Scope, receive: Receive, send: Send) -> None:
        detail = f"The request body is over {self.limit} bytes"
        await JSONResponse({"detail": detail}, 413)(scope, receive, send)
