"""`nx start` refuses to serve a project the way uv says a failure: one error line."""

from __future__ import annotations

import importlib

import pytest

# The package re-exports the function under the module's name: import the module by path.
start = importlib.import_module("nexy.modules.cli.commands.start")


@pytest.fixture(autouse=True)
def english(monkeypatch):
    monkeypatch.setenv("NEXY_LANG", "en")


def test_start_an_unbuilt_project_is_a_uv_error(monkeypatch, capsys):
    monkeypatch.setattr(start, "has_build", lambda: False)
    with pytest.raises(SystemExit):
        start._refuse_unbuilt_project()
    expected = "error: No production build: run `nexy build`, then `nexy start`.\n"
    assert capsys.readouterr().out == expected


def test_start_a_project_with_broken_routes_is_a_uv_error(capsys):
    with pytest.raises(SystemExit):
        start._refuse_broken_project(["src/routes/a.py", "src/routes/b.py"])
    expected = "error: 2 route file(s) failed to load: the server was not started.\n"
    assert capsys.readouterr().out == expected
