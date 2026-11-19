"""/sitemap.xml and /robots.txt, written from the routes of the application (#84)."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeGuard

from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
from starlette.routing import BaseRoute


def _is_page(route: BaseRoute) -> TypeGuard[APIRoute]:
    """A GET route that answers HTML on a fixed path and is not hidden from the schema."""
    if not isinstance(route, APIRoute) or "GET" not in (route.methods or ()):
        return False
    answers_html = isinstance(route.response_class, type) and issubclass(
        route.response_class, HTMLResponse
    )
    return answers_html and route.include_in_schema and "{" not in route.path


def page_paths(routes: Iterable[BaseRoute]) -> list[str]:
    """The paths of the static pages, sorted, each once."""
    return sorted({route.path for route in routes if _is_page(route)})
