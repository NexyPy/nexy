"""Contract of the Vite dev-server proxy middleware.

The dev server must expose a single public origin. Vite runs on an internal
loopback port, and this middleware forwards Vite's own traffic there. Everything
Vite does not recognise reaches the Nexy application untouched.

Each test stands up a throwaway loopback upstream that behaves like Vite, so the
real forwarding code path runs: request framing, streamed response bodies, and
the WebSocket relay. The fake mirrors Vite's decisive behaviour: module-graph
paths answer 200, application routes answer 404. Tests follow the house style:
sync functions driving ``asyncio.run`` over an inner coroutine (this project has
no pytest-asyncio).
"""

import asyncio
import socket
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any

import httpx
import pytest
from websockets.asyncio.server import ServerConnection, serve
from websockets.datastructures import Headers
from websockets.http11 import Request, Response

from nexy.helpers.server.proxy import (
    VITE_ONLY_PREFIXES,
    ViteProxyMiddleware,
    vite_proxy_port,
)

Scope = dict[str, Any]
Message = dict[str, Any]

FAKE_BODY = b"vite"

# Paths the fake Vite serves, mirroring its module graph.
VITE_MODULE_PREFIXES = ("/@vite/", "/@id/", "/@fs/", "/__nexy__/", "/node_modules/", "/src/")


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _http_scope(path: str, method: str = "GET", host: str = "localhost:3000") -> Scope:
    return {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [(b"host", host.encode("latin-1"))],
        "scheme": "http",
        "server": ("localhost", 3000),
        "client": ("127.0.0.1", 50000),
        "state": {},
    }


def _websocket_scope(
    path: str = "/", subprotocols: list[str] | None = None, host: str = "localhost:3000"
) -> Scope:
    return {
        "type": "websocket",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [(b"host", host.encode("latin-1"))],
        "scheme": "ws",
        "server": ("localhost", 3000),
        "client": ("127.0.0.1", 50000),
        "subprotocols": subprotocols or [],
        "state": {},
    }


class _Recorder:
    """Collects the ASGI messages the middleware sends."""

    def __init__(self) -> None:
        self.messages: list[Message] = []

    async def __call__(self, message: Message) -> None:
        self.messages.append(message)

    @property
    def status(self) -> int | None:
        start = next((m for m in self.messages if m["type"] == "http.response.start"), None)
        return None if start is None else int(start["status"])

    @property
    def headers(self) -> list[tuple[bytes, bytes]]:
        start = next((m for m in self.messages if m["type"] == "http.response.start"), None)
        return [] if start is None else list(start["headers"])

    @property
    def body(self) -> bytes:
        return b"".join(
            m.get("body", b"") for m in self.messages if m["type"] == "http.response.body"
        )


class _FakeApp:
    """Stand-in for the Nexy ASGI app; records that it was reached."""

    def __init__(self) -> None:
        self.reached = False

    async def __call__(
        self, _scope: Scope, _receive: Callable[..., Any], send: Callable[..., Any]
    ) -> None:
        self.reached = True
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"nexy"})


async def _empty_receive() -> Message:
    return {"type": "http.request", "body": b"", "more_body": False}


async def _disconnect_receive() -> Message:
    return {"type": "websocket.disconnect", "code": 1000}


async def _websocket_app(
    _scope: Scope, _receive: Callable[..., Any], send: Callable[..., Any]
) -> None:
    await send({"type": "websocket.accept", "subprotocol": None})


@asynccontextmanager
async def _fake_vite() -> AsyncIterator[int]:
    """Run a one-port upstream that answers like Vite for HTTP and WebSocket.

    ``process_request`` forces an HTTP response for plain requests and returns
    ``None`` for WebSocket upgrades, which is how a single port serves both.
    Unknown paths answer 404, exactly as a real Vite dev server does.
    """

    def process_request(_connection: ServerConnection, request: Request) -> Response | None:
        if request.headers.get("Upgrade", "").lower() == "websocket":
            return None
        path = request.path.split("?", 1)[0]
        if not path.startswith(VITE_MODULE_PREFIXES):
            return Response(404, "Not Found", Headers(), b"")
        headers = Headers({"content-type": "application/javascript", "x-upstream": "vite"})
        return Response(200, "OK", headers, FAKE_BODY)

    async def handler(connection: ServerConnection) -> None:
        async for message in connection:
            if message == "binary":
                await connection.send(b"\x00\x01")
            elif isinstance(message, bytes):
                await connection.send(b"echo:" + message)
            else:
                await connection.send(f"echo:{message}")

    port = _free_port()
    async with serve(
        handler, "127.0.0.1", port, subprotocols=["vite-hmr"], process_request=process_request
    ):
        yield port


