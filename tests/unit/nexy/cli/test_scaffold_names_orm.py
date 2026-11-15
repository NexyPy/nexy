"""`nx new` writes the ORM it scaffolded into `nexyconfig.py`, so `nx migrate` never guesses it.

The guess took the first ORM package installed: a SQLAlchemy project whose environment also held
sqlmodel got the SQLModel alembic env.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.modules.cli.init.template_setup import _render_local_template
from nexy.modules.cli.migrations.orm import detect_orm

TEMPLATES = ["web-fbr", "web-modular", "api-fbr", "api-modular"]


def _scaffold(dest: Path, template: str, orm: str) -> None:
    config = {
        "project_type": template.split("-")[0],
        "FBRouter": template.endswith("fbr"),
        "useCSR": False,
        "client_framework": "none",
        "orm": orm,
    }
    _render_local_template(template, dest, config, "demo")


@pytest.mark.parametrize("template", TEMPLATES)
@pytest.mark.parametrize("orm", ["SQLModel", "SQLAlchemy", "Tortoise-ORM"])
def test_a_scaffold_names_its_orm_whatever_is_installed(tmp_path, monkeypatch, template, orm):
    monkeypatch.setattr("importlib.util.find_spec", lambda _name: True)
    _scaffold(tmp_path, template, orm)
    found = detect_orm(tmp_path)
    assert found is not None and found.name == orm


@pytest.mark.parametrize("template", TEMPLATES)
def test_a_scaffold_without_an_orm_names_none(tmp_path, template):
    _scaffold(tmp_path, template, "None")
    assert "useORM" not in (tmp_path / "nexyconfig.py").read_text(encoding="utf-8")
