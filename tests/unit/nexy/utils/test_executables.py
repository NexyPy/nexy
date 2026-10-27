"""A command-line tool is found on the PATH, or next to the interpreter that runs Nexy."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from nexy.helpers.common import executables
from nexy.helpers.common.executables import find_tool

EXE = ".exe" if os.name == "nt" else ""


def _tool(folder: Path, name: str = "mytool") -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}{EXE}"
    path.write_text("#!/bin/sh\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return path


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    """No tool on the PATH, and an interpreter that lives in `tmp_path/env/bin`."""
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    bin_dir = tmp_path / "env" / ("Scripts" if os.name == "nt" else "bin")
    bin_dir.mkdir(parents=True)
    monkeypatch.setattr(executables.sys, "executable", str(bin_dir / f"python{EXE}"))
    return bin_dir


def test_a_tool_on_the_path_is_found(tmp_path, monkeypatch):
    folder = tmp_path / "tools"
    path = _tool(folder)
    monkeypatch.setenv("PATH", str(folder))
    assert find_tool("mytool") is not None and Path(find_tool("mytool")).samefile(path)


def test_a_tool_next_to_the_interpreter_is_found_without_an_active_environment(isolated):
    path = _tool(isolated)
    assert Path(find_tool("mytool")).samefile(path)


def test_the_path_wins_over_the_interpreter_folder(tmp_path, monkeypatch, isolated):
    _tool(isolated)
    on_path = _tool(tmp_path / "tools")
    monkeypatch.setenv("PATH", str(on_path.parent))
    assert Path(find_tool("mytool")).samefile(on_path)


@pytest.mark.usefixtures("isolated")
def test_a_missing_tool_is_none():
    assert find_tool("nothing-like-it") is None


def test_a_folder_with_the_name_of_a_tool_is_not_a_tool(isolated):
    (isolated / f"mytool{EXE}").mkdir()
    assert find_tool("mytool") is None
