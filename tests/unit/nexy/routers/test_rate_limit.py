"""`useRateLimit`: a 429 for a client that calls too often (#465)."""

# ruff: noqa: ARG001 - ASGI callables take (scope, receive, send) whether they use them or not

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from nexy.helpers.server.rate_limit import RateLimitMiddleware


class _Clock:
    """A clock a test moves by hand."""

    def __init__(self, now: float = 0.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now


async def _fallback(scope, receive, send):
    """The application behind the limit: it answers 418 to every request."""
    await send({"type": "http.response.start", "status": 418, "headers": []})
    await send({"type": "http.response.body", "body": b"app"})


_NO_CLIENT: Any = object()


async def _call(app: Any, path: str = "/", client: Any = ("10.0.0.1", 1)) -> list[dict[str, Any]]:
    """One HTTP request through *app*: the ASGI messages it sent."""
    sent: list[dict[str, Any]] = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    scope: dict[str, Any] = {"type": "http", "method": "GET", "path": path, "headers": []}
    if client is not _NO_CLIENT:
        scope["client"] = client
    await app(scope, receive, send)
    return sent


def _status(app: Any, path: str = "/", client: Any = ("10.0.0.1", 1)) -> int:
    return asyncio.run(_call(app, path, client))[0]["status"]


def _retry_after(app: Any) -> str:
    start = asyncio.run(_call(app))[0]
    return dict(start["headers"])[b"retry-after"].decode()


def _limited(requests: int = 60, per: float = 60, clock=None, **kwargs) -> RateLimitMiddleware:
    return RateLimitMiddleware(
        _fallback, requests=requests, per=per, clock=clock or _Clock(), **kwargs
    )


def _use_up(app: Any, times: int, **kwargs) -> None:
    for _ in range(times):
        _status(app, **kwargs)


class TestLimit:
    def test_rate_limit_the_request_over_the_limit_is_a_429(self):
        app = _limited()
        _use_up(app, 60)
        assert _status(app) == 429

    def test_rate_limit_the_last_request_within_the_limit_is_served(self):
        app = _limited()
        _use_up(app, 59)
        assert _status(app) == 418

    def test_rate_limit_a_429_carries_retry_after(self):
        app = _limited(requests=1, per=60, clock=_Clock(0.0))
        _use_up(app, 1)
        assert _retry_after(app) == "60"

    def test_rate_limit_retry_after_counts_to_the_end_of_the_window(self):
        clock = _Clock(0.0)
        app = _limited(requests=1, per=60, clock=clock)
        _use_up(app, 1)
        clock.now = 45.5
        assert _retry_after(app) == "15"

    def test_rate_limit_retry_after_is_at_least_one_second(self):
        clock = _Clock(0.0)
        app = _limited(requests=1, per=60, clock=clock)
        _use_up(app, 1)
        clock.now = 59.999
        assert _retry_after(app) == "1"

    def test_rate_limit_a_429_is_never_cached(self):
        app = _limited(requests=1)
        _use_up(app, 1)
        start = asyncio.run(_call(app))[0]
        assert (b"cache-control", b"no-store") in start["headers"]

    def test_rate_limit_a_429_says_why_in_json(self):
        app = _limited(requests=1)
        _use_up(app, 1)
        body = asyncio.run(_call(app))[1]["body"]
        assert body == b'{"detail":"Too many requests"}'

    def test_rate_limit_another_address_is_not_affected(self):
        app = _limited()
        _use_up(app, 60)
        assert _status(app, client=("10.0.0.2", 1)) == 418

    def test_rate_limit_connections_of_one_address_count_together(self):
        app = _limited(requests=2)
        _use_up(app, 2, client=("10.0.0.1", 1))
        assert _status(app, client=("10.0.0.1", 2)) == 429

    def test_rate_limit_a_refused_request_never_reaches_the_application(self):
        reached: list[str] = []

        async def app(scope, receive, send):
            reached.append(scope["path"])
            await _fallback(scope, receive, send)

        limited = RateLimitMiddleware(app, requests=1, per=60, clock=_Clock())
        _use_up(limited, 2)
        assert reached == ["/"]

    def test_rate_limit_a_new_window_lets_the_client_in_again(self):
        clock = _Clock(0.0)
        app = _limited(requests=1, per=60, clock=clock)
        _use_up(app, 2)
        clock.now = 60.0
        assert _status(app) == 418

    def test_rate_limit_a_scope_without_client_shares_one_count(self):
        app = _limited(requests=2)
        _use_up(app, 2, client=_NO_CLIENT)
        assert _status(app, client=None) == 429


class TestPaths:
    def test_rate_limit_paths_limit_only_their_prefixes(self):
        app = _limited(requests=1, paths=["/api/"])
        _use_up(app, 1, path="/api/users")
        assert _status(app, path="/api/users") == 429

    def test_rate_limit_a_path_outside_paths_is_not_counted(self):
        app = _limited(requests=1, paths=["/api/"])
        _use_up(app, 5, path="/about")
        assert _status(app, path="/about") == 418

    def test_rate_limit_a_path_outside_paths_does_not_use_up_the_limit(self):
        app = _limited(requests=1, paths=["/api/"])
        _use_up(app, 5, path="/about")
        assert _status(app, path="/api/users") == 418

    def test_rate_limit_any_of_several_prefixes_is_limited(self):
        app = _limited(requests=1, paths=["/api/", "/login"])
        _use_up(app, 1, path="/login")
        assert _status(app, path="/login") == 429

    def test_rate_limit_every_path_is_limited_without_paths(self):
        app = _limited(requests=1)
        _use_up(app, 1, path="/anything")
        assert _status(app, path="/else") == 429


class TestOtherScopes:
    def test_rate_limit_a_lifespan_scope_passes_through(self):
        seen: list[str] = []

        async def app(scope, receive, send):
            seen.append(scope["type"])

        limited = RateLimitMiddleware(app, requests=1, per=60, clock=_Clock())
        asyncio.run(limited({"type": "lifespan"}, None, None))
        assert seen == ["lifespan"]

    def test_rate_limit_a_websocket_scope_passes_through(self):
        seen: list[str] = []

        async def app(scope, receive, send):
            seen.append(scope["type"])

        limited = RateLimitMiddleware(app, requests=1, per=60, clock=_Clock())
        for _ in range(3):
            asyncio.run(limited({"type": "websocket", "path": "/ws"}, None, None))
        assert seen == ["websocket"] * 3

    def test_rate_limit_a_websocket_is_not_counted(self):
        app = _limited(requests=1)
        asyncio.run(app({"type": "websocket", "path": "/ws"}, None, _noop))
        assert _status(app) == 418


async def _noop(message):
    return None


class TestSettings:
    @pytest.mark.parametrize("requests", [0, -1, "10", 1.5])
    def test_rate_limit_requests_below_one_is_rejected(self, requests):
        with pytest.raises(ValueError, match="useRateLimit: 'requests'"):
            RateLimitMiddleware(_fallback, requests=requests, per=60)

    @pytest.mark.parametrize("per", [0, -5, "60"])
    def test_rate_limit_per_not_positive_is_rejected(self, per):
        with pytest.raises(ValueError, match="useRateLimit: 'per'"):
            RateLimitMiddleware(_fallback, requests=60, per=per)

    def test_rate_limit_a_fractional_window_is_accepted(self):
        assert RateLimitMiddleware(_fallback, requests=1, per=0.5).per == 0.5

    def test_rate_limit_the_default_clock_is_the_monotonic_clock(self):
        app = RateLimitMiddleware(_fallback, requests=1, per=60)
        assert _status(app) == 418
