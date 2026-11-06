"""HEAD answers wherever GET does: same status and headers, no body (RFC 9110, section 9.3.2).

FastAPI registers only the methods a handler names, so a ``GET`` route refuses ``HEAD`` with 405.
This middleware asks the application first, which keeps a route's own ``HEAD`` handler; only a
405 is asked again as ``GET``, and that answer goes out without its body.
"""

from __future__ import annotations

from starlette.types import ASGIApp, Message, Receive, Scope, Send

_NOT_ALLOWED = 405


class _Refusal:
    """The *send* of the first attempt: forwards the answer unless it is a 405."""

    def __init__(self, send: Send) -> None:
        self.send = send
        self.refused = False

    async def __call__(self, message: Message) -> None:
        if message["type"] == "http.response.start":
            self.refused = message["status"] == _NOT_ALLOWED
        if not self.refused:
            await self.send(message)


def _replay(receive: Receive) -> Receive:
    """The request has no body: the second attempt reads an empty one, then the real channel."""
    sent = False

    async def again() -> Message:
        nonlocal sent
        if sent:
            return await receive()
        sent = True
        return {"type": "http.request", "body": b"", "more_body": False}

    return again


def _bodiless(send: Send) -> Send:
    async def without_body(message: Message) -> None:
        if message["type"] == "http.response.body":
            message = {**message, "body": b""}
        await send(message)

    return without_body


class HeadRequestsMiddleware:
    """Pure ASGI middleware answering ``HEAD`` on every route that answers ``GET``."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["method"] != "HEAD":
            await self.app(scope, receive, send)
            return
        first = _Refusal(send)
        await self.app(scope, receive, first)
        if first.refused:
            await self.app({**scope, "method": "GET"}, _replay(receive), _bodiless(send))
