"""The fast path must be invisible: same status, headers and body as FastAPI's own dispatch."""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

import pytest
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel

from nexy.modules.routers.fastpath import FastPath, build_table, install


class Item(BaseModel):
    name: str


def _dep() -> None:
    return None


def _routes(router: APIRouter) -> None:
    @router.get("/dict")
    async def a_dict():
        return {"ok": True, "n": 1, "é": "ü"}

    @router.get("/list")
    async def a_list():
        return [1, "two", None, 3.5]

    @router.get("/none")
    async def nothing():
        return None

    @router.get("/str")
    async def text():
        return "hello"

    @router.get("/int")
    async def number():
        return 42

    @router.get("/response")
    async def raw_response():
        return PlainTextResponse("plain", status_code=202, headers={"x-test": "1"})

    @router.get("/html")
    async def html():
        return HTMLResponse("<p>x</p>")

    @router.get("/json-response")
    async def json_response():
        return JSONResponse({"a": 1}, status_code=201)

    @router.get("/dt")
    async def a_datetime():
        return {"at": dt.datetime(2026, 1, 2, 3, 4, 5, tzinfo=dt.UTC), "id": uuid.UUID(int=7)}

    @router.get("/model")
    async def a_model():
        return Item(name="ada")

    @router.get("/set")
    async def a_set():
        return {"tags": {"x"}}

    @router.get("/int-keys")
    async def int_keys():
        return {1: "a", 2: "b"}

    @router.get("/nan")
    async def nan():
        return {"v": float("nan")}

    @router.get("/forbidden")
    async def forbidden():
        raise HTTPException(status_code=403, detail="no")

    @router.get("/boom")
    async def boom():
        raise RuntimeError("boom")

    @router.get("/typed")
    async def typed() -> dict:
        return {"typed": True}

    @router.get("/model-typed")
    async def model_typed() -> Item:
        return Item(name="typed")

    @router.get("/status", status_code=201)
    async def created():
        return {"made": True}

    @router.get("/dep", dependencies=[Depends(_dep)])
    async def with_dependency():
        return {"dep": True}

    @router.get("/query")
    async def with_query(q: int = 1):
        return {"q": q}

    @router.get("/item/{item_id}")
    async def by_id(item_id: int):
        return {"id": item_id}

    @router.post("/post")
    async def posted():
        return {"posted": True}

    @router.get("/sync")
    def sync_handler():
        return {"sync": True}

    @router.get("/respmodel", response_model=Item)
    async def with_response_model():
        return {"name": "rm", "extra": 1}


PATHS = [
    "/dict",
    "/list",
    "/none",
    "/str",
    "/int",
    "/response",
    "/html",
    "/json-response",
    "/dt",
    "/model",
    "/set",
    "/int-keys",
    "/forbidden",
    "/typed",
    "/model-typed",
    "/status",
    "/dep",
    "/query",
    "/query?q=5",
    "/item/3",
    "/item/x",
    "/sync",
    "/respmodel",
    "/missing",
    "/dict/",
]


def _apps() -> tuple[TestClient, TestClient]:
    plain = FastAPI()
    _routes(plain.router)
    fast = FastAPI()
    _routes(fast.router)
    assert install(fast.router)
    return (
        TestClient(plain, raise_server_exceptions=False),
        TestClient(fast, raise_server_exceptions=False),
    )


def _snapshot(client: TestClient, method: str, path: str) -> tuple[Any, ...]:
    response = client.request(method, path, follow_redirects=False)
    headers = tuple(sorted((k, v) for k, v in response.headers.items() if k != "date"))
    return response.status_code, headers, response.content


@pytest.mark.parametrize("path", PATHS)
def test_get_is_identical_with_and_without_the_fast_path(path):
    plain, fast = _apps()
    assert _snapshot(fast, "GET", path) == _snapshot(plain, "GET", path)


@pytest.mark.parametrize("method", ["HEAD", "OPTIONS", "DELETE", "PUT", "POST"])
@pytest.mark.parametrize("path", ["/dict", "/post"])
def test_other_methods_are_identical(method, path):
    plain, fast = _apps()
    assert _snapshot(fast, method, path) == _snapshot(plain, method, path)


def test_nan_fails_the_same_way():
    plain, fast = _apps()
    assert _snapshot(fast, "GET", "/nan")[0] == _snapshot(plain, "GET", "/nan")[0] == 500