async def _run(scope: Scope, receive: Callable[..., Any], app: Any = None) -> _Recorder:
    """Drive one connection through the middleware against a fake Vite."""
    send = _Recorder()
    async with _fake_vite() as port:
        middleware = ViteProxyMiddleware(app or _FakeApp(), port=port)
        await middleware(scope, receive, send)
    return send


def _http(
    path: str, app: Any = None, method: str = "GET", host: str = "localhost:3000"
) -> _Recorder:
    return asyncio.run(_run(_http_scope(path, method, host), _empty_receive, app))


def _nav_scope(path: str) -> Scope:
    """Scope of a browser document navigation (Accept: text/html)."""
    scope = _http_scope(path)
    scope["headers"].append((b"accept", b"text/html,application/xhtml+xml"))
    return scope


@asynccontextmanager
async def _fake_vite_serves_all() -> AsyncIterator[int]:
    """Upstream that answers 200 for every path (no 404 fallthrough)."""

    def process_request(_connection: ServerConnection, request: Request) -> Response | None:
        if request.headers.get("Upgrade", "").lower() == "websocket":
            return None
        headers = Headers({"content-type": "application/javascript"})
        return Response(200, "OK", headers, FAKE_BODY)

    port = _free_port()
    async with serve(lambda c: _echo(c), "127.0.0.1", port, process_request=process_request):
        yield port


async def _echo(connection: ServerConnection) -> None:
    async for _message in connection:
        pass


@pytest.mark.parametrize(
    "path",
    [
        "/@vite/client",
        "/@id/foo",
        "/@fs/tmp/x",
        "/__nexy__/main.ts",
        "/node_modules/.vite/deps/x.js",
        "/src/globale.css",
    ],
)
def test_proxy_forwards_module_paths(path: str) -> None:
    assert _http(path).body == FAKE_BODY


@pytest.mark.parametrize("path", ["/", "/about", "/api/items", "/favicon.ico"])
def test_proxy_falls_through_for_app_paths(path: str) -> None:
    assert _http(path).body == b"nexy"


def test_proxy_reaches_app_for_non_vite_path() -> None:
    app = _FakeApp()
    _http("/about", app)
    assert app.reached is True


def test_proxy_does_not_reach_app_for_module_path() -> None:
    app = _FakeApp()
    _http("/@vite/client", app)
    assert app.reached is False


def test_proxy_preserves_upstream_status() -> None:
    assert _http("/@vite/client").status == 200


def test_proxy_forwards_upstream_headers() -> None:
    assert (b"x-upstream", b"vite") in _http("/@vite/client").headers


def test_proxy_strips_hop_by_hop_headers() -> None:
    names = {name for name, _ in _http("/@vite/client").headers}
    assert b"content-length" not in names


def test_proxy_forwards_websocket_upgrade() -> None:
    send = asyncio.run(_run(_websocket_scope(subprotocols=["vite-hmr"]), _disconnect_receive))
    assert send.messages[0]["type"] == "websocket.accept"


def test_proxy_does_not_reach_app_for_hmr_socket() -> None:
    app = _FakeApp()
    asyncio.run(_run(_websocket_scope(subprotocols=["vite-hmr"]), _disconnect_receive, app))
    assert app.reached is False


def test_proxy_leaves_plain_websocket_to_app() -> None:
    send = asyncio.run(
        _run(_websocket_scope(path="/_nexy/hmr"), _disconnect_receive, _websocket_app)
    )
    assert send.messages[0]["type"] == "websocket.accept"


def test_proxy_relays_websocket_payload() -> None:
    replies = _websocket_roundtrip(text="ping").messages
    assert {"type": "websocket.send", "text": "echo:ping"} in replies


def test_proxy_returns_502_for_vite_only_path_when_unreachable() -> None:
    async def run() -> _Recorder:
        send = _Recorder()
        middleware = ViteProxyMiddleware(_FakeApp(), port=_free_port())
        await middleware(_http_scope("/@vite/client"), _empty_receive, send)
        return send

    assert asyncio.run(run()).status == 502


