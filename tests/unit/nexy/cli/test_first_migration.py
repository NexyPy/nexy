"""`nx new` creates the first migration and the tables when the database is known.

A project with an ORM and a database URL should answer on its first `nexy dev`: the tables exist
before the developer has typed a migration command.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from nexy.modules.cli.migrations import first
from nexy.modules.cli.migrations.first import run_first_migration

URL = "sqlite:///dev.db"


class Runner:
    """Records every command and answers with the exit codes it was given."""

    def __init__(self, codes: dict[str, int] | None = None, output: str = ""):
        self.calls: list[list[str]] = []
        self.codes = codes or {}
        self.output = output

    def __call__(self, args: list[str], _cwd: Path) -> subprocess.CompletedProcess[str]:
        self.calls.append(args)
        code = self.codes.get(" ".join(args[:2]), 0)
        return subprocess.CompletedProcess(
            args, code, stdout="", stderr=self.output if code else ""
        )


@pytest.fixture(autouse=True)
def reachable(monkeypatch):
    monkeypatch.setattr(first, "connection_problem", lambda _url: None)


def test_alembic_creates_the_migration_then_applies_it(tmp_path):
    run = Runner()
    run_first_migration("alembic", tmp_path, URL, run)
    assert run.calls == [
        ["alembic", "revision", "--autogenerate", "-m", "create tables"],
        ["alembic", "upgrade", "head"],
    ]


def test_aerich_creates_the_migration_and_the_tables_in_one_command(tmp_path):
    run = Runner()
    run_first_migration("aerich", tmp_path, "sqlite://dev.db", run)
    assert run.calls == [["aerich", "init-db"]]


def test_a_finished_run_says_so(tmp_path):
    assert run_first_migration("alembic", tmp_path, URL, Runner()).done is True


def test_without_a_database_url_nothing_runs(tmp_path):
    run = Runner()
    result = run_first_migration("alembic", tmp_path, None, run)
    assert (run.calls, result.done) == ([], False)


def test_not_trying_is_not_a_problem_to_report(tmp_path):
    assert run_first_migration("alembic", tmp_path, None, Runner()).problem == ""


def test_an_unreachable_database_runs_nothing_and_says_why(tmp_path, monkeypatch):
    monkeypatch.setattr(
        first, "connection_problem", lambda _url: ("connection", OSError("refused"))
    )
    run = Runner()
    result = run_first_migration("alembic", tmp_path, URL, run)
    assert run.calls == [] and "refused" in result.problem


def test_a_missing_driver_is_named(tmp_path, monkeypatch):
    monkeypatch.setattr(
        first, "connection_problem", lambda _url: ("driver", ImportError("psycopg"))
    )
    assert "psycopg" in run_first_migration("alembic", tmp_path, URL, Runner()).problem


def test_tortoise_urls_are_not_checked_with_sqlalchemy(tmp_path, monkeypatch):
    def refuse(_url):
        raise AssertionError("SQLAlchemy cannot read a Tortoise URL")

    monkeypatch.setattr(first, "connection_problem", refuse)
    assert run_first_migration("aerich", tmp_path, "postgres://u:p@h/db", Runner()).done is True


def test_a_failing_command_reports_what_the_tool_said(tmp_path):
    run = Runner({"alembic revision": 1}, output="Target database is not up to date")
    result = run_first_migration("alembic", tmp_path, URL, run)
    assert not result.done and "not up to date" in result.problem


def test_nothing_is_applied_after_a_failed_revision(tmp_path):
    run = Runner({"alembic revision": 1}, output="boom")
    run_first_migration("alembic", tmp_path, URL, run)
    assert run.calls == [["alembic", "revision", "--autogenerate", "-m", "create tables"]]
