"""A page is rebuilt when any layout above it changes: all the way up to where layouts are found."""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.core.config import Config
from nexy.modules.builder.fingerprints import _layout_chain_cache, layout_chain_fingerprint


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Config, "ROUTER_PATH", "src/routes")
    monkeypatch.setattr(Config, "LAYOUT_FILE_NAMES", ["layout.nexy"])
    (tmp_path / "src" / "routes" / "blog").mkdir(parents=True)
    _layout_chain_cache.clear()
    yield tmp_path
    _layout_chain_cache.clear()


def test_a_folder_without_layouts_has_an_empty_fingerprint(project):
    assert layout_chain_fingerprint(project / "src" / "routes" / "blog") == ""


def test_a_layout_in_the_folder_is_in_the_fingerprint(project):
    (project / "src" / "routes" / "blog" / "layout.nexy").write_text("x")
    assert "blog/layout.nexy" in layout_chain_fingerprint(project / "src" / "routes" / "blog")


def test_a_layout_of_a_parent_folder_is_in_the_fingerprint(project):
    (project / "src" / "routes" / "layout.nexy").write_text("x")
    assert "routes/layout.nexy" in layout_chain_fingerprint(project / "src" / "routes" / "blog")


def test_a_layout_beside_the_routes_folder_is_in_the_fingerprint(project):
    (project / "src" / "layout.nexy").write_text("x")
    assert "src/layout.nexy" in layout_chain_fingerprint(project / "src" / "routes" / "blog")


def test_a_layout_outside_the_source_folder_is_not(project):
    (project / "layout.nexy").write_text("x")
    assert layout_chain_fingerprint(project / "src" / "routes" / "blog") == ""


def test_editing_a_layout_changes_the_fingerprint(project):
    layout = project / "src" / "routes" / "layout.nexy"
    layout.write_text("x")
    folder = project / "src" / "routes" / "blog"
    before = layout_chain_fingerprint(folder)
    _layout_chain_cache.clear()
    layout.write_text("a longer layout")
    assert layout_chain_fingerprint(folder) != before
