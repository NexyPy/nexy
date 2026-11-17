"""A request body over the limit is refused with a 413 before the application reads it all."""

from __future__ import annotations

from collections.abc import Iterator

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from nexy.helpers.server.body_limit import BodyLimitMiddleware

LIMIT = 10


async def _echo(request: Request) -> PlainTextResponse:
    return PlainTextResponse(str(len(await request.body())))


def _client(limit: int | None = LIMIT) -> TestClient:
    app = Starlette(routes=[Route("/", _echo, methods=["POST"])])
    return TestClient(BodyLimitMiddleware(app, limit=limit))


def _chunks(size: int) -> Iterator[bytes]:
    """A body sent without a Content-Length header, one byte at a time."""
    yield from (b"a" for _ in range(size))


def test_body_limit_a_body_at_the_limit_is_served():
    assert _client().post("/", content=b"a" * LIMIT).text == str(LIMIT)


def test_body_limit_a_declared_length_over_the_limit_is_a_413():
    assert _client().post("/", content=b"a" * (LIMIT + 1)).status_code == 413


def test_body_limit_a_streamed_body_over_the_limit_is_a_413():
    assert _client().post("/", content=_chunks(LIMIT + 1)).status_code == 413


def test_body_limit_a_streamed_body_under_the_limit_is_served():
    assert _client().post("/", content=_chunks(LIMIT)).text == str(LIMIT)


def test_body_limit_the_413_says_why():
    response = _client().post("/", content=b"a" * (LIMIT + 1))
    assert response.json() == {"detail": f"The request body is over {LIMIT} bytes"}


def test_body_limit_none_turns_the_limit_off():
    assert _client(limit=None).post("/", content=b"a" * 1000).text == "1000"


def test_body_limit_a_bad_content_length_is_a_400():
    response = _client().post("/", content=b"a", headers={"content-length": "x"})
    assert response.status_code == 400
