"""`useRateLimit` is read from nexyconfig.py and mounted on the real application."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from nexy.helpers.server import access_log
from nexy.helpers.server.rate_limit import RateLimitMiddleware

LIMIT = 'useRateLimit = {"requests": 60, "per": 60}'


def _server(nexy_project, attrs: str):
    from nexy.modules.routers.app import AppServer

    nexy_project(attrs)
    server = AppServer()
    return server, TestClient(server.run(), raise_server_exceptions=False)


def _statuses(client: TestClient, path: str, count: int) -> list[int]:
    return [client.get(path).status_code for _ in range(count)]


def test_app_rate_limit_the_request_over_the_limit_is_a_429(nexy_project):
    _server_, client = _server(nexy_project, LIMIT)
    assert _statuses(client, "/nowhere", 61)[-1] == 429


def test_app_rate_limit_the_requests_within_the_limit_are_not_a_429(nexy_project):
    _server_, client = _server(nexy_project, LIMIT)
    assert 429 not in _statuses(client, "/nowhere", 60)


def test_app_rate_limit_a_429_carries_retry_after(nexy_project):
    _server_, client = _server(nexy_project, LIMIT)
    _statuses(client, "/nowhere", 60)
    assert int(client.get("/nowhere").headers["retry-after"]) >= 1


def test_app_rate_limit_is_off_by_default(nexy_project):
    server, _client = _server(nexy_project, "")
    assert RateLimitMiddleware not in [m.cls for m in server.server.user_middleware]


def test_app_rate_limit_is_mounted_when_set(nexy_project):
    server, _client = _server(nexy_project, LIMIT)
    assert RateLimitMiddleware in [m.cls for m in server.server.user_middleware]


def test_app_rate_limit_a_health_probe_is_never_limited(nexy_project):
    _server_, client = _server(nexy_project, LIMIT + "\nuseHealth = True")
    _statuses(client, "/nowhere", 61)
    assert client.get("/health/live").status_code == 200


def test_app_rate_limit_a_429_is_in_the_access_log(nexy_project, monkeypatch):
    lines: list[str] = []
    monkeypatch.setattr(access_log, "_write_line", lines.append)
    _server_, client = _server(nexy_project, 'useRateLimit = {"requests": 1, "per": 60}')
    _statuses(client, "/nowhere", 2)
    assert "429" in lines[-1]


def test_app_rate_limit_an_invalid_setting_fails_when_the_stack_is_built(nexy_project):
    # Starlette builds its middleware stack when the server starts, before any request is served.
    server, _client = _server(nexy_project, 'useRateLimit = {"requests": 0, "per": 60}')
    with pytest.raises(ValueError, match="useRateLimit"):
        server.server.build_middleware_stack()
