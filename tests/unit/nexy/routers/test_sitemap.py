"""/sitemap.xml and /robots.txt, written from the routes once `useSiteUrl` is set (#84)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.testclient import TestClient

from nexy.modules.routers.sitemap import page_paths, robots_txt, setup_sitemap, sitemap_xml


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


class TestSitemapXml:
    def test_each_path_is_an_absolute_url(self):
        xml = sitemap_xml("https://example.com", ["/", "/about"])
        assert "<loc>https://example.com/about</loc>" in xml

    def test_a_trailing_slash_of_the_site_url_is_not_doubled(self):
        assert "<loc>https://example.com/about</loc>" in sitemap_xml(
            "https://example.com/", ["/about"]
        )

    def test_a_url_is_escaped(self):
        assert "<loc>https://example.com/a&amp;b</loc>" in sitemap_xml(
            "https://example.com", ["/a&b"]
        )

    def test_it_declares_the_sitemap_namespace(self):
        xml = sitemap_xml("https://example.com", [])
        assert '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' in xml


class TestRobotsTxt:
    def test_it_points_to_the_sitemap(self):
        assert "Sitemap: https://example.com/sitemap.xml" in robots_txt("https://example.com/")

    def test_it_lets_every_crawler_in(self):
        assert robots_txt("https://example.com").startswith("User-agent: *\nAllow: /\n")


def _served(app: FastAPI, path: str):
    setup_sitemap(app, "https://example.com")
    return TestClient(app).get(path)


class TestSetupSitemap:
    def test_the_sitemap_lists_the_pages(self):
        assert (
            "<loc>https://example.com/about</loc>" in _served(_app("/about"), "/sitemap.xml").text
        )

    def test_the_sitemap_is_xml(self):
        assert _served(_app(), "/sitemap.xml").headers["content-type"] == "application/xml"

    def test_robots_txt_is_plain_text(self):
        robots = _served(_app(), "/robots.txt")
        assert robots.headers["content-type"] == "text/plain; charset=utf-8"

    def test_a_project_route_keeps_its_path(self):
        app = FastAPI()
        app.get("/robots.txt", response_class=PlainTextResponse)(lambda: "mine")
        assert _served(app, "/robots.txt").text == "mine"

    def test_a_project_sitemap_keeps_its_path(self):
        app = FastAPI()
        app.get("/sitemap.xml", response_class=PlainTextResponse)(lambda: "mine")
        assert _served(app, "/sitemap.xml").text == "mine"

    def test_the_two_files_are_not_in_the_schema(self):
        app = _app()
        setup_sitemap(app, "https://example.com")
        assert not [path for path in app.openapi()["paths"] if "." in path]

    def test_a_page_added_later_is_listed(self):
        app = _app()
        setup_sitemap(app, "https://example.com")
        app.get("/late", response_class=HTMLResponse)(_page)
        assert "/late</loc>" in TestClient(app).get("/sitemap.xml").text
