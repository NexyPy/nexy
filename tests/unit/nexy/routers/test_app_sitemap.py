"""`useSiteUrl` serves /sitemap.xml and /robots.txt on the assembled application (#84)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def _client(nexy_project, attrs: str = 'useSiteUrl = "https://example.com"') -> TestClient:
    from nexy.modules.routers.app import AppServer

    nexy_project(attrs)
    routes = Path("src/routes")
    (routes / "api").mkdir(parents=True)
    (routes / "about.nexy").write_text("<p>About</p>\n", encoding="utf-8")
    (routes / "api" / "users.py").write_text("def GET():\n    return []\n", encoding="utf-8")
    return TestClient(AppServer().run(), raise_server_exceptions=False)


def test_the_sitemap_lists_a_page_of_the_project(nexy_project):
    assert "<loc>https://example.com/about</loc>" in _client(nexy_project).get("/sitemap.xml").text


def test_the_sitemap_leaves_an_api_route_out(nexy_project):
    assert "/api/users" not in _client(nexy_project).get("/sitemap.xml").text


def test_robots_txt_points_to_the_sitemap(nexy_project):
    robots = _client(nexy_project).get("/robots.txt").text
    assert "Sitemap: https://example.com/sitemap.xml" in robots


def test_nothing_is_served_without_a_site_url(nexy_project):
    assert _client(nexy_project, "").get("/sitemap.xml").status_code == 404


def test_a_file_in_public_wins(nexy_project):
    Path("public").mkdir()
    Path("public/robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    assert "Disallow: /" in _client(nexy_project).get("/robots.txt").text
