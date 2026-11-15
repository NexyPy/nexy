"""`nx start` serves a project only when every route loads."""

from __future__ import annotations

import importlib

import pytest

start_module = importlib.import_module("nexy.modules.cli.commands.start")


def test_a_project_whose_routes_load_is_served():
    start_module._refuse_broken_project([])


def test_a_route_that_fails_to_load_stops_the_start():
    with pytest.raises(SystemExit) as stop:
        start_module._refuse_broken_project(["src/routes/users.py: invalid syntax"])
    assert stop.value.code == 1


def test_the_stop_says_how_many_routes_failed(capsys):
    with pytest.raises(SystemExit):
        start_module._refuse_broken_project(["a.py: x", "b.py: y"])
    assert "2" in capsys.readouterr().out


def test_a_built_project_is_served(monkeypatch):
    monkeypatch.setattr(start_module, "has_build", lambda: True)
    start_module._refuse_unbuilt_project()


def test_a_project_without_a_build_is_not_started(monkeypatch):
    monkeypatch.setattr(start_module, "has_build", lambda: False)
    with pytest.raises(SystemExit) as stop:
        start_module._refuse_unbuilt_project()
    assert stop.value.code == 1


def test_the_stop_says_to_run_nexy_build(monkeypatch, capsys):
    monkeypatch.setattr(start_module, "has_build", lambda: False)
    with pytest.raises(SystemExit):
        start_module._refuse_unbuilt_project()
    assert "nexy build" in capsys.readouterr().out
