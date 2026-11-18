"""`nx test` prints what uv prints: one line per finished runner, uv errors and warnings."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from tests.unit.nexy.cli.fake_tools import fake_tool

# The package re-exports the function under the module's name: import the module by path.
command = importlib.import_module("nexy.modules.cli.commands.test")


def _fake_pytest(tmp_path: Path, output: str, code: int) -> str:
    return fake_tool(tmp_path, "fake-pytest", output, code)


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NEXY_LANG", "en")
    return tmp_path


def _run(monkeypatch, project: Path, output: str, code: int) -> None:
    monkeypatch.setattr(command, "find_tool", lambda _name: _fake_pytest(project, output, code))
    command.test(server=True, client=False, args=None)


def test_test_a_passing_run_leaves_one_line_with_its_duration(project, monkeypatch, capsys):
    _run(monkeypatch, project, "== 3 passed in 0.1s ==", 0)
    assert capsys.readouterr().out.startswith("Ran the server tests with pytest in ")


def test_test_a_passing_run_keeps_the_count_of_the_runner(project, monkeypatch, capsys):
    _run(monkeypatch, project, "== 3 passed in 0.1s ==", 0)
    assert capsys.readouterr().out.splitlines()[1] == "  == 3 passed in 0.1s =="


def test_test_all_passing_ends_with_the_verdict(project, monkeypatch, capsys):
    _run(monkeypatch, project, "== 3 passed ==", 0)
    assert capsys.readouterr().out.splitlines()[-1] == "All tests passed"


def test_test_a_failing_run_is_a_uv_error(project, monkeypatch, capsys):
    with pytest.raises(SystemExit):
        _run(monkeypatch, project, "FAILED tests/test_a.py::test_b", 1)
    assert capsys.readouterr().out.startswith("error: Running the server tests with pytest\n")


def test_test_a_failing_run_shows_the_report(project, monkeypatch, capsys):
    with pytest.raises(SystemExit):
        _run(monkeypatch, project, "FAILED tests/test_a.py::test_b", 1)
    assert "  FAILED tests/test_a.py::test_b\n" in capsys.readouterr().out


@pytest.mark.usefixtures("project")
def test_test_a_missing_pytest_is_a_uv_warning(monkeypatch, capsys):
    monkeypatch.setattr(command, "find_tool", lambda _name: None)
    command.test(server=True, client=False, args=None)
    assert capsys.readouterr().out.startswith("warning: pytest not found - skipping server tests\n")


@pytest.mark.usefixtures("project")
def test_test_a_project_without_vitest_is_a_uv_warning(capsys):
    command.test(server=False, client=True, args=None)
    expected = "warning: vitest not configured - skipping client tests\n"
    assert capsys.readouterr().out.startswith(expected)


def test_test_client_runs_vitest(project, monkeypatch, capsys):
    (project / "vitest.config.ts").write_text("export default {}\n")
    monkeypatch.setattr(command.shutil, "which", lambda _name: _fake_pytest(project, "1 passed", 0))
    command._run_client(project, [])
    assert capsys.readouterr().out.startswith("Ran the client tests with vitest in ")
