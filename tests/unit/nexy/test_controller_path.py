"""@Controller takes the path it answers on; `prefix=` is its old name."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from nexy.decorators import Controller, Module


def _get(controller: type, url: str) -> int:
    @Module()
    class DemoModule:
        controllers = [controller]

    app = FastAPI()
    app.include_router(DemoModule)
    return TestClient(app).get(url).status_code


def test_controller_path_is_the_first_argument():
    @Controller("/search")
    class SearchController:
        async def get(self) -> dict:
            return {}

    assert _get(SearchController, "/search/") == 200


def test_controller_path_is_a_keyword():
    @Controller(path="/find")
    class FindController:
        async def get(self) -> dict:
            return {}

    assert _get(FindController, "/find/") == 200


def test_controller_prefix_still_routes():
    with pytest.warns(DeprecationWarning):

        @Controller(prefix="/old")
        class OldController:
            async def get(self) -> dict:
                return {}

    assert _get(OldController, "/old/") == 200


def test_controller_prefix_warns_to_use_path():
    with pytest.warns(DeprecationWarning, match="path"):
        Controller(prefix="/old")


def test_controller_path_and_prefix_together_are_refused():
    with pytest.raises(TypeError):
        Controller("/a", prefix="/b")
