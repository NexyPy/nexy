"""The installer looks at the connection first, and names the tool and the folder it fills."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from nexy.helpers.common.network import Connection
from nexy.modules.cli.init import dependencies
from nexy.modules.cli.init.dependencies import DependencyInstaller

positions: list = []
done_lines: list = []


@pytest.fixture
def calls(monkeypatch):
    """Every task the installer runs: (label, argv)."""
    seen: list[tuple[str, list[str]]] = []
    positions.clear()
    done_lines.clear()

    def fake_run_task(label, argv, cwd=None, done=None, progress=None):
        seen.append((label, list(argv)))
        positions.append(progress)
        done_lines.append(done)
        return SimpleNamespace(ok=True)

    monkeypatch.setattr(dependencies, "run_task", fake_run_task)
    monkeypatch.setattr(dependencies.shutil, "which", lambda name: f"/bin/{name}")
    return seen


@pytest.fixture
def project(tmp_path):
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "vite.config.ts").write_text("")
    (tmp_path / "pyproject.toml").write_text("")
    return tmp_path


def _installer(project, connection):
    return DependencyInstaller(project, probe=lambda: connection)


class TestOffline:
    def test_nothing_is_installed(self, project, calls):
        _installer(project, Connection(False, None, None)).install_all()
        assert calls == []

    def test_the_user_is_told_and_given_the_way_to_install_later(self, project, calls, capsys):
        _installer(project, Connection(False, None, None)).install_all()
        out = capsys.readouterr().out
        assert "No connection" in out and "uv sync" in out


class TestOnline:
    def test_the_latency_and_speed_are_reported(self, project, calls, capsys):
        _installer(project, Connection(True, 42.0, 2500.0)).install_all()
        out = capsys.readouterr().out
        assert "42 ms" in out and "2.5 MB/s" in out

    def test_a_missing_speed_still_reports_the_latency(self, project, calls, capsys):
        _installer(project, Connection(True, 42.0, None)).install_all()
        assert "42 ms" in capsys.readouterr().out

    def test_a_slow_connection_is_a_warning(self, project, calls, capsys):
        _installer(project, Connection(True, 900.0, 20.0)).install_all()
        assert "Slow connection" in capsys.readouterr().out

    def test_a_good_connection_has_no_warning(self, project, calls, capsys):
        _installer(project, Connection(True, 30.0, 3000.0)).install_all()
        assert "Slow connection" not in capsys.readouterr().out


class TestLabels:
    def _labels(self, project, calls):
        _installer(project, Connection(True, 30.0, 3000.0)).install_all()
        return [label for label, _ in calls]

    def test_node_names_the_manager_and_the_folder(self, project, calls, monkeypatch):
        monkeypatch.setattr(dependencies.package_manager, "detect", lambda d: "pnpm")
        assert "pnpm install node_modules" in self._labels(project, calls)

    def test_python_names_uv_and_the_environment(self, project, calls):
        assert "uv sync .venv" in self._labels(project, calls)


class TestDoneLines:
    """The line a finished step leaves says what was done, as uv does."""

    def _done(self, project, calls):
        _installer(project, Connection(True, 30.0, 3000.0)).install_all()
        return done_lines

    def test_node_says_what_it_installed_and_with_what(self, project, calls, monkeypatch):
        monkeypatch.setattr(dependencies.package_manager, "detect", lambda d: "pnpm")
        assert "Installed node_modules with pnpm" in self._done(project, calls)

    def test_python_says_it_synced_the_environment(self, project, calls):
        assert "Synced .venv with uv" in self._done(project, calls)


class TestWarnings:
    def test_no_node_manager_is_a_warning(self, project, calls, monkeypatch, capsys):
        monkeypatch.setattr(dependencies.package_manager, "detect", lambda d: None)
        _installer(project, Connection(True, 30.0, 3000.0)).install_all()
        assert "warning: No Node.js package manager found" in capsys.readouterr().out

    def test_adding_a_package_without_a_manager_is_a_warning(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(dependencies.package_manager, "detect", lambda d: None)
        dependencies.install_packages(["zod"], tmp_path)
        assert capsys.readouterr().out.startswith("warning: No package manager found")


class TestOrmPackages:
    """What an ORM needs, written to pyproject.toml so that `uv sync` installs it."""

    def test_postgresql_adds_its_driver_after_the_orm(self):
        packages = dependencies.orm_packages("SQLModel", "neon")
        assert packages == ["sqlmodel", "alembic", "psycopg[binary]", "python-dotenv"]

    @pytest.mark.parametrize("orm", ["SQLModel", "SQLAlchemy"])
    def test_a_sql_orm_brings_alembic(self, orm):
        assert "alembic" in dependencies.orm_packages(orm, "sqlite")

    def test_tortoise_brings_aerich(self):
        assert "aerich" in dependencies.orm_packages("Tortoise-ORM", "sqlite")

    def test_tortoise_brings_the_zone_data_windows_lacks(self):
        assert "tzdata; sys_platform == 'win32'" in dependencies.orm_packages(
            "Tortoise-ORM", "sqlite"
        )

    def test_a_project_without_an_orm_brings_no_package(self):
        assert dependencies.orm_packages("None", "sqlite") == []

    def test_the_install_adds_no_package_one_by_one(self, project, calls):
        _installer(project, Connection(True, 30.0, 3000.0)).install_all()
        assert [argv for _, argv in calls if argv[:2] == ["uv", "add"]] == []


class TestProgressBar:
    def test_each_step_knows_its_place_in_the_whole_install(self, project, calls):
        _installer(project, Connection(True, 30.0, 3000.0)).install_all()
        # venv, node, python: the ORM's packages come with the python step
        assert positions == [(0, 3), (1, 3), (2, 3)]

    def test_a_single_step_has_no_count(self, tmp_path, calls):
        (tmp_path / ".venv").mkdir()
        (tmp_path / "pyproject.toml").write_text("")
        _installer(tmp_path, Connection(True, 30.0, 3000.0)).install_all()
        assert positions == [None]


class TestWhileTheConnectionIsChecked:
    """The check can take seconds: something must say so, and stop before the result is printed."""

    @staticmethod
    def _status_log(monkeypatch):
        log: list[str] = []

        class Spinner:
            def __enter__(self):
                log.append("shown")

            def __exit__(self, *_exc):
                log.append("hidden")

        monkeypatch.setattr(
            dependencies.console, "status", lambda text, **_kw: (log.append(text), Spinner())[1]
        )
        return log

    def test_a_spinner_says_the_connection_is_being_checked(self, project, calls, monkeypatch):
        log = self._status_log(monkeypatch)
        _installer(project, Connection(True, 30.0, 3000.0)).install_all()
        assert log[0] == "Checking the connection..."

    def test_the_spinner_is_gone_before_the_result_is_printed(self, project, calls, monkeypatch):
        log = self._status_log(monkeypatch)
        seen_at_probe: list[list[str]] = []

        def probe() -> Connection:
            seen_at_probe.append(list(log))
            return Connection(True, 30.0, 3000.0)

        DependencyInstaller(project, probe=probe).install_all()
        assert seen_at_probe == [["Checking the connection...", "shown"]] and log[-1] == "hidden"


class TestNpmRetry:
    def test_a_failed_npm_install_is_retried_with_legacy_peer_deps(self, project, monkeypatch):
        seen: list[list[str]] = []

        def failing(label, argv, cwd=None, done=None, progress=None):
            seen.append(list(argv))
            return SimpleNamespace(ok=False)

        monkeypatch.setattr(dependencies, "run_task", failing)
        monkeypatch.setattr(dependencies.package_manager, "detect", lambda d: "npm")
        _installer(project, Connection(True, 30.0, 3000.0)).install_node_dependencies()
        assert seen[-1][-1] == "--legacy-peer-deps"


def test_adding_a_package_runs_the_add_command_of_the_manager(tmp_path, calls, monkeypatch):
    monkeypatch.setattr(dependencies.package_manager, "detect", lambda d: "pnpm")
    dependencies.install_packages(["zod"], tmp_path)
    assert calls[-1][1] == dependencies.package_manager.add_argv("pnpm", ["zod"])
