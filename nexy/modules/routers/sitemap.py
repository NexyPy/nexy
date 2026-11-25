"""/sitemap.xml and /robots.txt, written from the routes of the application (#84)."""

from __future__ import annotations

from collections.abc import Iterable
from html import escape
from typing import TypeGuard

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.routing import APIRoute
from starlette.routing import BaseRoute

from nexy.core.config import Config
from nexy.modules.routers.base_path import normalize_base_path

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


def _taken(server: FastAPI, path: str) -> bool:
    return any(getattr(route, "path", None) == path for route in server.routes)


def setup_sitemap(server: FastAPI, site_url: str) -> None:
    """Serve /sitemap.xml and /robots.txt, unless the project already answers them.

    The sitemap reads the routes on each request, so it lists every page the application has.
    A file in `public/` is served before any route, so it wins too.
    """
    base = normalize_base_path(Config().useBasePath)
    if not _taken(server, "/sitemap.xml"):

        @server.get("/sitemap.xml", include_in_schema=False)
        def sitemap() -> Response:
            paths = [base + path for path in page_paths(server.routes)]
            return Response(sitemap_xml(site_url, paths), media_type="application/xml")

    if not _taken(server, "/robots.txt"):

        @server.get("/robots.txt", include_in_schema=False)
        def robots() -> Response:
            return PlainTextResponse(robots_txt(site_url + base))
