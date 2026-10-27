"""The Alembic files Nexy writes for a project: its `env.py` and the URL in `alembic.ini`."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from nexy.modules.cli.constants import TEMPLATES_DIR

_URL_LINE = re.compile(r"^sqlalchemy\.url\s*=.*", re.MULTILINE)


def render_env(alembic_dir: Path, orm: str) -> None:
    """Write `env.py` into *alembic_dir* from Nexy's template, for the project's ORM."""
    # Renders a Python code template, not HTML; autoescaping would corrupt the generated Python.
    # See SECURITY.md.
    environment = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR / "alembic")))  # nosec B701
    source = environment.get_template("env.py.jinja2").render(orm=orm)
    (alembic_dir / "env.py").write_text(source)


def write_ini_url(project: Path, database_url: str) -> None:
    """Point `alembic.ini` of *project* at *database_url*; a project without one is left alone."""
    ini = project / "alembic.ini"
    if not ini.exists():
        return
    text = _URL_LINE.sub(lambda _match: f"sqlalchemy.url = {database_url}", ini.read_text("utf-8"))
    ini.write_text(text, encoding="utf-8")