def test_proxy_falls_through_to_app_when_vite_unreachable() -> None:
    async def run() -> _Recorder:
        send = _Recorder()
        middleware = ViteProxyMiddleware(_FakeApp(), port=_free_port())
        await middleware(_http_scope("/about"), _empty_receive, send)
        return send

    assert asyncio.run(run()).body == b"nexy"


def test_proxy_returns_1011_when_hmr_unreachable() -> None:
    async def run() -> _Recorder:
        send = _Recorder()
        middleware = ViteProxyMiddleware(_FakeApp(), port=_free_port())
        await middleware(_websocket_scope(subprotocols=["vite-hmr"]), _disconnect_receive, send)
        return send

    assert asyncio.run(run()).messages[0] == {"type": "websocket.close", "code": 1011}


def test_proxy_passes_unsafe_method_to_app() -> None:
    app = _FakeApp()
    _http("/api/items", app, method="POST")
    assert app.reached is True


def test_html_navigation_skips_upstream_probe() -> None:
    """A document navigation must not wait for a guaranteed Vite 404.

    The upstream here answers 200 for every path, so the app body proves the
    probe was skipped entirely (a probe would relay FAKE_BODY instead).
    """

    async def run() -> tuple[_Recorder, _FakeApp]:
        send = _Recorder()
        app = _FakeApp()
        async with _fake_vite_serves_all() as port:
            middleware = ViteProxyMiddleware(app, port=port)
            await middleware(_nav_scope("/about"), _empty_receive, send)
        return send, app

    body, app = asyncio.run(run())
    assert body.body == b"nexy" and app.reached is True


def test_html_navigation_to_dotted_path_still_probes_vite() -> None:
    """``/favicon.ico`` may live in Vite's public dir: keep the probe."""

    async def run() -> _Recorder:
        send = _Recorder()
        async with _fake_vite_serves_all() as port:
            middleware = ViteProxyMiddleware(_FakeApp(), port=port)
            await middleware(_nav_scope("/favicon.ico"), _empty_receive, send)
        return send

    assert asyncio.run(run()).body == FAKE_BODY


def test_module_request_without_html_accept_still_probes_vite() -> None:
    """Script/module fetches send ``Accept: */*`` and must reach Vite."""

    async def run() -> _Recorder:
        send = _Recorder()
        async with _fake_vite_serves_all() as port:
            middleware = ViteProxyMiddleware(_FakeApp(), port=port)
            scope = _http_scope("/src/main.ts")
            scope["headers"].append((b"accept", b"*/*"))
            await middleware(scope, _empty_receive, send)
        return send

    assert asyncio.run(run()).body == FAKE_BODY


def test_proxy_reuses_one_upstream_client() -> None:
    """Keep-alive pooling: one AsyncClient for the middleware's lifetime."""

    async def run() -> None:
        middleware = ViteProxyMiddleware(_FakeApp(), port=_free_port())
        first = middleware._upstream_client()
        second = middleware._upstream_client()
        assert first is second
        await first.aclose()

    asyncio.run(run())


def test_upstream_client_ignores_proxy_env_vars() -> None:
    """trust_env must be off: HTTP_PROXY would detour loopback traffic."""

    async def run() -> httpx.AsyncClient:
        middleware = ViteProxyMiddleware(_FakeApp(), port=_free_port())
        client = middleware._upstream_client()
        assert client._trust_env is False
        await client.aclose()
        return client

    asyncio.run(run())


def test_proxy_passes_non_http_scope_to_app() -> None:
    async def run() -> _FakeApp:
        app = _FakeApp()
        middleware = ViteProxyMiddleware(app, port=_free_port())
        await middleware(
            {"type": "lifespan", "asgi": {"version": "3.0"}, "state": {}},
            _empty_receive,
            _Recorder(),
        )
        return app

    assert asyncio.run(run()).reached is True


def _websocket_roundtrip(text: str | None = None, payload: bytes | None = None) -> _Recorder:
    """Send one client frame, capture the reply, then disconnect."""

    async def run() -> _Recorder:
        inbox: asyncio.Queue[Message] = asyncio.Queue()
        message: Message = {"type": "websocket.receive"}
        if text is not None:
            message["text"] = text
        if payload is not None:
            message["bytes"] = payload
        await inbox.put(message)

        async def receive() -> Message:
            return await inbox.get()

        send = _Recorder()

        async def recording_send(reply: Message) -> None:
            await send(reply)
            if reply["type"] == "websocket.send":
                await inbox.put({"type": "websocket.disconnect", "code": 1000})

        async with _fake_vite() as port:
            middleware = ViteProxyMiddleware(_FakeApp(), port=port)
            await middleware(_websocket_scope(subprotocols=["vite-hmr"]), receive, recording_send)
        return send

    return asyncio.run(run())


