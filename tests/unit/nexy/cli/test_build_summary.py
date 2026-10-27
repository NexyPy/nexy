"""`nx build` names what it built: a client-routed project has routes, not server components."""

from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

build_module = importlib.import_module("nexy.modules.cli.commands.build")


@pytest.fixture
def sections(monkeypatch):
    seen: list[str] = []
    monkeypatch.setattr(
        build_module, "print_tree_section", lambda title, *_a, **_k: seen.append(title)
    )
    return seen


def _result():
    return SimpleNamespace(success=["a"], failed=[], skipped=[])


def test_a_server_project_reports_server_and_client_components(monkeypatch, sections):
    monkeypatch.setattr(build_module.Config, "useCSR", False)
    build_module._show_summary(_result(), [])
    assert sections == ["server components", "client components"]


def test_a_client_routed_project_reports_routes_not_server_components(monkeypatch, sections):
    monkeypatch.setattr(build_module.Config, "useCSR", True)
    build_module._show_summary(_result(), [])
    assert sections == ["routes"]


def test_the_compile_step_of_a_client_project_is_called_routes(monkeypatch):
    monkeypatch.setattr(build_module.Config, "useCSR", True)
    assert "routes" in build_module._compile_label().lower()
    monkeypatch.setattr(build_module.Config, "useCSR", False)
    assert "server components" in build_module._compile_label().lower()
