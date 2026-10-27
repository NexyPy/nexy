"""Which ORM a project uses, and the tool that migrates it."""

from __future__ import annotations

import importlib.util
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


def detect_orm(project: Path) -> Orm | None:
    """The ORM named in `nexyconfig.py`, else the first installed one; None when there is none."""
    config = project / "nexyconfig.py"
    if config.exists():
        text = config.read_text().lower()
        named = next((orm for orm in KNOWN if orm.package in text), None)
        if named:
            return named
    return next((orm for orm in KNOWN if importlib.util.find_spec(orm.package)), None)
