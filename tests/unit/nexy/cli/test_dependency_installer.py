"""The installer looks at the connection first, and names the tool and the folder it fills."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from nexy.helpers.common.network import Connection
from nexy.modules.cli.init import dependencies
from nexy.modules.cli.init.dependencies import DependencyInstaller

positions: list = []


@pytest.fixture
def calls(monkeypatch):
    """Every task the installer runs: (label, argv)."""
    seen: list[tuple[str, list[str]]] = []
    positions.clear()

    def fake_run_task(label, argv, cwd=None, done=None, progress=None):
        seen.append((label, list(argv)))
        positions.append(progress)
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


def _installer(project, connection, orm=None):
    return DependencyInstaller(project, orm=orm, probe=lambda: connection)


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
    def _labels(self, project, calls, orm=None):
        _installer(project, Connection(True, 30.0, 3000.0), orm=orm).install_all()
        return [label for label, _ in calls]

    def test_node_names_the_manager_and_the_folder(self, project, calls, monkeypatch):
        monkeypatch.setattr(dependencies.package_manager, "detect", lambda d: "pnpm")
        assert "pnpm install node_modules" in self._labels(project, calls)

    def test_python_names_uv_and_the_environment(self, project, calls):
        assert "uv sync .venv" in self._labels(project, calls)

    def test_a_package_names_uv_the_environment_and_the_package(self, project, calls):
        assert "uv add .venv sqlmodel" in self._labels(project, calls, orm="SQLModel")


class TestDatabaseDrivers:
    def test_postgresql_adds_its_driver_after_the_orm(self, project, calls):
        installer = DependencyInstaller(
            project,
            orm="SQLModel",
            database="neon",
            probe=lambda: Connection(True, 30.0, 3000.0),
        )
        installer.install_all()
        added = [argv[-1] for _, argv in calls if argv[:2] == ["uv", "add"]]
        assert added == ["sqlmodel", "psycopg[binary]", "python-dotenv"]


class TestProgressBar:
    def test_each_step_knows_its_place_in_the_whole_install(self, project, calls):
        _installer(project, Connection(True, 30.0, 3000.0), orm="SQLModel").install_all()
        # venv, node, python, sqlmodel, python-dotenv
        assert positions == [(0, 5), (1, 5), (2, 5), (3, 5), (4, 5)]

    def test_a_single_step_has_no_count(self, tmp_path, calls):
        (tmp_path / ".venv").mkdir()
        (tmp_path / "pyproject.toml").write_text("")
        _installer(tmp_path, Connection(True, 30.0, 3000.0)).install_all()
        assert positions == [None]
