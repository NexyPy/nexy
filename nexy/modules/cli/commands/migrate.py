from pathlib import Path

import typer

from nexy.helpers.common.process import run_tool
from nexy.modules.cli.migrations import alembic
from nexy.modules.cli.migrations.database import connection_problem, database_url
from nexy.modules.cli.migrations.orm import Orm, detect_orm
from nexy.modules.i18n import t

_AERICH_CONFIG = "src.configs.db.TORTOISE_ORM"
# What `init` leaves behind: Alembic writes alembic.ini; Aerich writes its settings into
# pyproject.toml and creates the migrations folder.
_INIT_FILES = {"alembic": "alembic.ini", "aerich": "migrations"}


def _run_tool(tool: str, args: list[str]) -> int:
    returncode = run_tool(tool, args)
    if returncode is None:
        message = t(
            "migrate.tool_missing", "Error: {tool} not found on PATH. Install it and try again."
        )
        typer.echo(message.format(tool=tool))
        raise typer.Exit(1)
    return returncode


def _fail(message: str) -> typer.Exit:
    typer.echo(message)
    return typer.Exit(1)


def _require_orm(project: Path) -> Orm:
    orm = detect_orm(project)
    if orm is None:
        raise _fail(
            t(
                "migrate.no_orm",
                "No supported ORM found. Install one: sqlmodel, tortoise-orm, sqlalchemy",
            )
        )
    return orm


def _initialize(orm: Orm, project: Path) -> None:
    """Set the migration tool up: Alembic with Nexy's `env.py` and URL, or Aerich."""
    if orm.tool == "aerich":
        _run_tool("aerich", ["init", "-t", _AERICH_CONFIG])
        return
    _run_tool("alembic", ["init", "alembic"])
    if (project / "alembic").exists():
        alembic.render_env(project / "alembic", orm.name, alembic.models_module(project))
    url = database_url(project)
    if url:
        alembic.write_ini_url(project, url)


def _require_initialized(orm: Orm, project: Path) -> None:
    if (project / _INIT_FILES[orm.tool]).exists():
        return
    messages = {
        "alembic": t(
            "migrate.alembic_not_initialized", "Alembic not initialized. Run 'nx m --init' first."
        ),
        "aerich": t(
            "migrate.aerich_not_initialized", "Aerich not initialized. Run 'nx m --init' first."
        ),
    }
    raise _fail(messages[orm.tool])


def _require_database(orm: Orm, project: Path) -> None:
    """Alembic's URL is a SQLAlchemy one and can be tried; Aerich's is Tortoise's: it reports."""
    if orm.tool == "aerich":
        return
    url = database_url(project)
    if not url:
        raise _fail(
            t("migrate.no_database_url", "Error: DATABASE_URL not found in .env or environment.")
        )
    problem = connection_problem(url)
    if problem is None:
        return
    kind, error = problem
    if kind == "driver":
        message = t("migrate.no_driver", "Error: Missing database driver - {error}")
    else:
        message = t("migrate.no_connection", "Error: Cannot connect to database - {error}")
    raise _fail(message.format(error=error)) from error


def _arguments(orm: Orm, project: Path, message: str, upgrade: bool) -> list[str]:
    """The arguments of the tool to apply migrations or to create one: they differ per tool."""
    if orm.tool == "alembic":
        if upgrade:
            return ["upgrade", "head"]
        return ["revision", "--autogenerate", *(["-m", message] if message else [])]
    if upgrade:
        return ["upgrade"]
    first = not any(path.is_dir() for path in (project / "migrations").iterdir())
    return ["init-db"] if first else ["migrate", "--name", message or "update"]


def migrate(
    message: str = typer.Option(
        "", "--message", "-m", help=t("migrate.help_message", "Migration message")
    ),
    init: bool = typer.Option(
        False, "--init", help=t("migrate.help_init", "Initialize migration tool")
    ),
    upgrade: bool = typer.Option(
        False, "--upgrade", "-u", help=t("migrate.help_upgrade", "Apply pending migrations")
    ),
) -> None:
    project = Path.cwd()
    orm = _require_orm(project)
    typer.echo(f"-- {orm.name} ({orm.tool}) --")
    if init:
        _initialize(orm, project)
        return
    _require_initialized(orm, project)
    _require_database(orm, project)
    _run_tool(orm.tool, _arguments(orm, project, message, upgrade))
