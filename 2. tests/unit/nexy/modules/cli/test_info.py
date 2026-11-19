"""Tests for the `nx info` command."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from typer.testing import CliRunner

from nexy.__version__ import __version__
from nexy.helpers.common import package_manager
from nexy.modules.cli import CLI

runner = CliRunner()


def test_info_inside_project(monkeypatch, tmp_path: Path) -> None:
    (tmp_path / "nexyconfig.py").write_text("useFF = react()\n", encoding="utf-8")
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"react": "^19.2.0", "vue": "~3.5.13"}}),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(package_manager, "resolve", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(package_manager, "detect", lambda root=None: "pnpm")
    monkeypatch.setattr(package_manager, "version", lambda manager: (9, 15, 9))
    monkeypatch.setattr(
        "nexy.modules.cli.commands.info.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="v22.18.0\n"),
    )

    result = runner.invoke(CLI, ["info"])

    assert result.exit_code == 0
    assert f"Nexy        {__version__}" in result.stdout
    assert "Python      " in result.stdout
    assert "OS          " in result.stdout
    assert "Node        22.18.0" in result.stdout
    assert "Package     pnpm 9.15.9" in result.stdout
    assert "Router      file-based" in result.stdout
    assert "Frameworks  react 19.2.0, vue 3.5.13" in result.stdout


def test_info_outside_project_and_missing_node(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(package_manager, "resolve", lambda name: None)
    monkeypatch.setattr(package_manager, "detect", lambda root=None: None)

    result = runner.invoke(CLI, ["info"])

    assert result.exit_code == 0
    assert "Node        not found" in result.stdout
    assert "Package     not found" in result.stdout
    assert "Router      not found" in result.stdout
    assert "Frameworks  not found" in result.stdout
