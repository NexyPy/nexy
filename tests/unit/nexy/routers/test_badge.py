"""The "Built with Nexy" tag: added to HTML pages once, never to anything else, off on request."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.testclient import TestClient

from nexy.helpers.server.badge import BadgeMiddleware, badge_markup, inject

PAGE = "<html><body><h1>Hi</h1></body></html>"


def _client(version: str = "9.9.9") -> TestClient:
    app = FastAPI()
    app.add_middleware(BadgeMiddleware, version=version)

    @app.get("/page", response_class=HTMLResponse)
    def page() -> str:
        return PAGE

    @app.get("/fragment", response_class=HTMLResponse)
    def fragment() -> str:
        return "<p>no body tag</p>"

    @app.get("/json")
    def json() -> JSONResponse:
        return JSONResponse({"a": "</body>"})

    @app.get("/text")
    def text() -> PlainTextResponse:
        return PlainTextResponse("</body>")

    @app.get("/twice", response_class=HTMLResponse)
    def twice() -> str:
        return "<body>a</body><body>b</body>"

    @app.get("/stream")
    def stream() -> StreamingResponse:
        chunks = [b"<html><bo", b"dy>x</bo", b"dy></html>"]
        return StreamingResponse(iter(chunks), media_type="text/html")

    return TestClient(app)


class TestMarkup:
    def test_it_names_nexy_and_its_version(self):
        assert b"Built with Nexy 2.2.0" in badge_markup("2.2.0")

    def test_it_links_to_the_project(self):
        assert b'href="https://github.com/NexyPy/nexy"' in badge_markup("1")

    def test_it_needs_no_script(self):
        assert b"<script" not in badge_markup("1")


class TestInject:
    def test_the_tag_goes_before_the_closing_body(self):
        data, found = inject(b"<body>x</body>", b"[TAG]")
        assert (data, found) == (b"<body>x[TAG]</body>", True)

    def test_a_closing_tag_in_capitals_is_found(self):
        assert inject(b"<BODY>x</BODY>", b"[TAG]")[0] == b"<BODY>x[TAG]</BODY>"

    def test_only_the_last_closing_body_is_used(self):
        assert inject(b"</body></body>", b"[TAG]")[0] == b"</body>[TAG]</body>"

    def test_without_a_closing_body_nothing_changes(self):
        assert inject(b"<p>x</p>", b"[TAG]") == (b"<p>x</p>", False)


class TestMiddleware:
    def test_an_html_page_gets_the_tag(self):
        assert "Built with Nexy 9.9.9" in _client().get("/page").text

    def test_the_page_is_otherwise_unchanged(self):
        text = _client().get("/page").text
        assert text.startswith("<html><body><h1>Hi</h1>") and text.endswith("</body></html>")

    def test_the_tag_is_inside_the_body(self):
        text = _client().get("/page").text
        assert text.index("nexy-badge") < text.index("</body>")

    def test_the_stale_length_header_is_dropped(self):
        assert "content-length" not in _client().get("/page").headers

    def test_a_fragment_without_a_body_is_left_alone(self):
        assert "nexy-badge" not in _client().get("/fragment").text

    def test_json_is_left_alone(self):
        assert _client().get("/json").json() == {"a": "</body>"}

    def test_plain_text_is_left_alone(self):
        assert _client().get("/text").text == "</body>"

    def test_a_closing_tag_split_between_two_chunks_is_still_found(self):
        text = _client().get("/stream").text
        assert text.count('id="nexy-badge"') == 1 and text.endswith("</body></html>")

    def test_the_tag_is_added_once(self):
        assert _client().get("/twice").text.count('id="nexy-badge"') == 1

    def test_a_page_that_has_the_tag_does_not_get_a_second(self):
        app = FastAPI()
        app.add_middleware(BadgeMiddleware, version="1")

        @app.get("/", response_class=HTMLResponse)
        def home() -> str:
            return '<body><a id="nexy-badge">mine</a></body>'

        assert TestClient(app).get("/").text.count('id="nexy-badge"') == 1

    def test_a_compressed_response_is_left_alone(self):
        app = FastAPI()
        app.add_middleware(BadgeMiddleware, version="1")

        @app.get("/")
        def home() -> HTMLResponse:
            return HTMLResponse("<body></body>", headers={"content-encoding": "identity"})

        assert (
            b"nexy-badge" not in TestClient(app).get("/", headers={"accept-encoding": ""}).content
        )

    def test_a_websocket_passes_through(self):
        seen: list[str] = []

        async def inner(scope: Any, receive: Any, send: Any) -> None:  # noqa: ARG001
            seen.append(scope["type"])

        asyncio.run(BadgeMiddleware(inner, "1")({"type": "websocket"}, None, None))
        assert seen == ["websocket"]


class TestOption:
    @pytest.fixture
    def project(self, nexy_project, tmp_path):
        def make(setting: str):
            nexy_project(setting)
            (tmp_path / "src" / "routes").mkdir(parents=True)
            (tmp_path / "src" / "routes" / "index.nexy").write_text(
                "<html><body><p>hi</p></body></html>", encoding="utf-8"
            )
            from nexy.modules.routers.app import AppServer

            return TestClient(AppServer().run())

        return make

    def test_the_tag_is_on_by_default(self, project):
        assert "nexy-badge" in project("").get("/", headers={"accept": "text/html"}).text

    def test_it_can_be_turned_off_in_the_config(self, project):
        assert "nexy-badge" not in project("useBadge = False").get("/").text
