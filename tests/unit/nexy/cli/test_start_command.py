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


def _start_shows(monkeypatch, use_docs: bool | str) -> list[str]:
    """What `nx start` lists once ready, with the steps around it stubbed."""
    from types import SimpleNamespace

    from nexy.helpers.common import launcher
    from nexy.helpers.server.listening import Endpoint

    shown: list[str] = []
    for step in ("pycache", "ensure_project_packages", "abort_on_invalid_config"):
        monkeypatch.setattr(start_module, step, lambda: None)
    monkeypatch.setattr(start_module, "_refuse_unbuilt_project", lambda: None)
    monkeypatch.setattr(start_module, "_route_failures", list)
    monkeypatch.setattr(start_module, "_endpoint", lambda *_: Endpoint("127.0.0.1", 8000))
    monkeypatch.setattr(start_module, "_serve", lambda _endpoint: None)
    config = SimpleNamespace(useDocs=use_docs, useDocsUrl="/docs")
    monkeypatch.setattr(start_module, "Config", lambda: config)
    monkeypatch.setattr(launcher, "banner", lambda *_: None)
    monkeypatch.setattr(launcher, "entry", lambda _label, value: shown.append(value))
    start_module.start()
    return shown


def test_start_says_where_the_api_reference_answers(monkeypatch):
    assert "http://localhost:8000/docs" in _start_shows(monkeypatch, True)


def test_start_names_no_reference_that_only_dev_serves(monkeypatch):
    assert "http://localhost:8000/docs" not in _start_shows(monkeypatch, "dev")
