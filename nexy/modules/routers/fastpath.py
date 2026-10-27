"""Direct dispatch for trivial file routes.

FastAPI resolves every request through route matching, dependency solving and response
serialization. A handler that takes no parameters, has no dependency and no declared response model
needs none of that: ``async def GET(): return {"ok": True}`` is just "call it, encode the result".

This wrapper sits at the innermost layer of the router stack, below Starlette's exception handling,
so errors raised by a handler are processed exactly as on the normal path. Anything that is not a
plain match falls through to FastAPI untouched: other methods, dynamic paths, trailing slashes,
handlers with parameters, dependencies, response models or custom response classes.
"""

from __future__ import annotations

import inspect
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute, APIRouter
from starlette.responses import Response
from starlette.routing import Match
from starlette.types import ASGIApp, Receive, Scope, Send

_log = logging.getLogger("nexy.fastpath")
_Entry = tuple[Callable[[], Awaitable[Any]], APIRoute]


def _is_default_json(route: APIRoute) -> bool:
    placeholder = route.response_class
    return getattr(placeholder, "value", placeholder) is JSONResponse


def _has_no_inputs(route: APIRoute) -> bool:
    dependant = route.dependant
    return not (
        route.dependencies
        or route.callbacks
        or dependant.dependencies
        or dependant.query_params
        or dependant.path_params
        or dependant.header_params
        or dependant.cookie_params
        or dependant.body_params
    )


def _has_plain_response(route: APIRoute) -> bool:
    return (
        route.response_field is None
        and not getattr(route, "response_fields", None)
        and route.status_code in (None, 200)
        and _is_default_json(route)
        and not getattr(route, "is_json_stream", False)
        and not getattr(route, "is_sse_stream", False)
    )


def _is_trivial(route: APIRoute) -> bool:
    """True when FastAPI would do nothing for this route that the fast path does not do."""
    if route.methods is None or len(route.methods) != 1 or "{" in route.path:
        return False
    endpoint = route.endpoint
    if not inspect.iscoroutinefunction(endpoint) or inspect.signature(endpoint).parameters:
        return False
    return _has_no_inputs(route) and _has_plain_response(route)


async def _send_json(body: bytes, send: Send) -> None:
    headers = [
        (b"content-length", str(len(body)).encode("latin-1")),
        (b"content-type", b"application/json"),
    ]
    await send({"type": "http.response.start", "status": 200, "headers": headers})
    await send({"type": "http.response.body", "body": body})


def _shadowed(candidate: APIRoute, method: str, earlier: list[Any]) -> bool:
    """True when a route registered before *candidate* would answer its URL first."""
    probe: Scope = {"type": "http", "method": method, "path": candidate.path, "root_path": ""}
    for route in earlier:
        try:
            if route.matches(probe)[0] == Match.FULL:
                return True
        except Exception as error:
            # An unknown kind of route: stay on the safe side and let FastAPI serve this URL.
            _log.debug(
                "fast path skipped %s: %r cannot be matched (%s)", candidate.path, route, error
            )
            return True
    return False


def build_table(router: APIRouter) -> dict[tuple[str, str], _Entry]:
    """Map ``(METHOD, path)`` to the handler for every route the fast path may serve."""
    table: dict[tuple[str, str], _Entry] = {}
    earlier: list[Any] = []
    for route in router.routes:
        if isinstance(route, APIRoute) and route.methods and _is_trivial(route):
            method = next(iter(route.methods))
            key = (method, route.path)
            if key not in table and not _shadowed(route, method, earlier):
                table[key] = (route.endpoint, route)
        earlier.append(route)
    return table


def _encode(value: Any) -> bytes:
    """JSON bytes identical to what FastAPI's ``JSONResponse`` would produce."""
    try:
        return json.dumps(
            value, ensure_ascii=False, allow_nan=False, indent=None, separators=(",", ":")
        ).encode("utf-8")
    except TypeError:
        return json.dumps(
            jsonable_encoder(value),
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


class FastPath:
    """ASGI wrapper that serves trivial routes directly and defers everything else."""

    def __init__(self, router: APIRouter, inner: ASGIApp) -> None:
        self.router = router
        self.inner = inner
        self._seen: int | None = None
        self._table: dict[tuple[str, str], _Entry] = {}

    def _refresh(self) -> None:
        # Routes can be added, removed or replaced after startup (tests, plugins): rebuild when
        # the routes themselves change, not just how many there are.
        fingerprint = hash(tuple(map(id, self.router.routes)))
        if fingerprint != self._seen:
            self._table = build_table(self.router)
            self._seen = fingerprint

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and not scope.get("root_path"):
            self._refresh()
            entry = self._table.get((scope["method"], scope["path"]))
            if entry is not None:
                await self._answer(entry, scope, receive, send)
                return
        await self.inner(scope, receive, send)

    async def _answer(
        self, entry: tuple[Any, Any], scope: Scope, receive: Receive, send: Send
    ) -> None:
        handler, route = entry
        scope.setdefault("router", self.router)
        scope.update({"endpoint": handler, "path_params": {}, "route": route})
        value = await handler()
        if isinstance(value, Response):
            await value(scope, receive, send)
            return
        await _send_json(_encode(value), send)


def install(router: APIRouter) -> bool:
    """Wrap the router's stack. Returns False when this Starlette has no such stack."""
    inner = getattr(router, "middleware_stack", None)
    if inner is None:
        return False
    router.middleware_stack = FastPath(router, inner)
    return True
