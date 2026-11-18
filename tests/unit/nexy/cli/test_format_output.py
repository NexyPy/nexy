"""`nx format` prints what uv prints: one line per finished tool, uv errors and warnings."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from tests.unit.nexy.cli.fake_tools import fake_tool

# The package re-exports the function under the module's name: import the module by path.
command = importlib.import_module("nexy.modules.cli.commands.format")


def _fake_tool(tmp_path: Path, output: str, code: int) -> str:
    """An executable that prints *output* and exits with *code*, standing for ruff."""
    return fake_tool(tmp_path, "fake-ruff", output, code)


@pytest.fixture
def project(tmp_path, monkeypatch):
    (tmp_path / "app.py").write_text("x = 1\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NEXY_LANG", "en")
    monkeypatch.setattr(command.shutil, "which", lambda _name: None)
    return tmp_path


def _with_ruff(monkeypatch, project: Path, output: str, code: int) -> None:
    monkeypatch.setattr(command, "find_tool", lambda _name: _fake_tool(project, output, code))


def test_format_a_formatted_scope_leaves_one_line_with_its_duration(project, monkeypatch, capsys):
    _with_ruff(monkeypatch, project, "1 file reformatted", 0)
    command.format_()
    assert capsys.readouterr().out.startswith("Formatted Python with ruff in ")


def test_format_check_mode_says_it_only_checked(project, monkeypatch, capsys):
    _with_ruff(monkeypatch, project, "ok", 0)
    command.format_(check=True)
    assert capsys.readouterr().out.startswith("Checked the format of Python with ruff in ")


def test_format_all_done_ends_with_the_verdict(project, monkeypatch, capsys):
    _with_ruff(monkeypatch, project, "ok", 0)
    command.format_()
    assert capsys.readouterr().out.splitlines()[-1] == "All files formatted"


def test_format_a_failing_tool_is_a_uv_error_with_its_report(project, monkeypatch, capsys):
    _with_ruff(monkeypatch, project, "Would reformat: app.py", 1)
    with pytest.raises(SystemExit):
        command.format_(check=True)
    out = capsys.readouterr().out
    assert out.startswith("error: Checking the format of Python with ruff\n")


def test_format_a_failing_tool_shows_what_it_said(project, monkeypatch, capsys):
    _with_ruff(monkeypatch, project, "Would reformat: app.py", 1)
    with pytest.raises(SystemExit):
        command.format_(check=True)
    assert "  Would reformat: app.py\n" in capsys.readouterr().out


@pytest.mark.usefixtures("project")
def test_format_a_missing_tool_is_a_uv_warning(monkeypatch, capsys):
    monkeypatch.setattr(command, "find_tool", lambda _name: None)
    command.format_()
    assert capsys.readouterr().out.startswith("warning: ruff not found - skipping Python\n")


def test_format_nexy_files_leave_one_line_for_all_of_them(project, monkeypatch, capsys):
    monkeypatch.setattr(command, "find_tool", lambda _name: None)
    (project / "page.nexy").write_text("<h1>Hi</h1>\n")
    command.format_()
    assert "Formatted 1 .nexy file(s) in " in capsys.readouterr().out


def test_format_a_nexy_file_that_would_change_is_a_uv_error(project, monkeypatch, capsys):
    monkeypatch.setattr(command, "find_tool", lambda _name: None)
    (project / "page.nexy").write_text("<h1>Hi</h1>\n\n\n")
    with pytest.raises(SystemExit):
        command.format_(check=True)
    assert "error: page.nexy\n  cause: would be reformatted\n" in capsys.readouterr().out


def test_format_ts_files_without_prettier_are_a_uv_warning(project, capsys):
    (project / "app.ts").write_text("export const x = 1\n")
    command._format_ts(project, check=False)
    assert capsys.readouterr().out == "warning: prettier not found - skipping JS/TS\n"


def test_format_ts_files_run_prettier(project, monkeypatch, capsys):
    (project / "app.ts").write_text("export const x = 1\n")
    monkeypatch.setattr(command.shutil, "which", lambda _name: _fake_tool(project, "ok", 0))
    command._format_ts(project, check=False)
    assert capsys.readouterr().out.startswith("Formatted JS/TS with prettier in ")
