"""A HEAD request to a route that answers GET gets the GET answer without its body (RFC 9110)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, Response
from fastapi.testclient import TestClient

from nexy.helpers.server.head_requests import HeadRequestsMiddleware


def _client() -> TestClient:
    app = FastAPI()
    app.add_middleware(HeadRequestsMiddleware)

    @app.get("/page")
    def page() -> PlainTextResponse:
        return PlainTextResponse("hello", headers={"x-page": "1"})

    @app.api_route("/own", methods=["GET", "HEAD"])
    def own() -> Response:
        return Response(headers={"x-own": "head"})

    @app.post("/form")
    def form() -> str:
        return "sent"

    return TestClient(app)


def test_head_on_a_get_route_answers_200():
    assert _client().head("/page").status_code == 200


def test_head_on_a_get_route_has_no_body():
    assert _client().head("/page").content == b""


def test_head_on_a_get_route_keeps_the_get_headers():
    client = _client()
    assert client.head("/page").headers == client.get("/page").headers


def test_a_route_with_its_own_head_handler_keeps_it():
    assert _client().head("/own").headers["x-own"] == "head"


def test_head_on_a_post_only_route_is_still_refused():
    assert _client().head("/form").status_code == 405


def test_head_on_a_missing_route_is_404():
    assert _client().head("/nowhere").status_code == 404


def test_get_is_unchanged():
    assert _client().get("/page").text == "hello"
