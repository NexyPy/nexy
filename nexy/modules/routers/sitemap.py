"""/sitemap.xml and /robots.txt, written from the routes of the application (#84)."""

from __future__ import annotations

from collections.abc import Iterable
from html import escape
from typing import TypeGuard

from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
from starlette.routing import BaseRoute

SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"


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


def sitemap_xml(site_url: str, paths: Iterable[str]) -> str:
    """A sitemap that gives each path as an absolute URL on *site_url*."""
    origin = site_url.rstrip("/")
    urls = "".join(f"<url><loc>{escape(origin + path, quote=False)}</loc></url>" for path in paths)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="{SITEMAP_NAMESPACE}">{urls}</urlset>\n'
    )


def robots_txt(site_url: str) -> str:
    """Every crawler may read every page; the sitemap tells them which pages there are."""
    return f"User-agent: *\nAllow: /\n\nSitemap: {site_url.rstrip('/')}/sitemap.xml\n"
