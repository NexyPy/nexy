"""Registering route modules on a router: what becomes an endpoint, in which order."""

# ruff: noqa: N802  (route modules name their handlers GET, POST, SOCKET)

from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from nexy.modules.routers.fbrouter.registrar import RouteRegistrar
from nexy.modules.routers.fbrouter.scanner import RouteModule
from nexy.modules.runtime.cache import REVALIDATE_CACHE


@pytest.fixture(autouse=True)
def _forget_module():
    yield
    sys.modules.pop("route_under_test", None)


def _module(**attributes: Any) -> ModuleType:
    """A route module, importable by name as pages are when they are requested."""
    module = ModuleType("route_under_test")
    for name, value in attributes.items():
        setattr(module, name, value)
    sys.modules["route_under_test"] = module
    return module


def _route(module: ModuleType, pathname: str, kind: str = "api", **extra: str) -> RouteModule:
    return RouteModule(
        module=module,
        type=kind,
        pathname=pathname,
        comp_name=extra.get("comp_name", "Page"),
        import_path=extra.get("import_path", "route_under_test"),
        source=extra.get("source", "src/routes/none.py"),
    )


def _register(*routes: RouteModule) -> APIRouter:
    router = APIRouter()
    RouteRegistrar(router).register(list(routes))
    return router


def _paths(router: APIRouter) -> list[str]:
    return [getattr(route, "path", "") for route in router.routes]


async def _hello() -> dict[str, str]:
    return {"hello": "world"}


class TestApiRoutes:
    def test_each_http_method_function_becomes_an_endpoint(self):
        async def GET() -> dict[str, bool]:
            return {"ok": True}

        async def POST() -> dict[str, bool]:
            return {"ok": False}

        router = _register(_route(_module(GET=GET, POST=POST), "/things"))
        methods = {tuple(sorted(route.methods)) for route in router.routes}
        assert methods == {("GET",), ("POST",)}

    def test_the_endpoint_answers(self):
        app = FastAPI()
        app.include_router(_register(_route(_module(GET=_hello), "/hello")))
        assert TestClient(app).get("/hello").json() == {"hello": "world"}

    def test_a_module_without_handlers_registers_nothing(self):
        assert _register(_route(_module(), "/empty")).routes == []

    def test_a_socket_handler_becomes_a_websocket_route(self):
        async def SOCKET(websocket: Any) -> None:
            await websocket.accept()
            await websocket.close()

        router = _register(_route(_module(SOCKET=SOCKET), "/live"))
        assert [type(route).__name__ for route in router.routes] == ["APIWebSocketRoute"]

    def test_the_response_status_comes_from_the_handler_metadata(self):
        async def POST() -> dict[str, bool]:
            return {"created": True}

        POST.__nexy_response_meta__ = SimpleNamespace(status_code=201)  # type: ignore[attr-defined]
        app = FastAPI()
        app.include_router(_register(_route(_module(POST=POST), "/made")))
        assert TestClient(app).post("/made").status_code == 201

    def test_a_handler_that_lacks_a_path_parameter_is_refused(self):
        async def GET() -> dict[str, str]:
            return {}

        with pytest.raises(RuntimeError, match="missing parameters: id"):
            _register(_route(_module(GET=GET), "/items/{id}"))


class TestPages:
    def test_a_page_is_served_as_html(self):
        def Page() -> str:
            return "<h1>hi</h1>"

        app = FastAPI()
        app.include_router(_register(_route(_module(Page=Page), "/", kind="page")))
        response = TestClient(app).get("/")
        assert response.text == "<h1>hi</h1>" and "text/html" in response.headers["content-type"]

    def test_a_page_without_its_component_is_skipped_with_a_warning(self, capsys):
        router = _register(_route(_module(), "/ghost", kind="page", source="src/ghost.nexy"))
        assert router.routes == [] and "Route '/ghost' skipped" in capsys.readouterr().out

    @staticmethod
    def _renders_after_two_requests(**module_attributes: Any) -> int:
        renders: list[int] = []

        def Page() -> str:
            renders.append(1)
            return "<p>page</p>"

        REVALIDATE_CACHE.clear()
        app = FastAPI()
        module = _module(Page=Page, **module_attributes)
        app.include_router(_register(_route(module, "/news", kind="page")))
        client = TestClient(app)
        client.get("/news")
        client.get("/news")
        return len(renders)

    def test_a_revalidating_page_is_rendered_once_inside_its_window(self):
        assert self._renders_after_two_requests(revalidate=60) == 1

    def test_a_plain_page_is_rendered_every_time(self):
        assert self._renders_after_two_requests() == 2

    def test_the_component_docstring_describes_the_route(self):
        def Page() -> str:
            """The home page."""
            return ""

        router = _register(_route(_module(Page=Page), "/", kind="page"))
        assert router.routes[0].description == "The home page."


class TestOrder:
    def test_static_paths_come_before_dynamic_ones(self):
        async def GET(slug: str) -> dict[str, str]:
            return {"slug": slug}

        dynamic = _route(_module(GET=GET), "/{slug}")
        static = _route(_module(GET=_hello), "/about")
        assert _paths(_register(dynamic, static)) == ["/about", "/{slug}"]

    def test_catch_all_paths_come_last(self):
        async def GET(rest: str) -> dict[str, str]:
            return {"rest": rest}

        async def get_one(slug: str) -> dict[str, str]:
            return {"slug": slug}

        catch = _route(_module(GET=GET), "/{rest:path}")
        one = _route(_module(GET=get_one), "/{slug}")
        assert _paths(_register(catch, one)) == ["/{slug}", "/{rest:path}"]
