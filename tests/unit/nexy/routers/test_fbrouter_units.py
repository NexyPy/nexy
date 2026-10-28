"""The small pieces of file-based routing, each tested alone."""

from __future__ import annotations

import inspect
import types

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from nexy.modules.routers.fbrouter.error_pages import ErrorPages, SpecialPage, pick, render
from nexy.modules.routers.fbrouter.handlers import coerce_path_params, stream_body
from nexy.modules.routers.fbrouter.registrar import path_sort_key, revalidate_window
from nexy.modules.routers.fbrouter.scanner import component_name, route_clean_path


class TestPathOrder:
    def test_a_static_path_comes_before_a_dynamic_one(self):
        assert path_sort_key("/about") < path_sort_key("/{slug}")

    def test_a_dynamic_path_with_more_fixed_segments_comes_first(self):
        assert path_sort_key("/blog/{slug}") < path_sort_key("/{a}/{b}")

    def test_a_catch_all_comes_last(self):
        assert path_sort_key("/docs/{path:path}") > path_sort_key("/{slug}")

    def test_paths_sort_from_specific_to_general(self):
        paths = ["/{path:path}", "/{slug}", "/blog/{slug}", "/about"]
        assert sorted(paths, key=path_sort_key) == [
            "/about",
            "/blog/{slug}",
            "/{slug}",
            "/{path:path}",
        ]


class TestPathParams:
    @staticmethod
    def _signature(**annotations):
        params = [
            inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY, annotation=annotation)
            for name, annotation in annotations.items()
        ]
        return inspect.Signature(params)

    def test_an_int_annotation_converts(self):
        assert coerce_path_params(self._signature(id=int), {"id": "7"}) == {"id": 7}

    def test_a_float_annotation_converts(self):
        assert coerce_path_params(self._signature(x=float), {"x": "1.5"}) == {"x": 1.5}

    def test_a_value_that_does_not_convert_stays_text(self):
        assert coerce_path_params(self._signature(id=int), {"id": "abc"}) == {"id": "abc"}

    def test_an_unannotated_value_stays_text(self):
        assert coerce_path_params(self._signature(), {"slug": "a"}) == {"slug": "a"}


class TestStreamBody:
    def test_a_string_is_one_chunk(self):
        assert list(stream_body("é")) == ["é".encode()]

    def test_a_generator_streams_its_chunks(self):
        assert list(stream_body(iter(["a", b"b"]))) == [b"a", b"b"]


class TestRevalidate:
    @pytest.mark.parametrize(("value", "expected"), [(5, 5), (0, None), (-1, None), ("5", None)])
    def test_only_a_positive_int_is_a_window(self, value, expected):
        module = types.SimpleNamespace(revalidate=value)
        assert revalidate_window(module) == expected

    def test_no_attribute_means_no_window(self):
        assert revalidate_window(types.SimpleNamespace()) is None


class TestCleanPath:
    def test_the_prefix_and_extension_go(self):
        assert route_clean_path("src/routes/blog/post.nexy") == "/blog/post"

    def test_dots_inside_a_dynamic_segment_survive(self):
        assert route_clean_path("src/routes/docs/[...path].tsx") == "/docs/[...path]"


class TestComponentName:
    @staticmethod
    def _module(**attrs):
        module = types.ModuleType("m")
        for name, value in attrs.items():
            setattr(module, name, value)
        return module

    def test_the_wanted_name_wins_when_it_exists(self):
        module = self._module(Page=lambda: "")
        assert component_name(module, "Page", ".tsx") == "Page"

    def test_a_framework_route_falls_back_to_the_function_it_defines(self):
        def Home() -> str:  # noqa: N802
            return ""

        Home.__module__ = "m"
        module = self._module(Home=Home)
        assert component_name(module, "Index", ".tsx") == "Home"

    def test_a_server_route_keeps_the_wanted_name(self):
        assert component_name(self._module(), "Index", ".nexy") == "Index"


class TestErrorPages:
    @staticmethod
    def _page(scope: str, body: str) -> SpecialPage:
        module = types.ModuleType("p")
        module.Page = lambda: body
        return SpecialPage(scope, module, "Page")

    def test_a_folder_is_not_a_prefix_of_a_longer_name(self):
        pages = [self._page("/", "root"), self._page("/blog", "blog")]
        assert pick(pages, "/blogger/post") is pages[0]

    def test_the_folder_itself_is_inside_the_folder(self):
        pages = [self._page("/", "root"), self._page("/blog", "blog")]
        assert pick(pages, "/blog") is pages[1]

    def test_an_api_client_still_gets_json_when_a_page_exists(self):
        app = FastAPI()
        ErrorPages([self._page("/", "<p>custom</p>")], []).register(app)
        answer = TestClient(app).get("/nowhere", headers={"accept": "application/json"})
        assert answer.headers["content-type"].startswith("application/json")

    def test_a_browser_still_gets_the_page(self):
        app = FastAPI()
        ErrorPages([self._page("/", "<p>custom</p>")], []).register(app)
        answer = TestClient(app).get("/nowhere", headers={"accept": "text/html"})
        assert "custom" in answer.text

    def test_the_deepest_folder_wins(self):
        pages = [self._page("/", "root"), self._page("/blog", "blog")]
        assert pick(pages, "/blog/post") is pages[1]

    def test_no_folder_matches(self):
        assert pick([self._page("/blog", "b")], "/about") is None

    def test_a_page_is_rendered_with_its_status(self):
        answer = render(self._page("/", "<h1>gone</h1>"), 404)
        assert (answer.status_code, answer.body) == (404, b"<h1>gone</h1>")

    def test_a_page_that_fails_shows_only_the_status(self):
        module = types.ModuleType("p")

        def boom() -> str:
            raise RuntimeError("secret")

        module.Page = boom
        answer = render(SpecialPage("/", module, "Page"), 500)
        assert answer.body == b"<h1>500</h1>"

    def test_a_missing_component_shows_only_the_status(self):
        answer = render(SpecialPage("/", types.ModuleType("p"), "Nope"), 404)
        assert answer.body == b"<h1>404</h1>"

    def test_the_root_page_answers_an_unknown_url(self):
        app = FastAPI()
        ErrorPages([self._page("/", "<p>custom</p>")], []).register(app)
        client = TestClient(app)
        assert "custom" in client.get("/nowhere").text

    def test_without_a_page_nothing_is_installed(self):
        app = FastAPI()
        ErrorPages([], []).register(app)
        assert app.exception_handlers.keys() == FastAPI().exception_handlers.keys()
