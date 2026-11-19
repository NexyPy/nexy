"""/sitemap.xml and /robots.txt, written from the routes once `useSiteUrl` is set (#84)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from nexy.modules.routers.sitemap import page_paths


def _page() -> str:
    return "<p>page</p>"


def _app(*paths: str, **options) -> FastAPI:
    app = FastAPI()
    for path in paths:
        app.get(path, **{"response_class": HTMLResponse, **options})(_page)
    return app


class TestPagePaths:
    def test_a_static_page_is_listed(self):
        assert page_paths(_app("/", "/about").routes) == ["/", "/about"]

    def test_a_dynamic_page_is_left_out(self):
        assert page_paths(_app("/users/{id}").routes) == []

    def test_an_api_route_is_left_out(self):
        assert page_paths(_app("/api/users", response_class=JSONResponse).routes) == []

    def test_a_route_hidden_from_the_schema_is_left_out(self):
        assert page_paths(_app("/docs", include_in_schema=False).routes) == []

    def test_the_paths_are_sorted_once_each(self):
        assert page_paths(_app("/b", "/a", "/b").routes) == ["/a", "/b"]