def test_proxy_relays_binary_client_frame() -> None:
    replies = _websocket_roundtrip(payload=b"ping").messages
    assert {"type": "websocket.send", "bytes": b"echo:ping"} in replies


def test_proxy_relays_binary_upstream_frame() -> None:
    replies = _websocket_roundtrip(text="binary").messages
    assert {"type": "websocket.send", "bytes": b"\x00\x01"} in replies


def test_vite_proxy_port_is_none_when_vite_disabled(nexy_project, tmp_path, monkeypatch) -> None:
    nexy_project("useVite = False")
    (tmp_path / "vite.config.ts").write_text("", encoding="utf-8")
    monkeypatch.setenv("NEXY_DEV_SERVER", "1")
    assert vite_proxy_port() is None


def test_proxy_prefixes_cover_vite_paths() -> None:
    assert "/@vite/" in VITE_ONLY_PREFIXES


def test_proxy_rejects_vite_asset_for_foreign_host() -> None:
    response = _http("/@fs/tmp/secret", host="evil.example")
    assert response.status == 403


def test_proxy_does_not_forward_vite_asset_for_foreign_host() -> None:
    app = _FakeApp()
    response = _http("/@fs/tmp/secret", app, host="evil.example")
    assert response.body != FAKE_BODY and app.reached is False


def test_proxy_allows_lan_ip_host() -> None:
    assert _http("/@vite/client", host="192.168.1.50:8000").body == FAKE_BODY


def test_proxy_allows_localhost_subdomain() -> None:
    assert _http("/@vite/client", host="app.localhost:3000").body == FAKE_BODY


def test_proxy_falls_through_for_app_path_with_foreign_host() -> None:
    app = _FakeApp()
    response = _http("/about", app, host="evil.example")
    assert response.body == b"nexy" and app.reached is True


def test_hmr_socket_rejects_foreign_host() -> None:
    send = asyncio.run(
        _run(
            _websocket_scope(subprotocols=["vite-hmr"], host="evil.example"),
            _disconnect_receive,
        )
    )
    assert send.messages[0] == {"type": "websocket.close", "code": 1008}


def test_vite_proxy_port_is_none_outside_dev_mode(tmp_path, monkeypatch) -> None:
    (tmp_path / "__nexy__").mkdir()
    (tmp_path / "vite.config.ts").write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NEXY_DEV_SERVER", raising=False)
    assert vite_proxy_port() is None


def test_vite_proxy_port_is_none_in_production(tmp_path, monkeypatch) -> None:
    (tmp_path / "__nexy__").mkdir()
    (tmp_path / "__nexy__" / "nexy.prod").write_text("", encoding="utf-8")
    (tmp_path / "vite.config.ts").write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NEXY_DEV_SERVER", "1")
    assert vite_proxy_port() is None


def test_vite_proxy_port_is_none_without_vite_config(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NEXY_DEV_SERVER", "1")
    assert vite_proxy_port() is None


def test_vite_proxy_port_reads_client_port(tmp_path, monkeypatch) -> None:
    (tmp_path / "__nexy__").mkdir()
    (tmp_path / "vite.config.ts").write_text("", encoding="utf-8")
    (tmp_path / "__nexy__" / "client.port").write_text("5199", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NEXY_DEV_SERVER", "1")
    assert vite_proxy_port() == 5199


class TestAppDocumentShortcut:
    @staticmethod
    def _scope(path: str, accept: str = "text/html") -> dict:
        return {"path": path, "headers": [(b"accept", accept.encode())]}

    def test_extensionless_page_goes_straight_to_the_app(self):
        from nexy.helpers.server.proxy import _is_app_document

        assert _is_app_document(self._scope("/about"))

    def test_plugin_ui_and_well_known_paths_still_reach_vite(self):
        from nexy.helpers.server.proxy import _is_app_document

        assert not _is_app_document(self._scope("/__inspect/"))
        assert not _is_app_document(self._scope("/.well-known/apple-app-site-association"))
        assert not _is_app_document(self._scope("/blog/_drafts/post"))

    def test_files_and_non_html_requests_are_probed(self):
        from nexy.helpers.server.proxy import _is_app_document

        assert not _is_app_document(self._scope("/logo.svg"))
        assert not _is_app_document(self._scope("/about", accept="application/json"))
