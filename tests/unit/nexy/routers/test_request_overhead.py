"""Per-request cost: flat file routes, no idle telemetry, no template re-checks in production."""

from fastapi import APIRouter, FastAPI

from nexy.modules.routers.app import _telemetry_options
from nexy.modules.routers.fbrouter import FBRouter


class TestFlatRoutes:
    @staticmethod
    def _fb(router) -> FBRouter:
        fb = FBRouter.__new__(FBRouter)
        fb.router = router
        fb._flat = router is not None
        fb._register_error_handlers = lambda _app: None  # type: ignore[method-assign]
        return fb

    def test_routes_on_the_app_router_are_not_included_again(self):
        app = FastAPI()

        @app.get("/ping")
        async def ping() -> dict:
            return {}

        before = list(app.router.routes)
        self._fb(app.router).register_on(app)
        assert app.router.routes == before

    def test_a_standalone_router_is_included(self):
        app = FastAPI()
        router = APIRouter()

        @router.get("/x")
        async def x() -> dict:
            return {}

        fb = self._fb(None)
        fb.router = router
        fb._flat = False
        before = len(app.router.routes)
        fb.register_on(app)
        assert len(app.router.routes) > before


class TestTelemetryOptions:
    def test_disabled_without_the_sdk(self, monkeypatch):
        import importlib.util

        monkeypatch.setattr(importlib.util, "find_spec", lambda _name: None)
        monkeypatch.delenv("FASTAPI_OTEL_AUTO_CONFIGURE", raising=False)
        options = _telemetry_options()
        if "telemetry" in options:
            assert options["telemetry"]["tracing"] is False

    def test_kept_when_the_sdk_is_installed(self, monkeypatch):
        import importlib.util

        monkeypatch.setattr(importlib.util, "find_spec", lambda _name: object())
        assert _telemetry_options() == {}

    def test_kept_when_auto_configure_is_requested(self, monkeypatch):
        import importlib.util

        monkeypatch.setattr(importlib.util, "find_spec", lambda _name: None)
        monkeypatch.setenv("FASTAPI_OTEL_AUTO_CONFIGURE", "true")
        assert _telemetry_options() == {}


class TestTemplateReload:
    def test_production_build_does_not_recheck_templates(self, tmp_path, monkeypatch):
        import nexy.template as template

        monkeypatch.chdir(tmp_path)
        (tmp_path / "__nexy__").mkdir()
        (tmp_path / "__nexy__" / "nexy.prod").write_text("", encoding="utf-8")
        monkeypatch.setattr(template, "_SHARED_ENV", None)
        assert template._get_shared_env().auto_reload is False

    def test_development_keeps_hot_reload(self, tmp_path, monkeypatch):
        import nexy.template as template

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(template, "_SHARED_ENV", None)
        assert template._get_shared_env().auto_reload is True
