"""`useHealth`: /health/live and /health/ready for load balancers and Kubernetes probes (#86)."""

# ruff: noqa: ARG001 - ASGI callables take (scope, receive, send) whether they use them or not

from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from nexy.helpers.server.access_log import AccessLogMiddleware
from nexy.helpers.server.health import HealthMiddleware


async def _fallback(scope, receive, send):
    """The application behind the probes: it answers 418 to every request."""
    await send({"type": "http.response.start", "status": 418, "headers": []})
    await send({"type": "http.response.body", "body": b"app"})


async def _probe(app: Any, path: str, method: str = "GET") -> tuple[int, Any]:
    """One HTTP request through *app*: its status and the JSON of its body."""
    sent: list[dict[str, Any]] = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    scope = {"type": "http", "method": method, "path": path, "headers": [], "root_path": ""}
    await app(scope, receive, send)
    body = b"".join(m.get("body", b"") for m in sent[1:])
    return sent[0]["status"], json.loads(body) if body.startswith(b"{") else body


async def _lifespan_app(scope, receive, send):
    """An application that starts and stops when the server says so."""
    while True:
        message = await receive()
        if message["type"] == "lifespan.startup":
            await send({"type": "lifespan.startup.complete"})
        elif message["type"] == "lifespan.shutdown":
            await send({"type": "lifespan.shutdown.complete"})
            return


class TestLifecycle:
    def test_ready_follows_startup_and_shutdown_and_live_does_not(self):
        async def scenario() -> list[tuple[int, Any, int, Any]]:
            health = HealthMiddleware(_lifespan_app)
            server_says: asyncio.Queue[dict[str, str]] = asyncio.Queue()
            app_says: asyncio.Queue[dict[str, str]] = asyncio.Queue()
            lifespan = asyncio.create_task(
                health({"type": "lifespan"}, server_says.get, app_says.put)
            )
            seen = []

            async def look() -> None:
                live = await _probe(health, "/health/live")
                ready = await _probe(health, "/health/ready")
                seen.append((*live, *ready))

            await look()  # the server has not asked the application to start
            await server_says.put({"type": "lifespan.startup"})
            assert (await app_says.get())["type"] == "lifespan.startup.complete"
            await look()
            await server_says.put({"type": "lifespan.shutdown"})
            await lifespan
            await look()
            return seen

        starting, running, stopping = asyncio.run(scenario())
        assert starting == (200, {"status": "ok"}, 503, {"status": "starting"})
        assert running == (200, {"status": "ok"}, 200, {"status": "ready"})
        assert stopping == (200, {"status": "ok"}, 503, {"status": "stopping"})

    def test_a_failed_startup_is_never_ready(self):
        async def failing(scope, receive, send):
            await receive()
            await send({"type": "lifespan.startup.failed", "message": "boom"})

        async def scenario() -> tuple[int, Any]:
            health = HealthMiddleware(failing)
            await health({"type": "lifespan"}, _startup_once(), _discard)
            return await _probe(health, "/health/ready")

        assert asyncio.run(scenario()) == (503, {"status": "starting"})

    def test_the_lifespan_reaches_the_application_untouched(self):
        received: list[str] = []

        async def app(scope, receive, send):
            received.append((await receive())["type"])
            await send({"type": "lifespan.startup.complete"})

        async def scenario() -> None:
            await HealthMiddleware(app)({"type": "lifespan"}, _startup_once(), _discard)

        asyncio.run(scenario())
        assert received == ["lifespan.startup"]


def _startup_once():
    async def receive():
        return {"type": "lifespan.startup"}

    return receive


async def _discard(message):
    return None


class TestRequests:
    @pytest.mark.parametrize("path", ["/health/live", "/health/ready"])
    @pytest.mark.parametrize("method", ["GET", "HEAD"])
    def test_a_probe_is_answered_before_the_application(self, path, method):
        status, _ = asyncio.run(_probe(HealthMiddleware(_fallback), path, method))
        assert status != 418

    def test_a_probe_is_never_cached(self):
        sent: list[dict[str, Any]] = []

        async def send(message):
            sent.append(message)

        async def scenario() -> None:
            scope = {"type": "http", "method": "GET", "path": "/health/live"}
            await HealthMiddleware(_fallback)(scope, None, send)

        asyncio.run(scenario())
        assert (b"cache-control", b"no-store") in sent[0]["headers"]

    @pytest.mark.parametrize(
        ("path", "method"),
        [
            ("/", "GET"),
            ("/health", "GET"),
            ("/health/live/", "GET"),
            ("/health/liveness", "GET"),
            ("/health/live", "POST"),
            ("/health/ready", "DELETE"),
        ],
    )
    def test_anything_else_goes_to_the_application(self, path, method):
        status, _ = asyncio.run(_probe(HealthMiddleware(_fallback), path, method))
        assert status == 418

    def test_a_probe_is_not_in_the_access_log(self):
        lines: list[str] = []
        app = HealthMiddleware(AccessLogMiddleware(_fallback, log=lines.append))

        asyncio.run(_probe(app, "/health/live"))
        asyncio.run(_probe(app, "/health/ready"))
        assert lines == []

        asyncio.run(_probe(app, "/"))
        assert len(lines) == 1


class TestAssembledApp:
    """The setting, read from nexyconfig.py, mounts the middleware on the real application."""

    def _client(self, nexy_project, attrs: str = "useHealth = True") -> TestClient:
        from nexy.modules.routers.app import AppServer

        nexy_project(attrs)
        return TestClient(AppServer().run(), raise_server_exceptions=False)

    def test_it_is_off_by_default(self, nexy_project):
        with self._client(nexy_project, "") as client:
            assert client.get("/health/live").status_code == 404
            assert client.get("/health/ready").status_code == 404

    def test_both_endpoints_answer_once_the_application_has_started(self, nexy_project):
        with self._client(nexy_project) as client:
            live = client.get("/health/live")
            ready = client.get("/health/ready")
        assert (live.status_code, live.json()) == (200, {"status": "ok"})
        assert (ready.status_code, ready.json()) == (200, {"status": "ready"})

    def test_the_application_is_not_ready_before_its_lifespan_has_run(self, nexy_project):
        client = self._client(nexy_project)  # not entered: the server never started it
        ready = client.get("/health/ready")
        assert (ready.status_code, ready.json()) == (503, {"status": "starting"})
        assert client.get("/health/live").status_code == 200

    def test_the_endpoints_are_not_in_the_openapi_schema(self, nexy_project):
        with self._client(nexy_project) as client:
            paths = client.get("/openapi.json").json()["paths"]
        assert not [path for path in paths if path.startswith("/health")]

    def test_a_probe_gets_through_the_host_check_and_the_https_redirect(self, nexy_project):
        attrs = 'useHealth = True\nuseTrustedHost = {"allowed_hosts": ["example.com"]}'
        with self._client(nexy_project, attrs + "\nuseHTTPSRedirect = True") as client:
            assert client.get("/health/ready").status_code == 200
            assert client.get("/", follow_redirects=False).status_code != 200
