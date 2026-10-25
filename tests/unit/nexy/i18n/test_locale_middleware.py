import asyncio

import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from nexy.modules.i18n.core import L
from nexy.modules.i18n.middleware import LocaleMiddleware


async def _request(app, path="/", headers=None, cookies=None, extra=()):
    header_bytes = [(b"host", b"testserver"), *extra]
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


def _raw_cookie(app, value: str):
    import json

    async def go():
        scope_headers = {"cookie": value}
        status, hdrs, body = await _request(app, "/hello", headers=scope_headers)
        return status, hdrs, json.loads(body)

    return asyncio.run(go())


def test_cookie_among_other_cookies(app):
    _, _, data = _raw_cookie(app, "theme=dark; nexy-locale=fr; session=abc")
    assert data["locale"] == "fr"


def test_quoted_cookie_value_is_unquoted(app):
    _, _, data = _raw_cookie(app, 'nexy-locale="fr"')
    assert data["locale"] == "fr"


def test_unknown_cookie_locale_falls_back_to_header_then_default(app):
    _, _, data = _raw_cookie(app, "nexy-locale=xx")
    assert data["locale"] == "en"


def test_matching_cookie_means_no_set_cookie_header(app):
    _, hdrs, _ = _raw_cookie(app, "nexy-locale=en")
    assert "set-cookie" not in hdrs


def test_mismatching_cookie_is_refreshed(app):
    _, hdrs, _ = _raw_cookie(app, "nexy-locale=xx")
    assert "nexy-locale=en" in hdrs.get("set-cookie", "")


def test_set_cookie_value_is_stable_across_requests(app):
    first = asyncio.run(_request(app, "/hello"))[1]["set-cookie"]
    second = asyncio.run(_request(app, "/hello"))[1]["set-cookie"]
    assert first == second


def test_cookie_split_across_several_headers_is_read(app):
    # HTTP/2 clients may send one `cookie` header per cookie.
    import json

    async def go():
        extra = [(b"cookie", b"theme=dark"), (b"cookie", b"nexy-locale=fr")]
        _, hdrs, body = await _request(app, "/hello", extra=extra)
        return hdrs, json.loads(body)

    headers, data = asyncio.run(go())
    assert data["locale"] == "fr"
    assert "set-cookie" not in headers


def test_language_split_across_several_headers_is_read(app):
    import json

    async def go():
        extra = [(b"accept-language", b"de"), (b"accept-language", b"fr")]
        _, _, body = await _request(app, "/hello", extra=extra)
        return json.loads(body)

    assert asyncio.run(go())["locale"] == "fr"


def test_middleware_uses_no_private_stdlib_helper():
    import inspect

    from nexy.modules.i18n import middleware

    assert "http.cookies import _" not in inspect.getsource(middleware)
