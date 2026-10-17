import asyncio
import json

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route

from nexy.routers.middlewares import PathMiddleware


async def _request(app, path="/hello"):
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": [(b"host", b"testserver")],
        "client": ("127.0.0.1", 12345),
        "server": ("127.0.0.1", 3000),
        "state": {},
    }
    status = 0
    body = b""

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        nonlocal status, body
        if message["type"] == "http.response.start":
            status = message["status"]
        elif message["type"] == "http.response.body":
            body += message.get("body", b"")

    await app(scope, receive, send)
    return status, body


def _app_with_path_middleware():
    inner = Starlette(
        routes=[
            Route(
                "/hello",
                lambda _: JSONResponse({"ok": True}),
            )
        ]
    )
    inner.add_middleware(PathMiddleware)
    return inner


def test_path_middleware_sets_current_request():
    from nexy.routers.context import current_request

    inner = Starlette(
        routes=[
            Route(
                "/hello",
                lambda _: JSONResponse({"path": current_request.get().url.path}),
            )
        ]
    )
    inner.add_middleware(PathMiddleware)
    status, body = asyncio.run(_request(inner))
    assert status == 200
    assert json.loads(body)["path"] == "/hello"


def test_path_middleware_clears_request_scope():
    inner = Starlette(
        routes=[
            Route(
                "/hello",
                lambda _: JSONResponse({"ok": True}),
            )
        ]
    )
    inner.add_middleware(PathMiddleware)
    status, _ = asyncio.run(_request(inner))
    assert status == 200
    from nexy.decorators import Container

    assert Container._request_store.get() is None


def test_path_middleware_is_pure_asgi():
    assert not issubclass(PathMiddleware, BaseHTTPMiddleware)
