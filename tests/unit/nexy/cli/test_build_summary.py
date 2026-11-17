"""`nx build` names what it built, the way uv lists what it installed."""

from __future__ import annotations

import importlib
import time
from types import SimpleNamespace

import pytest

build_module = importlib.import_module("nexy.modules.cli.commands.build")


@pytest.fixture(autouse=True)
def english(monkeypatch):
    monkeypatch.setenv("NEXY_LANG", "en")


@pytest.fixture
def sections(monkeypatch):
    seen: list[tuple[str, list[str]]] = []
    monkeypatch.setattr(
        build_module, "print_summary", lambda title, counts, *_a, **_k: seen.append((title, counts))
    )
    return seen


def _result(skipped=()):
    return SimpleNamespace(success=["a"], failed=[], skipped=list(skipped))


def _entries(*statuses: str) -> list[dict[str, str]]:
    return [{"file": f"c{n}.tsx", "status": status} for n, status in enumerate(statuses)]


def test_a_server_project_reports_server_and_client_components(monkeypatch, sections):
    monkeypatch.setattr(build_module.Config, "useCSR", False)
    build_module._show_summary(_result(), [])
    assert [title for title, _counts in sections] == ["Server components", "Client components"]


def test_a_client_routed_project_reports_routes_not_server_components(monkeypatch, sections):
    monkeypatch.setattr(build_module.Config, "useCSR", True)
    build_module._show_summary(_result(), [])
    assert [title for title, _counts in sections] == ["Routes"]


def test_the_counts_name_what_was_built_and_cached(monkeypatch, sections):
    monkeypatch.setattr(build_module.Config, "useCSR", True)
    build_module._show_summary(_result(skipped=["b", "c"]), [])
    assert sections[0][1] == ["1 built", "2 cached"]


def test_the_client_counts_name_the_client_only_components(monkeypatch, sections):
    monkeypatch.setattr(build_module.Config, "useCSR", False)
    build_module._show_summary(_result(), _entries("success", "not_supported"))
    assert sections[1][1] == ["1 rendered", "1 client-only"]


def test_a_component_that_failed_to_render_is_a_uv_warning(monkeypatch, capsys):
    monkeypatch.setattr(build_module.Config, "useCSR", False)
    build_module._show_summary(_result(), _entries("failed"))
    expected = "warning: c0.tsx has no server HTML: it renders on the client only"
    assert expected in capsys.readouterr().out


def test_the_compile_step_of_a_client_project_is_called_routes(monkeypatch):
    monkeypatch.setattr(build_module.Config, "useCSR", True)
    assert "routes" in build_module._compile_label().lower()


def test_the_compile_step_of_a_server_project_is_called_server_components(monkeypatch):
    monkeypatch.setattr(build_module.Config, "useCSR", False)
    assert "server components" in build_module._compile_label().lower()


def test_the_build_ends_with_one_line_and_its_duration(capsys):
    build_module._announce_end(time.perf_counter())
    assert capsys.readouterr().out.startswith("Built the project in ")


def test_a_failed_component_is_a_uv_error_naming_it(capsys):
    failed = SimpleNamespace(success=[], failed=["src/routes/a.nexy"], skipped=[])
    with pytest.raises(SystemExit):
        build_module._exit_on_failed_components(failed)
    expected = "error: 1 component(s) failed\n  cause: src/routes/a.nexy\n"
    assert capsys.readouterr().out == expected


def test_a_failed_check_is_a_uv_error(monkeypatch, capsys):
    monkeypatch.setattr(build_module, "run_task", lambda *_a, **_k: SimpleNamespace(ok=False))
    with pytest.raises(SystemExit):
        build_module._run_checks()
    assert capsys.readouterr().out == "error: Some checks failed\n"


def test_passing_checks_end_with_the_verdict(monkeypatch, capsys):
    monkeypatch.setattr(build_module, "run_task", lambda *_a, **_k: SimpleNamespace(ok=True))
    build_module._run_checks()
    assert capsys.readouterr().out == "All checks passed\n"
