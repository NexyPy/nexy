"""Headers every production response should carry, unless the application set its own."""

from __future__ import annotations

from collections.abc import Iterable

from starlette.types import ASGIApp, Message, Receive, Scope, Send

DEFAULT_HEADERS = {
    # A file is read as the type it was sent with: an upload cannot turn into a script.
    "x-content-type-options": "nosniff",
    # Other sites see where the visitor came from only as an origin, and never on a downgrade.
    "referrer-policy": "strict-origin-when-cross-origin",
}


_RAW_DEFAULTS = [
    (name.encode("latin-1"), value.encode("latin-1")) for name, value in DEFAULT_HEADERS.items()
]


def with_defaults(headers: Iterable[tuple[bytes, bytes]]) -> list[tuple[bytes, bytes]]:
    """*headers*, then each default header whose name they do not already carry, in any case."""
    own = list(headers)
    present = {name.lower() for name, _value in own}
    return own + [header for header in _RAW_DEFAULTS if header[0] not in present]


class SecurityHeadersMiddleware:
    """Pure ASGI middleware adding `DEFAULT_HEADERS` to every HTTP response."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                message = {**message, "headers": with_defaults(message.get("headers", ()))}
            await send(message)

        await self.app(scope, receive, with_headers)
