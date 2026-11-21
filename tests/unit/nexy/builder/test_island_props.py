"""The build lists the literal props each island gets, so it can snapshot each set (#554)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jinja2 import Environment

from nexy.helpers.imports.component_import import Import
from nexy.modules.builder.island_props import MANIFEST, collect, literal_props, write_manifest
from nexy.modules.compiler.parser.template import TemplateParser

IMPORTS = '---\nfrom "../components/spike.tsx" import Spike\n---\n'
TEMPLATE = '<Spike label="clicks" count="3" open="true" directive="client:visible" />'


@pytest.fixture
def page(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src" / "routes").mkdir(parents=True)
    file = tmp_path / "src" / "routes" / "index.nexy"
    file.write_text(IMPORTS + TEMPLATE, encoding="utf-8")
    return file


def _props(template: str) -> list[dict[str, object]]:
    return [props for _, props in literal_props(template)]


def _snapshots(page: Path) -> dict[str, dict[str, object]]:
    return collect([page])["src/components/spike.tsx"]["Spike"]


def test_literal_props_are_read_as_the_page_passes_them():
    assert _props(TEMPLATE) == [{"label": "clicks", "count": 3, "open": True}]


def test_a_computed_prop_is_not_literal():
    assert _props('<Spike label="{{ name }}" />') == []


def test_a_spread_is_not_literal():
    assert _props("<Spike {{ ...props }} />") == []


def test_an_island_with_children_is_not_snapshot_per_props():
    assert _props('<Spike label="clicks">text</Spike>') == []


def test_an_island_without_props_has_no_snapshot_of_its_own():
    assert _props('<Spike directive="client:idle" />') == []


def test_a_plain_tag_is_not_an_island():
    assert _props('<div label="clicks"><p title="x" /></div>') == []


def test_an_island_inside_a_tag_is_found():
    assert _props('<main><Spike label="taps" /></main>') == [{"label": "taps"}]


def test_a_value_that_is_not_a_valid_expression_is_skipped():
    assert _props("<Spike label='say \"hi\"' />") == []


def test_the_props_are_listed_under_the_island_file_and_symbol(page: Path):
    assert list(_snapshots(page).values()) == [{"label": "clicks", "count": 3, "open": True}]


def test_a_component_that_is_not_an_island_is_not_listed(page: Path):
    page.write_text(IMPORTS.replace("spike.tsx", "spike.nexy") + TEMPLATE, encoding="utf-8")
    assert collect([page]) == {}


def test_the_manifest_is_written_for_the_client_build(page: Path):
    write_manifest([page])
    assert json.loads(MANIFEST.read_text(encoding="utf-8")) == collect([page])


def test_the_page_serves_the_snapshot_the_build_listed(page: Path):
    key = next(iter(_snapshots(page)))
    static = page.parents[2] / "__nexy__" / "client" / "static" / "src" / "components"
    static.mkdir(parents=True)
    (static / "spike.Default.html").write_text("<b>count</b>", encoding="utf-8")
    (static / f"spike.Default.{key}.html").write_text("<b>clicks</b>", encoding="utf-8")
    island = Import("src/components/spike.tsx", "react", "Spike")
    html = (
        Environment().from_string(TemplateParser().parse(TEMPLATE, {"Spike"})).render(Spike=island)
    )
    assert "<b>clicks</b>" in html
