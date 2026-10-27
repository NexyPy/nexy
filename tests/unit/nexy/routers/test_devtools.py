"""The dev toolbar: injected with what the server knows, never into production, easy to turn off."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.testclient import TestClient

from nexy.helpers.server import devtools
from nexy.helpers.server.devtools import DevToolsMiddleware, source_of, toolbar_markup
from nexy.helpers.server.devtools.state import RECENT, config_of, record_error, routes_of
from nexy.helpers.server.proxy import DEV_ENV_VAR


def _app() -> FastAPI:
    app = FastAPI()

    @app.get("/page", response_class=HTMLResponse)
    async def page() -> str:
        return "<html><body><h1>hi</h1></body></html>"

    @app.get("/data")
    async def data() -> JSONResponse:
        return JSONResponse({"ok": True})

    @app.get("/_nexy/devtools/state", response_class=HTMLResponse)
    async def internal() -> str:
        return "<html><body>internal</body></html>"

    app.add_middleware(DevToolsMiddleware, version="9.9.9")
    return app


def _data(html: str) -> dict:
    match = re.search(r'id="nexy-devtools-data">(.*?)</script>', html, re.S)
    assert match
    return json.loads(match.group(1))


class TestMarkup:
    def test_the_page_data_is_json_in_the_page(self):
        assert _data(toolbar_markup("1.0", {"path": "/x"}).decode())["path"] == "/x"

    def test_the_version_is_in_the_data(self):
        assert _data(toolbar_markup("1.2.3", {}).decode())["version"] == "1.2.3"

    def test_data_cannot_close_the_script_element(self):
        markup = toolbar_markup("1", {"path": "/</script><b>"}).decode()
        assert markup.count("</script>") == 2

    def test_the_style_does_not_apply_to_the_page(self):
        assert 'id="nexy-devtools-css" media="not all"' in toolbar_markup("1", {}).decode()


class TestMiddleware:
    def test_an_html_page_gets_the_toolbar(self):
        assert "nexy-devtools-data" in TestClient(_app()).get("/page").text

    def test_it_is_placed_before_the_end_of_the_body(self):
        text = TestClient(_app()).get("/page").text
        assert text.index("nexy-devtools-data") < text.index("</body>")

    def test_the_route_that_answered_is_in_the_data(self):
        data = _data(TestClient(_app()).get("/page").text)
        assert (data["route"], data["name"], data["status"]) == ("/page", "page", 200)

    def test_the_server_time_is_measured(self):
        assert _data(TestClient(_app()).get("/page").text)["ms"] >= 0

    def test_json_is_left_alone(self):
        assert TestClient(_app()).get("/data").json() == {"ok": True}

    def test_its_own_endpoints_are_left_alone(self):
        assert "nexy-devtools-data" not in TestClient(_app()).get("/_nexy/devtools/state").text

    def test_a_page_is_given_the_toolbar_once(self):
        assert TestClient(_app()).get("/page").text.count('id="nexy-devtools-data"') == 1


class TestState:
    def test_routes_leave_out_the_internal_ones(self):
        paths = [route["path"] for route in routes_of(_app())]
        assert "/page" in paths and not any(path.startswith("/_nexy") for path in paths)

    def test_methods_leave_out_head_and_options(self):
        methods = {r["path"]: r["methods"] for r in routes_of(_app())}
        assert methods["/page"] == ["GET"]

    def test_config_has_plain_values_only(self):
        fake = SimpleNamespace(useCSR=True, useFF=object())
        values = config_of(fake)
        assert values["useCSR"] is True and values["useFF"] == "object"

    def test_recorded_errors_come_newest_first(self):
        RECENT.clear()
        record_error("A", "first", "GET /a", "r1")
        record_error("B", "second", "GET /b", "r2")
        assert [e["kind"] for e in RECENT] == ["B", "A"]

    def test_only_twenty_errors_are_kept(self):
        RECENT.clear()
        for number in range(30):
            record_error("E", str(number), "", "")
        assert len(RECENT) == 20


class TestMounting:
    @staticmethod
    def _paths():
        from nexy.modules.routers.app import AppServer

        return {getattr(route, "path", "") for route in AppServer().run().routes}

    def test_development_mounts_the_state_endpoint(self, nexy_project, monkeypatch):
        monkeypatch.setenv(DEV_ENV_VAR, "1")
        nexy_project("")
        assert devtools.STATE_PATH in self._paths()

    def test_production_does_not(self, nexy_project, monkeypatch):
        monkeypatch.delenv(DEV_ENV_VAR, raising=False)
        nexy_project("")
        assert devtools.STATE_PATH not in self._paths()

    def test_the_config_can_turn_it_off(self, nexy_project, monkeypatch):
        monkeypatch.setenv(DEV_ENV_VAR, "1")
        nexy_project("useDevTools = False")
        assert devtools.STATE_PATH not in self._paths()


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_the_toolbar_script_is_valid_javascript():
    script = Path(devtools.__file__).parent / "toolbar.js"
    done = subprocess.run(["node", "--check", str(script)], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr


class TestCrashPage:
    @staticmethod
    def _crash(monkeypatch, dev: bool):
        import asyncio

        from starlette.requests import Request

        from nexy.modules.routers.crash import handle_crash

        if dev:
            monkeypatch.setenv(DEV_ENV_VAR, "1")
        else:
            monkeypatch.delenv(DEV_ENV_VAR, raising=False)
        RECENT.clear()
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/boom",
            "headers": [],
            "query_string": b"",
        }
        try:
            raise ValueError("kaput")
        except ValueError as error:
            return asyncio.run(handle_crash(Request(scope), error))

    def test_development_answers_with_the_overlay_page(self, monkeypatch):
        body = self._crash(monkeypatch, True).body.decode()
        assert "Server Error" in body and "ValueError: kaput" in body

    def test_development_remembers_the_error_for_the_toolbar(self, monkeypatch):
        self._crash(monkeypatch, True)
        assert [e["message"] for e in RECENT] == ["kaput"]

    def test_production_remembers_nothing(self, monkeypatch):
        self._crash(monkeypatch, False)
        assert list(RECENT) == []


class TestSource:
    def test_a_handler_that_knows_its_file_is_reported_with_both_paths(self):
        def handler() -> None: ...

        handler.__nexy_source__ = "src/routes/about.nexy"
        found = source_of(SimpleNamespace(endpoint=handler))
        assert found["source"] == "src/routes/about.nexy"
        assert found["file"].endswith("src/routes/about.nexy") and Path(found["file"]).is_absolute()

    def test_a_route_without_a_file_reports_none(self):
        assert source_of(SimpleNamespace(endpoint=lambda: None)) == {"source": None, "file": None}

    def test_a_route_without_an_endpoint_reports_none(self):
        assert source_of(object()) == {"source": None, "file": None}

    def test_the_page_data_carries_the_source(self):
        app = FastAPI()

        @app.get("/page", response_class=HTMLResponse)
        async def page() -> str:
            return "<html><body></body></html>"

        page.__nexy_source__ = "src/routes/page.nexy"
        app.add_middleware(DevToolsMiddleware, version="1")
        assert _data(TestClient(app).get("/page").text)["source"] == "src/routes/page.nexy"

    def test_the_routes_list_carries_the_source(self):
        app = FastAPI()

        @app.get("/page")
        async def page() -> dict[str, bool]:
            return {}

        page.__nexy_source__ = "src/routes/page.nexy"
        assert routes_of(app)[-1]["source"] == "src/routes/page.nexy"


class TestToolbarAssets:
    @staticmethod
    def _asset(name: str) -> str:
        return (Path(devtools.__file__).parent / name).read_text(encoding="utf-8")

    def test_it_starts_in_the_bottom_left_corner(self):
        assert "position: 'bottom-left'" in self._asset("toolbar.js")

    def test_every_corner_has_a_place(self):
        css = self._asset("toolbar.css")
        assert all(
            f'data-pos="{corner}"' in css
            for corner in ("top-left", "top-right", "bottom-left", "bottom-right")
        )

    def test_it_can_be_dragged_and_snaps_to_a_corner(self):
        script = self._asset("toolbar.js")
        assert "pointermove" in script and "snap" in script and "setPointerCapture" in script

    def test_the_badge_holds_the_nexy_mark(self):
        assert "M12.5527 0.5459" in self._asset("toolbar.js")

    def test_the_badge_is_a_circle(self):
        css = self._asset("toolbar.css")
        assert re.search(r"\.logo \{[^}]*border-radius: 50%", css)

    def test_the_badge_does_not_draw_a_letter(self):
        assert "'N')" not in self._asset("toolbar.js")

    def test_preferences_are_remembered(self):
        assert "localStorage.setItem(STORE" in self._asset("toolbar.js")

    def test_motion_is_switched_off_for_people_who_ask(self):
        assert "prefers-reduced-motion: no-preference" in self._asset("toolbar.css")


class TestToolbarColours:
    def test_it_follows_the_page_by_default(self):
        assert "theme: 'system'" in TestToolbarAssets._asset("toolbar.js")

    def test_it_does_not_wear_the_green_of_the_app(self):
        css = TestToolbarAssets._asset("toolbar.css").lower()
        assert not any(green in css for green in ("#062b24", "#0a3a30", "#14503f", "#2ee6a6"))
