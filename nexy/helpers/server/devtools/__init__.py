"""The development toolbar of `nexy dev`: injected into every HTML page, off with `useDevTools`.

It shows the page (route, handler, timings), the routes of the app, the errors since the server
started (and the ones the browser raises, in a dialog) and the configuration in use. It is
self-contained: one style block and one script, no external request.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from starlette.types import ASGIApp, Receive, Scope, Send

from nexy.helpers.server.html_inject import InjectMiddleware

MARKER = b'id="nexy-devtools-data"'
STATE_PATH = "/_nexy/devtools/state"
_STARTED = "nexy.devtools.started"
_ASSETS = Path(__file__).parent

__all__ = ["MARKER", "STATE_PATH", "DevToolsMiddleware", "toolbar_markup"]


def _asset(name: str) -> str:
    return (_ASSETS / name).read_text(encoding="utf-8")


def _script_safe(data: dict[str, object]) -> str:
    """JSON that cannot close the script element it sits in."""
    return json.dumps(data).replace("<", "\\u003c")


def toolbar_markup(version: str, page: dict[str, object]) -> bytes:
    """The toolbar for one page: its data, its style (inert) and its script."""
    data = {"version": version, **page}
    return (
        f'<script type="application/json" id="nexy-devtools-data">{_script_safe(data)}</script>'
        f'<style id="nexy-devtools-css" media="not all">{_asset("toolbar.css")}</style>'
        f"<script>{_asset('toolbar.js')}</script>"
    ).encode()


def source_of(route: object) -> dict[str, str | None]:
    """Where the route's handler lives: the path as written, and the absolute one for an editor."""
    source = getattr(getattr(route, "endpoint", None), "__nexy_source__", None)
    if not source:
        return {"source": None, "file": None}
    return {"source": Path(source).as_posix(), "file": Path(source).resolve().as_posix()}


def _page(scope: Scope, status: int) -> dict[str, object]:
    route = scope.get("route")
    started = scope.get(_STARTED, time.perf_counter())
    return {
        "path": scope.get("path", ""),
        "route": getattr(route, "path", None),
        "name": getattr(route, "name", None),
        "status": status,
        "ms": round((time.perf_counter() - started) * 1000, 1),
        **source_of(route),
    }


class DevToolsMiddleware(InjectMiddleware):
    """Adds the toolbar to HTML responses, with what the server knew about the request."""

    def __init__(self, app: ASGIApp, version: str) -> None:
        def markup(scope: Scope, status: int) -> bytes:
            return toolbar_markup(version, _page(scope, status))

        super().__init__(app, markup, MARKER)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["path"].startswith("/_nexy/"):
            await self.app(scope, receive, send)
            return
        scope[_STARTED] = time.perf_counter()
        await super().__call__(scope, receive, send)
