"""An island serves the build snapshot of the props it is given, else the default one (#554)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nexy.helpers.imports.ncc import NexyClientComponent, snapshot_key

STATIC = Path("__nexy__/client/static/src/components")


@pytest.fixture(autouse=True)
def _project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    STATIC.mkdir(parents=True)
    (STATIC / "spike.Default.html").write_text("<b>count</b>", encoding="utf-8")
    (STATIC / "spike.vue.html").write_text("<i>count</i>", encoding="utf-8")


def _plant(snapshot: str, props: dict[str, object], html: str) -> None:
    (STATIC / f"{snapshot}.{snapshot_key(json.dumps(props))}.html").write_text(html, "utf-8")


def _react(props: dict[str, object]) -> str:
    return NexyClientComponent("src/components/spike.tsx", "react", "Spike").generate(props)


def test_snapshot_key_is_the_same_for_the_same_props():
    assert snapshot_key('{"label": "clicks"}') == snapshot_key('{"label": "clicks"}')


def test_snapshot_key_differs_for_other_props():
    assert snapshot_key('{"label": "clicks"}') != snapshot_key('{"label": "taps"}')


def test_an_island_serves_the_snapshot_of_its_props():
    _plant("spike.Default", {"label": "clicks"}, "<b>clicks</b>")
    assert "<b>clicks</b>" in _react({"label": "clicks"})


def test_an_island_whose_props_have_no_snapshot_serves_the_default_one():
    _plant("spike.Default", {"label": "clicks"}, "<b>clicks</b>")
    assert "<b>count</b>" in _react({"label": "taps"})


def test_an_island_without_props_serves_the_default_snapshot():
    _plant("spike.Default", {}, "<b>empty</b>")
    assert "<b>count</b>" in _react({})


def test_the_directive_is_not_part_of_the_snapshot_key():
    _plant("spike.Default", {"label": "clicks"}, "<b>clicks</b>")
    assert "<b>clicks</b>" in _react({"label": "clicks", "directive": "client:visible"})


def test_a_vue_island_serves_the_snapshot_of_its_props():
    _plant("spike.vue", {"label": "clicks"}, "<i>clicks</i>")
    vue = NexyClientComponent("src/components/spike.vue", "vue", "Spike")
    assert "<i>clicks</i>" in vue.generate({"label": "clicks"})


def test_an_island_without_any_snapshot_is_empty():
    island = NexyClientComponent("src/components/none.tsx", "react", "None")
    assert "></ncc>" in island.generate({"label": "clicks"})


def test_a_named_export_serves_the_snapshot_of_its_props():
    (STATIC / "spike.Badge.html").write_text("<u>new</u>", encoding="utf-8")
    _plant("spike.Badge", {"label": "hot"}, "<u>hot</u>")
    badge = NexyClientComponent("src/components/spike.tsx", "react", "Badge")
    assert "<u>hot</u>" in badge.generate({"label": "hot"})
