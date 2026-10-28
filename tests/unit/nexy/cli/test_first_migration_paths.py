"""A relative SQLite file is a file of the new project, not of the folder `nx new` runs from.

`nx new my-app` runs from the parent folder. Checking `sqlite:///dev.db` from there would create
`dev.db` next to `my-app`, and test a database the project never uses.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from nexy.modules.cli.migrations.first import run_first_migration


def _ok(args: list[str], _cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args, 0, stdout="", stderr="")


def test_the_check_leaves_no_file_where_nx_runs(tmp_path, monkeypatch):
    project, elsewhere = tmp_path / "my-app", tmp_path / "parent"
    project.mkdir()
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    run_first_migration("alembic", project, "sqlite:///dev.db", _ok)
    assert not (elsewhere / "dev.db").exists()


def test_the_database_that_is_checked_is_the_one_of_the_project(tmp_path, monkeypatch):
    project, elsewhere = tmp_path / "my-app", tmp_path / "parent"
    project.mkdir()
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    run_first_migration("alembic", project, "sqlite:///dev.db", _ok)
    assert (project / "dev.db").exists()


def test_an_absolute_sqlite_path_is_left_as_it_is(tmp_path, monkeypatch):
    project, elsewhere = tmp_path / "my-app", tmp_path / "parent"
    project.mkdir()
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    database = (tmp_path / "chosen.db").as_posix()
    run_first_migration("alembic", project, f"sqlite:///{database}", _ok)
    assert (tmp_path / "chosen.db").exists() and not (project / "dev.db").exists()
