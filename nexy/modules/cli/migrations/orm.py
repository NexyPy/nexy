"""Which ORM a project uses, and the tool that migrates it."""

from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Orm:
    name: str
    tool: str
    package: str


KNOWN = (
    Orm("SQLModel", "alembic", "sqlmodel"),
    Orm("Tortoise-ORM", "aerich", "tortoise"),
    Orm("SQLAlchemy", "alembic", "sqlalchemy"),
)


# `useORM = "SQLAlchemy"` in `nexyconfig.py`, read as text: the config may import `src`.
_USE_ORM = re.compile(r"""^\s*useORM\s*=\s*["']([^"']+)["']""", re.MULTILINE)


def _named_orm(text: str) -> Orm | None:
    """The ORM `useORM` names, else the first ORM package the config mentions."""
    found = _USE_ORM.search(text)
    if found:
        return next((orm for orm in KNOWN if orm.name == found.group(1)), None)
    return next((orm for orm in KNOWN if orm.package in text.lower()), None)


def detect_orm(project: Path) -> Orm | None:
    """The ORM named in `nexyconfig.py`, else the first installed one; None when there is none."""
    config = project / "nexyconfig.py"
    named = _named_orm(config.read_text(encoding="utf-8")) if config.exists() else None
    if named:
        return named
    return next((orm for orm in KNOWN if importlib.util.find_spec(orm.package)), None)
