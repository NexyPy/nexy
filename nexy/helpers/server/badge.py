"""The "Built with Nexy" tag: a small link in the corner of every HTML page, off with `useBadge`."""

from __future__ import annotations

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

_CLOSING = b"</body>"
_ID = b'id="nexy-badge"'
# What is held back from a chunk: `</body>` may be split between two of them.
_HOLD = len(_CLOSING) - 1


def badge_markup(version: str) -> bytes:
    """The tag as HTML: its own style, light and dark, no script, no external request."""
    style = (
        "#nexy-badge{position:fixed;right:16px;bottom:16px;z-index:2147483000;display:inline-flex;"
        "align-items:center;gap:8px;padding:10px 16px;border:1px solid #d4d4d4;border-radius:999px;"
        "background:#fff;color:#171717;font:600 14px/1.2 system-ui,sans-serif;text-decoration:none;"
        "box-shadow:0 2px 8px rgba(0,0,0,.1)}"
        "#nexy-badge:hover{border-color:#a3a3a3}"
        "@media(prefers-color-scheme:dark){#nexy-badge{background:#0a0a0a;color:#ededed;"
        "border-color:#303030}#nexy-badge:hover{border-color:#525252}}"
    )
    return (
        f"<style>{style}</style>"
        f'<a id="nexy-badge" href="https://github.com/NexyPy/nexy" target="_blank" '
        f'rel="noopener noreferrer">Built with Nexy {version}</a>'
    ).encode()


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


class BadgeMiddleware:
    """Pure ASGI middleware adding the tag to HTML responses that have a ``</body>``."""

    def __init__(self, app: ASGIApp, version: str) -> None:
        self.app = app
        self._markup = badge_markup(version)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        state = _Response(self._markup, send)
        await self.app(scope, receive, state.send)


class _Response:
    """One response being rewritten: headers first, then the body chunk by chunk."""

    def __init__(self, markup: bytes, send: Send) -> None:
        self._markup = markup
        self._send = send
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
        self._active = _is_html(message)
        if self._active:
            # The length changes when the tag is added.
            del MutableHeaders(scope=message)["content-length"]
        await self._send(message)

    async def _body(self, message: Message) -> None:
        data = self._held + message.get("body", b"")
        more = message.get("more_body", False)
        data, found = inject(data, self._markup) if _ID not in data else (data, True)
        self._done = found
        keep = 0 if (found or not more) else min(_HOLD, len(data))
        self._held = data[len(data) - keep :] if keep else b""
        await self._send({**message, "body": data[: len(data) - keep]})
