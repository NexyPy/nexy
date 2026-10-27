"""/favicon.ico: the project's file when there is one, else a built-in SVG with the right type."""

import inspect

from fastapi import FastAPI
from fastapi.testclient import TestClient

from nexy.modules.routers.static_assets import setup_favicon


def _client(router_path: str) -> TestClient:
    app = FastAPI()
    setup_favicon(app, router_path)
    return TestClient(app)


def test_serves_the_project_favicon(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src" / "routes").mkdir(parents=True)
    (tmp_path / "src" / "routes" / "favicon.ico").write_bytes(b"ICO-ROUTES")
    response = _client("src/routes").get("/favicon.ico")
    assert response.content == b"ICO-ROUTES"
    assert response.headers["content-type"] == "image/x-icon"


def test_falls_back_to_public(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "favicon.ico").write_bytes(b"ICO-PUBLIC")
    assert _client("src/routes").get("/favicon.ico").content == b"ICO-PUBLIC"


def test_built_in_icon_is_an_svg_with_the_svg_type(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    response = _client("src/routes").get("/favicon.ico")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/svg+xml"
    assert response.content.startswith(b"<svg")


def test_reading_the_file_does_not_block_the_event_loop():
    app = FastAPI()
    setup_favicon(app, "src/routes")
    route = next(r for r in app.routes if getattr(r, "path", "") == "/favicon.ico")
    assert not inspect.iscoroutinefunction(route.endpoint)
