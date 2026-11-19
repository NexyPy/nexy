"""/sitemap.xml and /robots.txt, written from the routes once `useSiteUrl` is set (#84)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from nexy.modules.routers.sitemap import page_paths, robots_txt, sitemap_xml


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
