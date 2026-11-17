"""`nx format` prints what uv prints: one line per finished tool, uv errors and warnings."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

# The package re-exports the function under the module's name: import the module by path.
command = importlib.import_module("nexy.modules.cli.commands.format")


def _fake_tool(tmp_path: Path, output: str, code: int) -> str:
    """An executable that prints *output* and exits with *code*, standing for ruff."""
    tool = tmp_path / "fake-ruff"
    tool.write_text(f"#!{sys.executable}\nimport sys\nprint({output!r})\nsys.exit({code})\n")
    tool.chmod(0o755)
    return str(tool)


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
