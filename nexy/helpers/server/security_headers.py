"""Headers every production response should carry, unless the application set its own."""

from __future__ import annotations

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

DEFAULT_HEADERS = {
    # A file is read as the type it was sent with: an upload cannot turn into a script.
    "x-content-type-options": "nosniff",
    # Other sites see where the visitor came from only as an origin, and never on a downgrade.
    "referrer-policy": "strict-origin-when-cross-origin",
}


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
                headers = MutableHeaders(scope=message)
                for name, value in DEFAULT_HEADERS.items():
                    headers.setdefault(name, value)
            await send(message)

        await self.app(scope, receive, with_headers)