def test_unhandled_error_is_a_500_on_both_paths():
    plain, fast = _apps()
    assert _snapshot(fast, "GET", "/boom")[0] == _snapshot(plain, "GET", "/boom")[0] == 500


class TestEligibility:
    @staticmethod
    def _eligible() -> set[str]:
        router = APIRouter()
        _routes(router)
        return {path for (_method, path) in build_table(router)}

    def test_trivial_routes_are_served_directly(self):
        eligible = self._eligible()
        for path in ("/dict", "/list", "/none", "/str", "/int", "/response", "/dt", "/forbidden"):
            assert path in eligible

    def test_routes_with_work_for_fastapi_are_left_alone(self):
        eligible = self._eligible()
        for path in (
            "/typed",
            "/model-typed",
            "/status",
            "/dep",
            "/query",
            "/item/{item_id}",
            "/sync",
            "/respmodel",
        ):
            assert path not in eligible

    def test_only_the_registered_method_is_served(self):
        router = APIRouter()
        _routes(router)
        methods = {method for (method, path) in build_table(router) if path == "/post"}
        assert methods == {"POST"}


class TestShadowing:
    def test_an_earlier_dynamic_route_still_wins(self):
        for fast in (False, True):
            app = FastAPI()

            @app.get("/{anything}")
            async def catch(anything: str):
                return {"caught": anything}

            @app.get("/ping")
            async def ping():
                return {"ping": True}

            if fast:
                install(app.router)
            body = TestClient(app).get("/ping").json()
            assert body == {"caught": "ping"}

    def test_the_first_of_two_identical_routes_wins(self):
        app = FastAPI()

        @app.get("/same")
        async def first():
            return {"which": 1}

        @app.get("/same")
        async def second():
            return {"which": 2}

        install(app.router)
        assert TestClient(app).get("/same").json() == {"which": 1}


class TestLiveRouteChanges:
    def test_routes_added_after_install_are_picked_up(self):
        app = FastAPI()
        install(app.router)
        client = TestClient(app)
        assert client.get("/late").status_code == 404

        @app.get("/late")
        async def late():
            return {"late": True}

        assert client.get("/late").json() == {"late": True}

    def test_a_route_replaced_at_the_same_count_is_picked_up(self):
        app = FastAPI()

        @app.get("/swap")
        async def before():
            return {"which": "before"}

        install(app.router)
        client = TestClient(app)
        assert client.get("/swap").json() == {"which": "before"}
        app.router.routes.clear()

        @app.get("/swap")
        async def after():
            return {"which": "after"}

        assert client.get("/swap").json() == {"which": "after"}

    def test_a_removed_route_is_no_longer_served(self):
        app = FastAPI()

        @app.get("/gone")
        async def gone():
            return {"gone": False}

        install(app.router)
        client = TestClient(app)
        assert client.get("/gone").status_code == 200
        app.router.routes.clear()
        assert client.get("/gone").status_code == 404


class TestUnmatchableRoutes:
    def test_a_route_that_cannot_be_matched_keeps_the_url_on_fastapi(self):
        class Odd:
            def matches(self, _scope: Any) -> tuple[Any, Any]:
                raise RuntimeError("cannot match")

        router = APIRouter()

        @router.get("/ping")
        async def ping():
            return {"ping": True}

        router.routes.insert(0, Odd())
        assert build_table(router) == {}


class TestScope:
    def test_handlers_see_the_route_in_the_scope(self):
        seen: dict[str, Any] = {}
        app = FastAPI()

        @app.middleware("http")
        async def peek(request, call_next):
            response = await call_next(request)
            seen["route"] = request.scope.get("route")
            seen["path_params"] = request.scope.get("path_params")
            return response

        @app.get("/scoped")
        async def scoped():
            return {"ok": True}

        install(app.router)
        TestClient(app).get("/scoped")
        assert seen["route"].path == "/scoped"
        assert seen["path_params"] == {}

    def test_a_root_path_falls_back_to_fastapi(self):
        app = FastAPI(root_path="/api")

        @app.get("/x")
        async def x():
            return {"x": 1}

        install(app.router)
        assert isinstance(app.router.middleware_stack, FastPath)
        assert TestClient(app).get("/x").json() == {"x": 1}
