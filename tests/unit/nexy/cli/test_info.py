"""Tests for the `nx info` command."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from nexy.__version__ import __version__
from nexy.helpers.common import package_manager
from nexy.modules.cli import CLI

runner = CliRunner()
info_module = importlib.import_module("nexy.modules.cli.commands.info")


def _raise_os_error(*_args: object, **_kwargs: object) -> object:
    raise OSError("boom")


@pytest.fixture
def project_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    (tmp_path / "nexyconfig.py").write_text("useFF = react()\n", encoding="utf-8")
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"react": "^19.2.0", "vue": "~3.5.13"}}),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(package_manager, "resolve", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(package_manager, "detect", lambda _root=None: "pnpm")
    monkeypatch.setattr(package_manager, "version", lambda _manager: (9, 15, 9))
    monkeypatch.setattr(
        info_module.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=0, stdout="v22.18.0\n"),
    )
    return tmp_path


@pytest.fixture
def empty_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(package_manager, "resolve", lambda _name: None)
    monkeypatch.setattr(package_manager, "detect", lambda _root=None: None)
    return tmp_path


@pytest.mark.usefixtures("project_env")
def test_info_exits_cleanly_inside_project() -> None:
    result = runner.invoke(CLI, ["info"])
    assert result.exit_code == 0


@pytest.mark.usefixtures("project_env")
def test_info_prints_the_nexy_version() -> None:
    result = runner.invoke(CLI, ["info"])
    assert f"Nexy        {__version__}" in result.stdout


@pytest.mark.usefixtures("project_env")
def test_info_prints_the_python_version() -> None:
    result = runner.invoke(CLI, ["info"])
    assert "Python      " in result.stdout


@pytest.mark.usefixtures("project_env")
def test_info_prints_the_os() -> None:
    result = runner.invoke(CLI, ["info"])
    assert "OS          " in result.stdout


@pytest.mark.usefixtures("project_env")
def test_info_prints_the_node_version() -> None:
    result = runner.invoke(CLI, ["info"])
    assert "Node        22.18.0" in result.stdout


@pytest.mark.usefixtures("project_env")
def test_info_prints_the_package_manager() -> None:
    result = runner.invoke(CLI, ["info"])
    assert "Package     pnpm 9.15.9" in result.stdout


@pytest.mark.usefixtures("project_env")
def test_info_prints_the_router() -> None:
    result = runner.invoke(CLI, ["info"])
    assert "Router      file-based" in result.stdout


@pytest.mark.usefixtures("project_env")
def test_info_prints_the_frameworks() -> None:
    result = runner.invoke(CLI, ["info"])
    assert "Frameworks  react 19.2.0, vue 3.5.13" in result.stdout


@pytest.mark.usefixtures("empty_env")
def test_info_says_node_is_not_found() -> None:
    result = runner.invoke(CLI, ["info"])
    assert "Node        not found" in result.stdout


@pytest.mark.usefixtures("empty_env")
def test_info_says_package_is_not_found() -> None:
    result = runner.invoke(CLI, ["info"])
    assert "Package     not found" in result.stdout


@pytest.mark.usefixtures("empty_env")
def test_info_says_router_is_not_found() -> None:
    result = runner.invoke(CLI, ["info"])
    assert "Router      not found" in result.stdout


@pytest.mark.usefixtures("empty_env")
def test_info_says_frameworks_are_not_found() -> None:
    result = runner.invoke(CLI, ["info"])
    assert "Frameworks  not found" in result.stdout


@pytest.mark.usefixtures("project_env")
def test_info_says_node_is_not_found_on_os_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(info_module.subprocess, "run", _raise_os_error)
    result = runner.invoke(CLI, ["info"])
    assert "Node        not found" in result.stdout


@pytest.mark.usefixtures("project_env")
def test_info_says_node_is_not_found_on_nonzero_exit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        info_module.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=1, stdout="v22.0.0\n"),
    )
    result = runner.invoke(CLI, ["info"])
    assert "Node        not found" in result.stdout


@pytest.mark.usefixtures("project_env")
def test_info_prints_package_manager_name_without_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(package_manager, "version", lambda _manager: None)
    result = runner.invoke(CLI, ["info"])
    assert "Package     pnpm\n" in result.stdout


@pytest.mark.usefixtures("project_env")
def test_info_prints_non_fbr_router(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        info_module,
        "detect_profile",
        lambda _root: SimpleNamespace(router="modular"),
    )
    result = runner.invoke(CLI, ["info"])
    assert "Router      modular" in result.stdout


@pytest.mark.usefixtures("project_env")
def test_info_says_frameworks_are_not_found_on_invalid_json(
    project_env: Path,
) -> None:
    (project_env / "package.json").write_text("{", encoding="utf-8")
    result = runner.invoke(CLI, ["info"])
    assert "Frameworks  not found" in result.stdout
