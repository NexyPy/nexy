"""`nexy build` leaves a marker; `nexy start` serves only a project that has one."""

from __future__ import annotations

import json

from nexy.helpers.server.markers import has_build, write_build_marker


def test_a_project_never_built_has_no_build(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert not has_build()


def test_a_built_project_has_a_build(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_build_marker("9.9.9")
    assert has_build()


def test_the_marker_names_the_version_that_built(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_build_marker("9.9.9")
    marker = json.loads((tmp_path / "__nexy__" / "build.json").read_text(encoding="utf-8"))
    assert marker["version"] == "9.9.9"
