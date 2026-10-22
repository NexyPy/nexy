import asyncio

import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from nexy.modules.i18n.core import L
from nexy.modules.i18n.middleware import LocaleMiddleware


async def _request(app, path="/", headers=None, cookies=None):
    header_bytes = [(b"host", b"testserver")]
    if headers:
        header_bytes += [(k.lower().encode(), v.encode()) for k, v in headers.items()]
    if cookies:
        joined = "; ".join(f"{k}={v}" for k, v in cookies.items())
        header_bytes.append((b"cookie", joined.encode()))
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
        "headers": header_bytes,
        "client": ("127.0.0.1", 12345),
        "server": ("127.0.0.1", 3000),
        "state": {},
    }
    status = 0
    response_headers = {}
    body = b""

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        nonlocal status, body
        if message["type"] == "http.response.start":
            status = message["status"]
            for k, v in message["headers"]:
                response_headers[k.decode().lower()] = v.decode()
        elif message["type"] == "http.response.body":
            body += message.get("body", b"")

    await app(scope, receive, send)
    return status, response_headers, body


@pytest.fixture
def app():
    L.configure(available=["en", "fr"], default="en")
    inner = Starlette(
        routes=[
            Route(
                "/hello",
                lambda request: JSONResponse(
                    {"locale": request.state.locale, "path": request.url.path}
                ),
            )
        ]
    )
    inner.add_middleware(LocaleMiddleware)
    return inner


def _get_locale(app, path="/", headers=None, cookies=None):
    import json

    status, hdrs, body = asyncio.run(_request(app, path, headers, cookies))
    assert status == 200
    return json.loads(body)


def test_locale_from_url_prefix(app):
    data = _get_locale(app, "/fr/hello")
    assert data["locale"] == "fr"
    assert data["path"] == "/hello"


def test_locale_default_locale(app):
    data = _get_locale(app, "/hello")
    assert data["locale"] == "en"


def test_locale_from_cookie(app):
    data = _get_locale(app, "/hello", cookies={"nexy-locale": "fr"})
    assert data["locale"] == "fr"


def test_locale_from_header(app):
    data = _get_locale(app, "/hello", headers={"Accept-Language": "fr-FR"})
    assert data["locale"] == "fr"


def test_locale_cookie_set_on_response(app):
    status, hdrs, _ = asyncio.run(_request(app, "/hello"))
    assert status == 200
    set_cookie = hdrs.get("set-cookie", "")
    assert "nexy-locale=en" in set_cookie
    assert "Max-Age=31536000" in set_cookie


def test_locale_middleware_is_pure_asgi():
    from starlette.middleware.base import BaseHTTPMiddleware

    assert not issubclass(LocaleMiddleware, BaseHTTPMiddleware)


def test_current_locale_contextvar_set():
    from nexy.modules.i18n.core import current_locale

    inner = Starlette(
        routes=[
            Route(
                "/hello",
                lambda _: JSONResponse({"locale": current_locale.get() or "en"}),
            )
        ]
    )
    inner.add_middleware(LocaleMiddleware)
    data = _get_locale(inner, "/fr/hello")
    assert data["locale"] == "fr"
