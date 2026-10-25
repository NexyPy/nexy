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
import ipaddress
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
        self._client: httpx.AsyncClient | None = None

    def _upstream_client(self) -> httpx.AsyncClient:
        """Reuse one pooled client for the whole dev session.

        A per-request ``AsyncClient`` tears down and re-opens a loopback TCP
        connection for every module request a dev page load makes (dozens per
        refresh), which dominates local TTFB. ``trust_env=False`` also keeps
        any ``HTTP_PROXY`` defined on the host from intercepting 127.0.0.1
        traffic - that turns a local roundtrip into a proxy detour.
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                trust_env=False,
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            )
        return self._client

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
        if not _host_allowed(scope):
            await send({"type": "websocket.close", "code": 1008})
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
        if vite_only and not _host_allowed(scope):
            await _send_forbidden(send)
            return
        if not vite_only and _is_app_document(scope):
            # An HTML navigation to an extension-less path: only the app can
            # answer it, so skip the upstream probe (one loopback roundtrip
            # per page refresh for free).
            await self.app(scope, receive, send)
            return
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
        client = self._upstream_client()
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


def _is_app_document(scope: Scope) -> bool:
    """True for HTML navigations that only the application can answer.

    Vite runs with ``appType: 'custom'``: it never serves an HTML document,
    and a route such as ``/about`` carries no file extension it could resolve
    from its module graph or public dir. Probing it first would add a full
    loopback roundtrip to every page refresh with a guaranteed 404 as the
    answer. Requests that name a file (``/favicon.ico``, ``/logo.svg``) keep
    the probe: those may live in Vite's ``public/`` directory.
    """
    accept = dict(scope.get("headers", ())).get(b"accept", b"").lower()
    if b"text/html" not in accept:
        return False
    return "." not in scope["path"].rsplit("/", 1)[-1]


def _host_name(scope: Scope) -> str:
    """Return the request Host header without its port, lowercased."""
    for name, value in scope.get("headers", ()):
        if name.lower() == b"host":
            host: str = value.decode("latin-1").strip().lower()
            if host.startswith("["):  # IPv6 literal, e.g. [::1]:3000
                end = host.find("]")
                return host[1:end] if end != -1 else host
            if host.count(":") == 1:
                return host.split(":", 1)[0]
            return host
    return ""


def _host_allowed(scope: Scope) -> bool:
    """Accept only localhost names and IP literals, mirroring Vite's policy.

    Vite's own allowed-host check is bypassed by construction: the proxy
    rewrites the upstream Host to the loopback address. Replaying the check
    here stops DNS-rebinding pages and hostile origins from reading project
    files through the forwarded ``/@fs/`` endpoints. Requests that are not
    Vite-only keep their existing app behaviour.
    """
    host = _host_name(scope)
    if not host:
        return False
    if host == "localhost" or host.endswith(".localhost"):
        return True
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return True


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


async def _send_forbidden(send: Send) -> None:
    """Refuse Vite-only assets for a non-local Host."""
    await send(
        {
            "type": "http.response.start",
            "status": 403,
            "headers": [(b"content-type", b"text/plain; charset=utf-8")],
        }
    )
    await send({"type": "http.response.body", "body": b"Host not allowed for Vite dev assets"})


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
