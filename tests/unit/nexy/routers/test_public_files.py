"""Files in `public/` are served at the root, like Vite and Next.js."""

from __future__ import annotations

import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import FileResponse

from nexy.modules.routers.static_assets import PublicFilesMiddleware


@pytest.fixture
def client(tmp_path):
    public = tmp_path / "public"
    (public / "img").mkdir(parents=True)
    (public / "logo.svg").write_text("<svg/>")
    (public / "img" / "a.png").write_bytes(b"png")
    (public / ".secret").write_text("hidden")
    (public / "page").mkdir()
    (tmp_path / "outside.txt").write_text("outside")

    app = FastAPI()

    @app.get("/page")
    def page() -> str:
        return "route"

    @app.get("/logo.svg/extra")
    def extra() -> str:
        return "route"

    app.add_middleware(PublicFilesMiddleware, directory=public)
    return TestClient(app)


def test_a_public_file_is_served_at_the_root(client):
    response = client.get("/logo.svg")
    assert (response.status_code, response.text) == (200, "<svg/>")
    assert response.headers["content-type"].startswith("image/svg+xml")


def test_a_nested_file_keeps_its_folder(client):
    assert client.get("/img/a.png").content == b"png"


def test_head_is_served_too(client):
    assert client.head("/logo.svg").status_code == 200


def test_a_missing_file_is_left_to_the_application(client):
    assert client.get("/missing.svg").status_code == 404


def test_routes_without_an_extension_are_untouched(client):
    assert client.get("/page").text == '"route"'


def test_a_directory_is_not_a_file(client):
    assert client.get("/img.png").status_code == 404


def test_dot_files_are_never_served(client):
    assert client.get("/.secret").status_code == 404


def test_other_methods_go_to_the_application(client):
    assert "<svg/>" not in client.post("/logo.svg").text


@pytest.mark.parametrize(
    "path", ["/../outside.txt", "/img/../../outside.txt", "/%2e%2e/outside.txt"]
)
def test_a_path_cannot_leave_the_public_folder(client, path):
    response = client.get(path)
    assert "outside" not in response.text


def test_a_file_changed_on_disk_is_served_fresh(client, tmp_path):
    client.get("/logo.svg")
    (tmp_path / "public" / "logo.svg").write_text("<svg id='new'/>")
    os.utime(tmp_path / "public" / "logo.svg", ns=(1, 2_000_000_000))
    assert client.get("/logo.svg").text == "<svg id='new'/>"


def test_a_deleted_file_is_no_longer_served(client, tmp_path):
    client.get("/logo.svg")
    (tmp_path / "public" / "logo.svg").unlink()
    assert client.get("/logo.svg").status_code == 404


def test_a_range_request_gets_the_bytes_it_asks_for(client):
    response = client.get("/logo.svg", headers={"range": "bytes=0-1"})
    assert (response.status_code, response.content) == (206, b"<s")


def test_the_headers_are_those_of_a_file_response(client, tmp_path):
    path = tmp_path / "public" / "logo.svg"
    expected = FileResponse(path, stat_result=path.stat()).headers
    headers = client.get("/logo.svg").headers
    assert [headers[name] for name in ("etag", "last-modified", "content-length")] == [
        expected[name] for name in ("etag", "last-modified", "content-length")
    ]


def test_head_sends_no_body(client):
    response = client.head("/logo.svg")
    assert (response.content, response.headers["content-length"]) == (b"", "6")


def test_a_public_file_is_served_under_public_too(client):
    assert client.get("/public/logo.svg").text == "<svg/>"


def test_a_file_removed_after_it_was_found_is_left_to_the_application(client, monkeypatch):
    from pathlib import Path

    def gone(self, *_args, **_kwargs):
        raise FileNotFoundError(self)

    monkeypatch.setattr(Path, "stat", gone)
    monkeypatch.setattr(PublicFilesMiddleware, "_file_for", lambda _self, _path: Path("x.svg"))
    assert client.get("/x.svg").status_code == 404
