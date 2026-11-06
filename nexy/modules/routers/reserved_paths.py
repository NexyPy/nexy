"""A route on the path of the API reference, or of its OpenAPI schema, is never served (#81).

FastAPI answers a path with the first route registered for it, and the reference is registered
before the project's routes, so a page at ``/docs`` stays silent. This module names those routes.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from fastapi.routing import APIRoute
from starlette.routing import BaseRoute, Match

SCHEMA_URL = "/openapi.json"
_REFERENCE_FIX = "Move the reference with useDocsUrl, or set useDocs = False, in nexyconfig.py."
_SCHEMA_FIX = "Give the route another path."


def _claims(route: APIRoute, path: str) -> bool:
    """*route* answers *path*, or ``path/``, where Starlette would redirect *path* without one."""
    for candidate in {path, path.rstrip("/") + "/"}:
        scope = {"type": "http", "path": candidate, "root_path": "", "method": "GET"}
        if route.matches(scope)[0] is not Match.NONE:
            return True
    return False


def _owner(route: APIRoute) -> str:
    source = getattr(route.endpoint, "__nexy_source__", None)
    return str(source) if source else f"GET {route.path}"


def _reserved(docs_url: str | None) -> list[tuple[str, str, str]]:
    """``(path, what answers there, how to free it)`` for each path Nexy keeps."""
    schema = (SCHEMA_URL, "the OpenAPI schema", _SCHEMA_FIX)
    if not docs_url:
        return [schema]
    return [(docs_url, "the API reference", _REFERENCE_FIX), schema]


def shadowed_routes(
    routes: Iterable[BaseRoute], docs_url: str | None, reference: Callable[..., Any]
) -> list[str]:
    """One warning per project route that a path of the API reference hides."""
    own = [r for r in routes if isinstance(r, APIRoute) and r.endpoint != reference]
    return [
        f"{_owner(route)} is never served at {path}: {what} answers there. {fix}"
        for path, what, fix in _reserved(docs_url)
        for route in own
        if _claims(route, path)
    ]
