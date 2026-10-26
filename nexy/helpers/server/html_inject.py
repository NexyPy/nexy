"""Add markup before the ``</body>`` of an HTML response: the badge and the dev toolbar."""

from __future__ import annotations

from collections.abc import Callable

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

_CLOSING = b"</body>"
# What is held back from a chunk: `</body>` may be split between two of them.
_HOLD = len(_CLOSING) - 1

# The markup of a response, from the request scope and the status it answers with.
Markup = Callable[[Scope, int], bytes]


def inject(data: bytes, markup: bytes) -> tuple[bytes, bool]:
    """*data* with *markup* before its last ``</body>``, and whether there was one."""
    index = data.lower().rfind(_CLOSING)
    if index == -1:
        return data, False
    return data[:index] + markup + data[index:], True


def _is_html(message: Message) -> bool:
    headers = MutableHeaders(scope=message)
    kind = headers.get("content-type", "").lower()
    return kind.startswith("text/html") and "content-encoding" not in headers


class _Response:
    """One response being rewritten: headers first, then the body chunk by chunk."""

    def __init__(self, scope: Scope, markup: Markup, marker: bytes, send: Send) -> None:
        self._scope = scope
        self._markup = markup
        self._marker = marker
        self._send = send
        self._status = 200
        self._active = False
        self._done = False
        self._held = b""

    async def send(self, message: Message) -> None:
        if message["type"] == "http.response.start":
            await self._start(message)
        elif message["type"] == "http.response.body" and self._active and not self._done:
            await self._body(message)
        else:
            await self._send(message)

    async def _start(self, message: Message) -> None:
        self._status = message["status"]
        self._active = _is_html(message)
        if self._active:
            # The length changes when the markup is added.
            del MutableHeaders(scope=message)["content-length"]
        await self._send(message)

    async def _body(self, message: Message) -> None:
        data = self._held + message.get("body", b"")
        more = message.get("more_body", False)
        found = self._marker in data
        if not found:
            data, found = inject(data, self._markup(self._scope, self._status))
        self._done = found
        keep = 0 if (found or not more) else min(_HOLD, len(data))
        self._held = data[len(data) - keep :] if keep else b""
        await self._send({**message, "body": data[: len(data) - keep]})


class InjectMiddleware:
    """Pure ASGI middleware adding markup to HTML responses that have a ``</body>``.

    *marker* is a byte string the markup contains: a page that already has it is left alone.
    """

    def __init__(self, app: ASGIApp, markup: Markup, marker: bytes) -> None:
        self.app = app
        self._markup = markup
        self._marker = marker

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        state = _Response(scope, self._markup, self._marker, send)
        await self.app(scope, receive, state.send)
