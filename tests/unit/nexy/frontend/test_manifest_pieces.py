"""The route manifest: which files are routes, and the TypeScript written for them."""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.core.config import Config
from nexy.modules.frontend.manifest import (
    _is_route_file,
    _route_line,
    _route_literal,
    _route_type,
    render_manifest,
)


def _entry(path: str, **changes) -> dict[str, object]:
    base = {
        "path": path,
        "file": f"/src/routes{path}.tsx",
        "layout": None,
        "layouts": [],
        "params": [],
    }
    return {**base, **changes}


class TestRouteLiteral:
    def test_a_static_url_is_a_string_literal(self):
        assert _route_literal("/about") == '"/about"'

    def test_a_parameter_becomes_a_template_slot(self):
        assert _route_literal("/blog/{slug}") == "`/blog/${string}`"

    def test_a_catch_all_becomes_a_template_slot(self):
        assert _route_literal("/docs/{path:path}") == "`/docs/${string}`"

    def test_several_parameters_each_get_a_slot(self):
        assert _route_literal("/a/{x}/b/{y}") == "`/a/${string}/b/${string}`"


class TestRouteType:
    def test_no_routes_still_export_the_type_the_client_imports(self):
        assert _route_type([]) == ["", "export type Route = never;"]

    def test_a_url_is_listed_once(self):
        lines = _route_type([_entry("/a"), _entry("/a"), _entry("/b")])
        assert lines[-1] == 'export type Route = "/a" | "/b";'


class TestRender:
    def test_the_array_has_one_line_per_route(self):
        text = render_manifest([_entry("/"), _entry("/about")], include_route_type=False)
        assert text.count("  { path:") == 2

    def test_the_route_type_is_only_in_the_full_manifest(self):
        entries = [_entry("/")]
        assert "export type Route" in render_manifest(entries, True)
        assert "export type Route" not in render_manifest(entries, False)

    def test_a_line_carries_the_layout_and_params(self):
        line = _route_line(_entry("/b/{id}", layout="/src/routes/layout.tsx", params=["id"]))
        assert 'layout: "/src/routes/layout.tsx"' in line and 'params: ["id"]' in line

    def test_a_line_without_layouts_has_an_empty_list(self):
        entry = _entry("/")
        del entry["layouts"]
        assert "layouts: []" in _route_line(entry)

    def test_the_file_ends_with_a_newline(self):
        assert render_manifest([], include_route_type=False).endswith("];\n")


class TestIsRouteFile:
    @pytest.fixture
    def routes(self, tmp_path: Path, monkeypatch) -> Path:
        monkeypatch.setattr(Config, "ROUTE_FILE_EXTENSIONS", [".tsx", ".nexy"])
        root = tmp_path / "routes"
        (root / "blog").mkdir(parents=True)
        (root / "_private").mkdir()
        return root

    def _make(self, root: Path, name: str) -> Path:
        path = root / name
        path.write_text("x", encoding="utf-8")
        return path

    def test_a_page_is_a_route(self, routes):
        assert _is_route_file(self._make(routes, "about.tsx"), routes, set())

    def test_an_unknown_extension_is_not(self, routes):
        assert not _is_route_file(self._make(routes, "notes.txt"), routes, set())

    def test_a_layout_is_not(self, routes):
        assert not _is_route_file(self._make(routes, "layout.tsx"), routes, {"layout.tsx"})

    def test_a_private_folder_is_not(self, routes):
        assert not _is_route_file(self._make(routes, "_private/a.tsx"), routes, set())

    def test_a_dot_file_is_not(self, routes):
        assert not _is_route_file(self._make(routes, ".hidden.tsx"), routes, set())

    def test_a_folder_is_not(self, routes):
        assert not _is_route_file(routes / "blog", routes, set())
