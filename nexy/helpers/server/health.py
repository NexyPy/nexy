"""Liveness and readiness endpoints for load balancers and Kubernetes probes (`useHealth`, #86).

``GET /health/live`` answers 200 while the process answers. ``GET /health/ready`` answers 200 once
the application has started, and 503 while it starts and again once it is asked to stop: the phase
is read from the ASGI lifespan messages, so it follows the real startup and shutdown.

The middleware is the outermost one, so a probe is answered before the access log, the trusted
host check and the HTTPS redirect: the address a probe uses is the one of the pod, not of the site.
It adds no route, so the endpoints are not in the OpenAPI schema.
"""

from __future__ import annotations

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

LIVE_PATH = "/health/live"
READY_PATH = "/health/ready"
HEALTH_PATHS = (LIVE_PATH, READY_PATH)

_STARTING = "starting"
_READY = "ready"
_STOPPING = "stopping"
_NO_CACHE = {"cache-control": "no-store"}


class HealthMiddleware:
    """Pure ASGI middleware serving `HEALTH_PATHS` to GET and HEAD, before the application."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.phase = _STARTING

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            await self.app(scope, self._watch_receive(receive), self._watch_send(send))
        elif self._is_probe(scope):
            await self._answer(scope)(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    @staticmethod
    def _is_probe(scope: Scope) -> bool:
        return (
            scope["type"] == "http"
            and scope["method"] in ("GET", "HEAD")
            and scope["path"] in HEALTH_PATHS
        )

    def _answer(self, scope: Scope) -> JSONResponse:
        if scope["path"] == LIVE_PATH:
            return JSONResponse({"status": "ok"}, headers=_NO_CACHE)
        status = 200 if self.phase == _READY else 503
        return JSONResponse({"status": self.phase}, status_code=status, headers=_NO_CACHE)

    def _watch_receive(self, receive: Receive) -> Receive:
        """The server asking the application to stop: it is not ready any more."""

        async def watched() -> Message:
            message = await receive()
            if message["type"] == "lifespan.shutdown":
                self.phase = _STOPPING
            return message

        return watched

    def _watch_send(self, send: Send) -> Send:
        """The application saying it has started: from here it is ready."""

        async def watched(message: Message) -> None:
            if message["type"] == "lifespan.startup.complete":
                self.phase = _READY
            await send(message)

        return watched
