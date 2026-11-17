"""Time an ASGI application in process: the same requests, no network, best of several rounds."""

from __future__ import annotations

import asyncio
import time
from typing import Any

ROUNDS = 5


def _scope(method: str, path: str, body: bytes) -> dict[str, Any]:
    headers = [(b"host", b"testserver"), (b"content-length", str(len(body)).encode())]
    if body:
        headers.append((b"content-type", b"application/json"))
    return {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "server": ("testserver", 80),
        "client": ("127.0.0.1", 1),
        "headers": headers,
    }


async def _one(app: Any, scope: dict[str, Any], body: bytes) -> int:
    status = 0

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message: dict[str, Any]) -> None:
        nonlocal status
        if message["type"] == "http.response.start":
            status = message["status"]

    await app(dict(scope), receive, send)
    return status


async def _round(app: Any, scope: dict[str, Any], body: bytes, count: int) -> float:
    started = time.perf_counter()
    for _ in range(count):
        status = await _one(app, scope, body)
    if status != 200:
        raise AssertionError(f"{scope['method']} {scope['path']} answered {status}")
    return (time.perf_counter() - started) / count


def seconds_per_request(
    app: Any, path: str, method: str = "GET", body: bytes = b"", count: int = 2000
) -> float:
    """The fastest of `ROUNDS` rounds of *count* requests, in seconds per request."""
    scope = _scope(method, path, body)

    async def best() -> float:
        await _round(app, scope, body, 200)
        return min([await _round(app, scope, body, count) for _ in range(ROUNDS)])

    return asyncio.run(best())
