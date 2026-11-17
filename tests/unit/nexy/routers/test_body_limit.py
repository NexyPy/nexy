"""A request body over the limit is refused with a 413 before the application reads it all."""

from __future__ import annotations

import asyncio
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


def _scope(http_version: str, headers: list[tuple[bytes, bytes]]) -> dict:
    return {"type": "http", "http_version": http_version, "method": "POST", "headers": headers}


def _status(scope: dict, body: bytes) -> int:
    """The status the middleware answers when the application reads *body* to the end."""
    sent: list[dict] = []
    queue = [{"type": "http.request", "body": body, "more_body": False}]

    async def receive() -> dict:
        return queue.pop(0)

    async def send(message: dict) -> None:
        sent.append(message)

    async def app(_scope, app_receive, app_send) -> None:
        await app_receive()
        await app_send({"type": "http.response.start", "status": 200, "headers": []})
        await app_send({"type": "http.response.body", "body": b""})

    asyncio.run(BodyLimitMiddleware(app, limit=LIMIT)(scope, receive, send))
    return sent[0]["status"]


def _receive_given(scope: dict) -> tuple[object, object]:
    """The receive the server gave and the one the application got."""
    got: list[object] = []

    async def app(_scope, app_receive, _send) -> None:
        got.append(app_receive)

    async def receive() -> dict:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(_message: dict) -> None:
        return None

    asyncio.run(BodyLimitMiddleware(app, limit=LIMIT)(scope, receive, send))
    return receive, got[0]


def test_body_limit_an_http2_body_without_a_length_is_counted():
    assert _status(_scope("2", []), b"a" * (LIMIT + 1)) == 413


def test_body_limit_a_chunked_body_is_counted():
    chunked = _scope("1.1", [(b"transfer-encoding", b"chunked")])
    assert _status(chunked, b"a" * (LIMIT + 1)) == 413


def test_body_limit_a_request_without_a_body_is_not_wrapped():
    given, got = _receive_given(_scope("1.1", []))
    assert got is given


def test_body_limit_a_declared_length_is_not_wrapped():
    given, got = _receive_given(_scope("1.1", [(b"content-length", b"3")]))
    assert got is given
