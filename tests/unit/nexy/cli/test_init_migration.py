"""`nx new` sets the migration tool up, then creates the first migration and the tables."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from nexy.modules.cli.init import template_setup
from nexy.modules.cli.init.template_setup import init_migration
from nexy.modules.cli.migrations import first

URL = "sqlite:///dev.db"


class Runner:
    def __init__(self):
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        self.calls.append(args)
        if args[:2] == ["alembic", "init"]:
            (cwd / "alembic").mkdir()
        if args[:2] == ["aerich", "init"]:
            (cwd / "migrations").mkdir()
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")


@pytest.fixture(autouse=True)
def reachable(monkeypatch):
    monkeypatch.setattr(first, "connection_problem", lambda _url: None)


def test_a_sql_project_is_initialised_then_migrated(tmp_path):
    run = Runner()
    init_migration("SQLModel", tmp_path, URL, run)
    assert [call[:2] for call in run.calls] == [
        ["alembic", "init"],
        ["alembic", "revision"],
        ["alembic", "upgrade"],
    ]


def test_a_tortoise_project_is_initialised_then_migrated(tmp_path):
    run = Runner()
    init_migration("Tortoise-ORM", tmp_path, "sqlite://dev.db", run)
    assert run.calls == [
        ["aerich", "init", "-t", "src.configs.db.TORTOISE_ORM"],
        ["aerich", "init-db"],
    ]


def test_without_a_url_the_tool_is_set_up_and_nothing_more(tmp_path):
    run = Runner()
    result = init_migration("SQLModel", tmp_path, None, run)
    assert [call[:2] for call in run.calls] == [["alembic", "init"]] and not result.done


def test_without_an_orm_nothing_runs(tmp_path):
    run = Runner()
    assert init_migration("None", tmp_path, URL, run).done is False and run.calls == []


def test_a_tool_that_did_not_initialise_is_not_migrated(tmp_path):
    def silent(args, _cwd):
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    result = init_migration("SQLModel", tmp_path, URL, silent)
    assert not result.done and "alembic" in result.problem


class TestReport:
    @pytest.fixture
    def said(self, monkeypatch):
        lines: list[str] = []
        monkeypatch.setattr(template_setup.console, "print", lambda text="": lines.append(text))
        return lines

    def test_it_says_when_the_tables_exist(self, said):
        template_setup._report_migration(first.FirstMigration(True))
        assert any("tables" in line for line in said)

    def test_it_gives_the_reason_when_it_could_not_run(self, said):
        template_setup._report_migration(first.FirstMigration(False, "cannot connect"))
        assert any("cannot connect" in line for line in said)

    def test_it_stays_quiet_when_nothing_was_tried(self, said):
        template_setup._report_migration(first.FirstMigration(False))
        assert said == []
