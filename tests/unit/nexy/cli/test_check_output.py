"""`nx check` prints what uv prints: one line per finished tool, uv errors and warnings."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from tests.unit.nexy.cli.fake_tools import fake_tool

# The package re-exports the function under the module's name: import the module by path.
command = importlib.import_module("nexy.modules.cli.commands.check")


def _fake_tool(tmp_path: Path, output: str, code: int) -> str:
    """An executable that prints *output* and exits with *code*, standing for mypy."""
    return fake_tool(tmp_path, "fake-mypy", output, code)


@pytest.fixture
def project(tmp_path, monkeypatch):
    (tmp_path / "app.py").write_text("x = 1\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NEXY_LANG", "en")
    return tmp_path


def test_check_a_passing_tool_leaves_one_line_with_its_duration(project, monkeypatch, capsys):
    monkeypatch.setattr(command, "find_tool", lambda _name: _fake_tool(project, "ok", 0))
    command.check(tsc=False, nexypy=False)
    assert capsys.readouterr().out.startswith("Checked Python with mypy in ")


def test_check_all_passing_ends_with_the_verdict(project, monkeypatch, capsys):
    monkeypatch.setattr(command, "find_tool", lambda _name: _fake_tool(project, "ok", 0))
    command.check(tsc=False, nexypy=False)
    assert capsys.readouterr().out.splitlines()[-1] == "All checks passed"


def test_check_a_failing_tool_is_a_uv_error(project, monkeypatch, capsys):
    monkeypatch.setattr(command, "find_tool", lambda _name: _fake_tool(project, "app.py:1: bad", 1))
    with pytest.raises(SystemExit):
        command.check(tsc=False, nexypy=False)
    assert capsys.readouterr().out.startswith("error: Checking Python with mypy\n")


def test_check_a_failing_tool_shows_its_report(project, monkeypatch, capsys):
    monkeypatch.setattr(command, "find_tool", lambda _name: _fake_tool(project, "app.py:1: bad", 1))
    with pytest.raises(SystemExit):
        command.check(tsc=False, nexypy=False)
    assert "  app.py:1: bad\n" in capsys.readouterr().out


def test_check_a_failure_names_the_failed_sections(project, monkeypatch, capsys):
    monkeypatch.setattr(command, "find_tool", lambda _name: _fake_tool(project, "bad", 1))
    with pytest.raises(SystemExit):
        command.check(tsc=False, nexypy=False)
    out = capsys.readouterr().out
    assert out.endswith("error: 1 section(s) failed\n  cause: Python\n")


@pytest.mark.usefixtures("project")
def test_check_a_missing_tool_is_a_uv_warning(monkeypatch, capsys):
    monkeypatch.setattr(command, "find_tool", lambda _name: None)
    command.check(tsc=False, nexypy=False)
    assert capsys.readouterr().out.startswith("warning: mypy not found - skipping Python\n")


def test_check_prints_no_mark(project, monkeypatch, capsys):
    monkeypatch.setattr(command, "find_tool", lambda _name: _fake_tool(project, "ok", 0))
    command.check(tsc=False, nexypy=False)
    assert not set(capsys.readouterr().out) & set("✓✘⚠")


@pytest.mark.usefixtures("project")
def test_check_typescript_without_tsc_is_a_uv_warning(monkeypatch, capsys):
    monkeypatch.setattr(command.shutil, "which", lambda _name: None)
    command._check_typescript()
    assert capsys.readouterr().out == "warning: tsc not found - skipping TypeScript\n"


def test_check_typescript_runs_tsc(project, monkeypatch):
    monkeypatch.setattr(command.shutil, "which", lambda _name: _fake_tool(project, "ok", 0))
    assert command._check_typescript() is True


class _Built:
    def __init__(self, failed: list[str]) -> None:
        self.failed = failed

    def build(self, **_options: bool) -> _Built:
        return self


def test_check_nexy_a_file_that_does_not_compile_is_a_uv_error(project, monkeypatch, capsys):
    monkeypatch.setattr(command, "Builder", lambda: _Built(["src/routes/a.nexy"]))
    monkeypatch.setattr(command, "find_tool", lambda _name: None)
    command._check_nexy(project)
    assert "error: Could not compile src/routes/a.nexy\n" in capsys.readouterr().out


def test_check_nexy_without_mypy_passes_on_the_compile_alone(project, monkeypatch):
    monkeypatch.setattr(command, "Builder", lambda: _Built([]))
    monkeypatch.setattr(command, "find_tool", lambda _name: None)
    assert command._check_nexy(project) is True


def test_check_nexy_runs_mypy_on_the_generated_code(project, monkeypatch, capsys):
    (project / "__nexy__").mkdir()
    monkeypatch.setattr(command, "Builder", lambda: _Built([]))
    monkeypatch.setattr(command, "find_tool", lambda _name: _fake_tool(project, "ok", 0))
    command._check_nexy(project)
    assert "Checked __nexy__ with mypy in " in capsys.readouterr().out
