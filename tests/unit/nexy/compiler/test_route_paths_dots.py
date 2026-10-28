"""Only the extension is cut from a route file: dots in the name are part of the URL."""

from __future__ import annotations

from nexy.modules.compiler.route_paths import route_paths


def test_a_catch_all_keeps_its_dots_until_it_becomes_a_parameter():
    assert route_paths("src/routes/docs/[...path].tsx", "[...path]").pathname == "/docs/{path:path}"


def test_a_folder_with_a_dot_keeps_it():
    assert route_paths("src/routes/v1.2/index.tsx", "index").pathname == "/v1.2"


def test_a_page_with_a_dot_in_its_name_keeps_it():
    assert route_paths("src/routes/release.notes.tsx", "release.notes").pathname == "/release.notes"
