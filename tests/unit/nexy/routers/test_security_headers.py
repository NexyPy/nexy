"""Production answers carry the safe default headers, and never override the application's own."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.testclient import TestClient

from nexy.helpers.server.security_headers import SecurityHeadersMiddleware


def _client() -> TestClient:
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/")
    def home() -> str:
        return "ok"

    @app.get("/own")
    def own() -> PlainTextResponse:
        return PlainTextResponse("x", headers={"referrer-policy": "no-referrer"})

    return TestClient(app)


def test_a_response_is_not_sniffed():
    assert _client().get("/").headers["x-content-type-options"] == "nosniff"


def test_a_response_limits_the_referrer():
    assert _client().get("/").headers["referrer-policy"] == "strict-origin-when-cross-origin"


def test_a_header_the_application_set_is_kept():
    assert _client().get("/own").headers["referrer-policy"] == "no-referrer"


def _raw_app(headers: list[tuple[bytes, bytes]]):
    async def app(_scope, _receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": headers})
        await send({"type": "http.response.body", "body": b"ok"})

    return SecurityHeadersMiddleware(app)


def test_a_header_set_in_another_case_is_kept():
    client = TestClient(_raw_app([(b"Referrer-Policy", b"no-referrer")]))
    assert client.get("/").headers.get_list("referrer-policy") == ["no-referrer"]


def test_the_headers_of_the_application_come_first():
    client = TestClient(_raw_app([(b"x-own", b"1")]))
    assert list(client.get("/").headers.keys())[:1] == ["x-own"]
