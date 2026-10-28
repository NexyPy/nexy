"""The Alembic files Nexy writes for a project: its `env.py` and the URL in `alembic.ini`."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from nexy.modules.cli.constants import TEMPLATES_DIR

_URL_LINE = re.compile(r"^sqlalchemy\.url\s*=.*", re.MULTILINE)


def models_module(project: Path) -> str:
    """The module that holds the models the scaffold wrote: `src/models`, or the users module."""
    if (project / "src" / "models").is_dir():
        return "src.models.user_model"
    return "src.apps.users.user_model"


def render_env(alembic_dir: Path, orm: str, models: str = "src.models.user_model") -> None:
    """Write `env.py` into *alembic_dir* from Nexy's template, for the project's ORM.

    *models* is the module whose import puts the tables on the metadata Alembic compares.
    """
    # Renders a Python code template, not HTML; autoescaping would corrupt the generated Python.
    # See SECURITY.md.
    environment = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR / "alembic")))  # nosec B701
    source = environment.get_template("env.py.jinja2").render(orm=orm, models=models)
    (alembic_dir / "env.py").write_text(source)
    if orm == "SQLModel":
        _import_sqlmodel_in_migrations(alembic_dir)


def _import_sqlmodel_in_migrations(alembic_dir: Path) -> None:
    """Make every new migration import `sqlmodel`: Alembic writes its column types as
    `sqlmodel.sql.sqltypes.AutoString()`, and applying the migration fails without the import."""
    template = alembic_dir / "script.py.mako"
    if not template.exists():
        return
    text = template.read_text(encoding="utf-8")
    if "import sqlmodel" in text:
        return
    marker = "import sqlalchemy as sa\n"
    template.write_text(text.replace(marker, marker + "import sqlmodel\n", 1), encoding="utf-8")


def write_ini_url(project: Path, database_url: str) -> None:
    """Point `alembic.ini` of *project* at *database_url*; a project without one is left alone."""
    ini = project / "alembic.ini"
    if not ini.exists():
        return
    text = _URL_LINE.sub(lambda _match: f"sqlalchemy.url = {database_url}", ini.read_text("utf-8"))
    ini.write_text(text, encoding="utf-8")
