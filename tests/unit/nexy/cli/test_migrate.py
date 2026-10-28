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


class TestAerichCommands:
    """Aerich has its own commands: no `revision`, no `head`, no `aerich.ini`."""

    @staticmethod
    def _tortoise(project: Path) -> None:
        (project / "nexyconfig.py").write_text("tortoise", encoding="utf-8")

    def test_the_migrations_folder_marks_an_initialised_project(self, project, tools):
        self._tortoise(project)
        (project / "migrations").mkdir()
        result = runner.invoke(CLI, ["migrate"])
        assert "--init" not in result.output and tools != []

    def test_the_first_migration_creates_the_tables_too(self, project, tools):
        self._tortoise(project)
        (project / "migrations").mkdir()
        runner.invoke(CLI, ["migrate"])
        assert tools == [("aerich", ["init-db"])]

    def test_later_migrations_are_named(self, project, tools):
        self._tortoise(project)
        (project / "migrations" / "models").mkdir(parents=True)
        runner.invoke(CLI, ["migrate", "-m", "add users"])
        assert tools == [("aerich", ["migrate", "--name", "add users"])]

    def test_upgrade_takes_no_target(self, project, tools):
        self._tortoise(project)
        (project / "migrations" / "models").mkdir(parents=True)
        runner.invoke(CLI, ["migrate", "--upgrade"])
        assert tools == [("aerich", ["upgrade"])]

    def test_a_tortoise_url_is_not_checked_with_sqlalchemy(self, project, tools, monkeypatch):
        self._tortoise(project)
        (project / "migrations" / "models").mkdir(parents=True)
        monkeypatch.setenv("DATABASE_URL", "postgres://user:password@localhost:5432/mydb")
        runner.invoke(CLI, ["migrate", "--upgrade"])
        assert tools == [("aerich", ["upgrade"])]


class TestAlembicEnv:
    """Autogenerate compares the database with the models: env.py must import them."""

    @staticmethod
    def _env(tmp_path: Path, orm: str, models: str = "src.models.user_model") -> str:
        alembic.render_env(tmp_path, orm, models)
        return (tmp_path / "env.py").read_text(encoding="utf-8")

    def test_sqlmodel_imports_the_module_that_holds_the_models(self, tmp_path):
        assert "import src.apps.users.user_model" in self._env(
            tmp_path, "SQLModel", "src.apps.users.user_model"
        )

    def test_sqlalchemy_takes_its_base_from_the_module_that_holds_the_models(self, tmp_path):
        env = self._env(tmp_path, "SQLAlchemy", "src.apps.users.user_model")
        assert "from src.apps.users.user_model import Base" in env

    def test_the_old_import_of_an_empty_package_is_gone(self, tmp_path):
        assert "from src.models import Base" not in self._env(tmp_path, "SQLAlchemy")

    def test_a_file_based_project_keeps_its_models_in_src_models(self, tmp_path):
        (tmp_path / "src" / "models").mkdir(parents=True)
        assert alembic.models_module(tmp_path) == "src.models.user_model"

    def test_a_modular_project_keeps_them_with_the_users_module(self, tmp_path):
        assert alembic.models_module(tmp_path) == "src.apps.users.user_model"


class TestMigrationTemplate:
    """SQLModel columns are written as `sqlmodel.sql.sqltypes...`: a migration must import it."""

    MAKO = "import sqlalchemy as sa\nfrom alembic import op\n"

    @staticmethod
    def _mako(tmp_path: Path, orm: str, text: str = MAKO) -> str:
        (tmp_path / "script.py.mako").write_text(text, encoding="utf-8")
        alembic.render_env(tmp_path, orm)
        return (tmp_path / "script.py.mako").read_text(encoding="utf-8")

    def test_a_sqlmodel_migration_imports_sqlmodel(self, tmp_path):
        assert "import sqlmodel" in self._mako(tmp_path, "SQLModel")

    def test_the_import_is_added_once(self, tmp_path):
        text = self._mako(tmp_path, "SQLModel")
        alembic.render_env(tmp_path, "SQLModel")
        assert (tmp_path / "script.py.mako").read_text(encoding="utf-8") == text

    def test_a_sqlalchemy_migration_is_left_alone(self, tmp_path):
        assert self._mako(tmp_path, "SQLAlchemy") == self.MAKO

    def test_a_folder_without_the_template_is_fine(self, tmp_path):
        alembic.render_env(tmp_path, "SQLModel")
        assert (tmp_path / "env.py").is_file()
