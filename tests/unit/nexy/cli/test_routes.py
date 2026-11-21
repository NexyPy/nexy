"""Tests for the `nx routes` command."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from nexy.modules.cli import CLI

runner = CliRunner()


def test_routes_lists_the_project_routes(
    nexy_project,
    tmp_path: Path,
) -> None:
    nexy_project()

    routes_dir = tmp_path / "src" / "routes"
    routes_dir.mkdir(parents=True)

    (routes_dir / "index.nexy").write_text("<h1>Home</h1>", encoding="utf-8")

    (routes_dir / "users.py").write_text(
        "async def GET():\n"
        "    return {'users': []}\n",
        encoding="utf-8",
    )

    result = runner.invoke(CLI, ["routes"])

    assert result.exit_code == 0
    assert "/" in result.stdout
    assert "/users" in result.stdout
    assert "index.nexy" in result.stdout
    assert "users.py" in result.stdout


def test_routes_are_sorted_by_path(nexy_project, tmp_path: Path) -> None:
    nexy_project()

    routes_dir = tmp_path / "src" / "routes"
    routes_dir.mkdir(parents=True)

    (routes_dir.parent / "__init__.py").touch()
    (routes_dir / "__init__.py").touch()

    (routes_dir / "zebra.py").write_text(
        "async def GET():\n"
        "    return {'ok': True}\n",
        encoding="utf-8",
    )

    (routes_dir / "alpha.py").write_text(
        "async def GET():\n"
        "    return {'ok': True}\n",
        encoding="utf-8",
    )

    result = runner.invoke(CLI, ["routes"])

    assert result.exit_code == 0
    assert result.stdout.index("/alpha") < result.stdout.index("/zebra")


def test_routes_reports_when_no_routes_exist(nexy_project) -> None:
    nexy_project()

    result = runner.invoke(CLI, ["routes"])

    assert result.exit_code == 0
    assert "No routes found." in result.stdout