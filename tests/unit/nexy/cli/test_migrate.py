"""`nx migrate`: find the ORM, check the project is ready, run the migration tool."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from nexy.modules.cli import CLI
from nexy.modules.cli.migrations import alembic, database, orm

migrate_module = importlib.import_module("nexy.modules.cli.commands.migrate")
runner = CliRunner()


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(orm.importlib.util, "find_spec", lambda _name: None)
    return tmp_path


@pytest.fixture
def tools(monkeypatch) -> list[tuple[str, list[str]]]:
    calls: list[tuple[str, list[str]]] = []
    monkeypatch.setattr(
        migrate_module, "run_tool", lambda tool, args: calls.append((tool, args)) or 0
    )
    return calls


class TestDetectOrm:
    def test_nothing_is_found_in_an_empty_project(self, project):
        assert orm.detect_orm(project) is None

    @pytest.mark.parametrize(
        ("text", "name", "tool"),
        [
            ("import sqlmodel", "SQLModel", "alembic"),
            ("from tortoise import Tortoise", "Tortoise-ORM", "aerich"),
            ("import sqlalchemy", "SQLAlchemy", "alembic"),
        ],
    )
    def test_the_config_names_the_orm(self, project, text, name, tool):
        (project / "nexyconfig.py").write_text(text, encoding="utf-8")
        found = orm.detect_orm(project)
        assert found is not None and (found.name, found.tool) == (name, tool)

    def test_sqlmodel_wins_over_sqlalchemy_which_it_builds_on(self, project):
        (project / "nexyconfig.py").write_text("sqlmodel sqlalchemy", encoding="utf-8")
        found = orm.detect_orm(project)
        assert found is not None and found.name == "SQLModel"

    def test_an_installed_orm_is_used_when_the_config_names_none(self, project, monkeypatch):
        monkeypatch.setattr(
            orm.importlib.util, "find_spec", lambda name: name == "tortoise" or None
        )
        found = orm.detect_orm(project)
        assert found is not None and found.tool == "aerich"


class TestAlembic:
    def test_the_url_line_of_the_ini_is_replaced(self, tmp_path):
        (tmp_path / "alembic.ini").write_text(
            "a = 1\nsqlalchemy.url = old\nb = 2\n", encoding="utf-8"
        )
        alembic.write_ini_url(tmp_path, "sqlite:///x.db")
        text = (tmp_path / "alembic.ini").read_text(encoding="utf-8")
        assert "sqlalchemy.url = sqlite:///x.db" in text and "old" not in text and "b = 2" in text

    def test_a_url_with_backslashes_is_written_as_it_is(self, tmp_path):
        (tmp_path / "alembic.ini").write_text("sqlalchemy.url = old\n", encoding="utf-8")
        alembic.write_ini_url(tmp_path, r"sqlite:///C:\data\x.db")
        assert r"C:\data\x.db" in (tmp_path / "alembic.ini").read_text(encoding="utf-8")

    def test_a_project_without_an_ini_is_left_alone(self, tmp_path):
        alembic.write_ini_url(tmp_path, "sqlite://")
        assert not (tmp_path / "alembic.ini").exists()

    def test_env_py_is_written_for_the_orm(self, tmp_path):
        alembic.render_env(tmp_path, "SQLModel")
        assert "SQLModel" in (tmp_path / "env.py").read_text()


class TestDatabase:
    def test_the_url_comes_from_the_environment(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "sqlite://")
        assert database.database_url(tmp_path) == "sqlite://"

    def test_no_url_is_none(self, tmp_path, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        assert database.database_url(tmp_path) is None

    def test_a_working_sqlite_database_has_no_problem(self, tmp_path):
        assert database.connection_problem(f"sqlite:///{(tmp_path / 'ok.db').as_posix()}") is None

    def test_without_sqlalchemy_the_driver_is_missing(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "sqlalchemy", None)
        problem = database.connection_problem("sqlite://")
        assert problem is not None and problem[0] == "driver"

    def test_an_unreachable_database_is_a_connection_problem(self):
        problem = database.connection_problem("sqlite:////nonexistent-folder/x/y.db")
        assert problem is not None and problem[0] == "connection"


class TestCommand:
    @pytest.mark.usefixtures("project")
    def test_without_an_orm_it_says_so_and_fails(self):
        result = runner.invoke(CLI, ["migrate"])
        assert result.exit_code == 1 and "No supported ORM" in result.output

    def test_init_runs_alembic_for_a_sql_orm(self, project, tools):
        (project / "nexyconfig.py").write_text("sqlmodel", encoding="utf-8")
        runner.invoke(CLI, ["migrate", "--init"])
        assert tools == [("alembic", ["init", "alembic"])]

    def test_init_runs_aerich_for_tortoise(self, project, tools):
        (project / "nexyconfig.py").write_text("tortoise", encoding="utf-8")
        runner.invoke(CLI, ["migrate", "--init"])
        assert tools[0][0] == "aerich"

    def test_an_uninitialized_project_is_asked_to_init(self, project, tools):
        (project / "nexyconfig.py").write_text("sqlmodel", encoding="utf-8")
        result = runner.invoke(CLI, ["migrate"])
        assert result.exit_code == 1 and "--init" in result.output and tools == []

    def test_a_missing_database_url_is_reported(self, project, tools):
        (project / "nexyconfig.py").write_text("sqlmodel", encoding="utf-8")
        (project / "alembic.ini").write_text("", encoding="utf-8")
        result = runner.invoke(CLI, ["migrate"])
        assert result.exit_code == 1 and "DATABASE_URL" in result.output and tools == []

    def test_a_ready_project_generates_a_revision(self, project, tools, monkeypatch):
        monkeypatch.setattr(migrate_module, "connection_problem", lambda _url: None)
        (project / "nexyconfig.py").write_text("sqlmodel", encoding="utf-8")
        (project / "alembic.ini").write_text("", encoding="utf-8")
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{(project / 'ok.db').as_posix()}")
        runner.invoke(CLI, ["migrate", "-m", "add users"])
        assert tools == [("alembic", ["revision", "--autogenerate", "-m", "add users"])]

    def test_upgrade_goes_to_head(self, project, tools, monkeypatch):
        monkeypatch.setattr(migrate_module, "connection_problem", lambda _url: None)
        (project / "nexyconfig.py").write_text("sqlmodel", encoding="utf-8")
        (project / "alembic.ini").write_text("", encoding="utf-8")
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{(project / 'ok.db').as_posix()}")
        runner.invoke(CLI, ["migrate", "--upgrade"])
        assert tools == [("alembic", ["upgrade", "head"])]

    def test_a_tool_that_is_not_installed_is_reported(self, project, monkeypatch):
        (project / "nexyconfig.py").write_text("sqlmodel", encoding="utf-8")
        monkeypatch.setattr(migrate_module, "run_tool", lambda _tool, _args: None)
        result = runner.invoke(CLI, ["migrate", "--init"])
        assert result.exit_code == 1 and "not found on PATH" in result.output
