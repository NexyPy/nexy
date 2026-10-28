"""The first migration of a new project: its tables exist before the first `nexy dev`.

A project made with an ORM and a database URL has models but no tables, so its first page that
reads the database fails until someone runs `nexy migrate`. `nx new` runs those two commands itself
when it can, and says why when it cannot.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from nexy.modules.cli.migrations.database import connection_problem

Runner = Callable[[list[str], Path], "subprocess.CompletedProcess[str]"]

# Alembic writes the migration, then applies it. Aerich does both in `init-db`.
_COMMANDS: dict[str, list[list[str]]] = {
    "alembic": [
        ["alembic", "revision", "--autogenerate", "-m", "create tables"],
        ["alembic", "upgrade", "head"],
    ],
    "aerich": [["aerich", "init-db"]],
}
_SAID_LENGTH = 300


@dataclass(frozen=True)
class FirstMigration:
    """`done` when the tables exist; `problem` says why not, and is empty when nothing was tried."""

    done: bool
    problem: str = ""


def _in_project(url: str, dest: Path) -> str:
    """Anchor a relative SQLite file in the project: `nx new` runs from its parent folder."""
    try:
        from sqlalchemy.engine import make_url

        parsed = make_url(url)
    except Exception:  # not a SQLAlchemy URL, or SQLAlchemy is missing: checked as given
        return url
    database = parsed.database
    if not parsed.drivername.startswith("sqlite") or not database or database == ":memory:":
        return url
    if Path(database).is_absolute():
        return url
    return parsed.set(database=(dest / database).as_posix()).render_as_string(hide_password=False)


def _unreachable(url: str, dest: Path) -> str:
    """Why SQLAlchemy cannot use *url*, or an empty string."""
    problem = connection_problem(_in_project(url, dest))
    if problem is None:
        return ""
    kind, error = problem
    what = "missing database driver" if kind == "driver" else "cannot connect to the database"
    return f"{what} - {error}"


def _said(args: list[str], result: subprocess.CompletedProcess[str]) -> str:
    """What the tool printed, shortened, or at least which command failed."""
    output = (result.stderr or result.stdout or "").strip()
    return output[-_SAID_LENGTH:] or f"`{' '.join(args)}` exited with {result.returncode}"


def run_first_migration(tool: str, dest: Path, url: str | None, run: Runner) -> FirstMigration:
    """Create the first migration and the tables of the project in *dest*.

    Only Alembic's URLs are checked up front: they are SQLAlchemy URLs. Aerich's are Tortoise's
    (`postgres://...`), which SQLAlchemy cannot read, so Aerich reports its own failure.
    """
    if not url:
        return FirstMigration(False)
    if tool == "alembic":
        problem = _unreachable(url, dest)
        if problem:
            return FirstMigration(False, problem)
    for args in _COMMANDS[tool]:
        result = run(args, dest)
        if result.returncode != 0:
            return FirstMigration(False, _said(args, result))
    return FirstMigration(True)
