"""Reverse-proxy Vite's dev-server endpoints through the Nexy origin.

In development Vite listens on an internal loopback port. Exposing that port to
the browser would leak an implementation detail, break any client that is not
on ``localhost``, and double the exposed attack surface. This middleware hides
it: Vite's own traffic is forwarded internally, so the whole application is
served from a single origin.

Vite only answers for its module graph. For a project source file it returns
200; for a Nexy route it returns 404. That asymmetry is what lets the proxy
serve arbitrary project layouts without guessing path prefixes: anything Vite
does not know about falls through to the application untouched.
"""

import asyncio
import contextlib
import os
from pathlib import Path

import httpx
from starlette.types import ASGIApp, Receive, Scope, Send
from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed, WebSocketException
from websockets.typing import Subprotocol

from nexy.core.config import Config
from nexy.helpers.server.ports import get_client_port

# Paths that only Vite can serve: its client runtime, id- and fs-resolved
# modules, the generated Nexy entry, and pre-bundled dependencies. A request
# for one of these never belongs to the application, so a failure is reported
# instead of being retried against the app.
VITE_ONLY_PREFIXES = ("/@vite/", "/@id/", "/@fs/", "/__nexy__/", "/node_modules/")

# Vite's HMR client asks for this subprotocol; Nexy's own HMR socket does not.
HMR_SUBPROTOCOL: Subprotocol = Subprotocol("vite-hmr")

# Methods Vite serves. Anything else is a genuine application request.
SAFE_METHODS = frozenset({"GET", "HEAD"})


# Set by `nexy dev` for the application process it serves. Nothing else sets
# it, so user test suites and `nexy start` never route through the proxy.
DEV_ENV_VAR = "NEXY_DEV_SERVER"


def vite_proxy_port() -> int | None:
    """Return the loopback Vite port to proxy, or None when not in dev mode.

    Dev mode is opt-in through the environment so that importing the app in a
    user's test suite or under ``nexy start`` never touches a Vite port.
    """
    if os.environ.get(DEV_ENV_VAR) != "1":
        return None
    if not os.path.exists("vite.config.ts"):
        return None
    if Path("__nexy__/nexy.prod").is_file():
        return None
    if not Config().useVite:
        return None
    return get_client_port()


class ViteProxyMiddleware:
    """Forward Vite dev-server traffic that arrives on the Nexy origin."""

    def __init__(self, app: ASGIApp, port: int, host: str = "127.0.0.1") -> None:
        self.app = app
        self.port = port
        self.host = host

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "websocket":
            await self._handle_websocket(scope, receive, send)
        elif scope["type"] == "http":
            await self._handle_http(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    async def _handle_websocket(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Proxy Vite's HMR socket; every other socket belongs to the app."""
        if HMR_SUBPROTOCOL not in scope.get("subprotocols", ()):
            await self.app(scope, receive, send)
            return
        try:
            await self._forward_websocket(scope, receive, send)
        except (OSError, WebSocketException):
            await _close_websocket(send)

    async def _handle_http(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Proxy Vite's assets; fall through to the app for everything else."""
        if scope["method"] not in SAFE_METHODS:
            await self.app(scope, receive, send)
            return

        vite_only = _is_vite_only(scope["path"])
        try:
            await self._forward_http(scope, receive, send, fallthrough=not vite_only)
        except (httpx.HTTPError, OSError):
            if vite_only:
                await _send_unavailable(send)
            else:
                await self.app(scope, receive, send)

    def _upstream_url(self, scope: Scope) -> str:
        query = scope.get("query_string", b"").decode("latin-1")
        url = f"http://{self.host}:{self.port}{scope['path']}"
        return f"{url}?{query}" if query else url

    async def _forward_http(
        self, scope: Scope, receive: Receive, send: Send, *, fallthrough: bool
    ) -> None:
        """Relay one HTTP response, or hand an unknown path to the application."""
        async with httpx.AsyncClient() as client:
            request = client.build_request(scope["method"], self._upstream_url(scope))
            response = await client.send(request, stream=True)
            try:
                if fallthrough and response.status_code == httpx.codes.NOT_FOUND:
                    await self.app(scope, receive, send)
                    return
                await _relay_response(response, send)
            finally:
                await response.aclose()

    async def _forward_websocket(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Relay a WebSocket connection to Vite's HMR endpoint."""
        uri = f"ws://{self.host}:{self.port}{scope['path']}"
        async with connect(uri, subprotocols=[HMR_SUBPROTOCOL], open_timeout=10) as upstream:
            await send({"type": "websocket.accept", "subprotocol": upstream.subprotocol})
            await asyncio.gather(
                _pump_client_to_upstream(upstream, receive),
                _pump_upstream_to_client(upstream, send),
            )


def _is_vite_only(path: str) -> bool:
    """True when the path can only be served by Vite."""
    return any(path.startswith(prefix) for prefix in VITE_ONLY_PREFIXES)


async def _relay_response(response: httpx.Response, send: Send) -> None:
    """Stream an upstream response back to the client."""
    await send(
        {
            "type": "http.response.start",
            "status": response.status_code,
            "headers": _response_headers(response),
        }
    )
    async for chunk in response.aiter_bytes():
        await send({"type": "http.response.body", "body": chunk, "more_body": True})
    await send({"type": "http.response.body", "body": b"", "more_body": False})


def _response_headers(response: httpx.Response) -> list[tuple[bytes, bytes]]:
    """Drop headers the ASGI server recomputes; httpx already decoded the body."""
    skip = {"content-length", "content-encoding", "transfer-encoding", "connection"}
    return [
        (name.lower().encode("latin-1"), value.encode("latin-1"))
        for name, value in response.headers.multi_items()
        if name.lower() not in skip
    ]


async def _send_unavailable(send: Send) -> None:
    """Report that Vite is not reachable, without killing the server."""
    await send(
        {
            "type": "http.response.start",
            "status": httpx.codes.BAD_GATEWAY,
            "headers": [(b"content-type", b"text/plain; charset=utf-8")],
        }
    )
    await send({"type": "http.response.body", "body": b"Vite dev server is not reachable"})


async def _close_websocket(send: Send) -> None:
    """Report that Vite's HMR socket could not be reached."""
    await send({"type": "websocket.close", "code": 1011})


async def _pump_client_to_upstream(upstream: ClientConnection, receive: Receive) -> None:
    """Forward browser frames to Vite until the client disconnects."""
    while True:
        message = await receive()
        if message["type"] == "websocket.disconnect":
            await upstream.close()
            return
        if message.get("text") is not None:
            await upstream.send(message["text"])
        elif message.get("bytes") is not None:
            await upstream.send(message["bytes"])


async def _pump_upstream_to_client(upstream: ClientConnection, send: Send) -> None:
    """Forward Vite frames to the browser until Vite closes the socket."""
    with contextlib.suppress(ConnectionClosed):
        async for message in upstream:
            if isinstance(message, str):
                await send({"type": "websocket.send", "text": message})
            else:
                await send({"type": "websocket.send", "bytes": message})
