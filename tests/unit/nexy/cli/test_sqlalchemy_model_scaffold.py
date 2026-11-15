"""A scaffolded SQLAlchemy model names every constraint it declares.

Alembic can drop or rebuild only a constraint it can name: SQLite batch mode refuses an unnamed
one ("Constraint must have a name"), and a downgrade renders `drop_constraint(None)` on every
database. The convention lives on the scaffold's `Base`, because it applies when a table is
declared, and `Base` is declared in the same module as the first model.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from nexy.modules.cli.init.template_setup import _render_local_template

# (template, the model file it writes)
TEMPLATES = [
    ("web-fbr", "src/models/user_model.py"),
    ("api-fbr", "src/models/user_model.py"),
    ("web-modular", "src/apps/users/user_model.py"),
    ("api-modular", "src/apps/users/user_model.py"),
]


def _users_table(tmp_path: Path, template: str, model: str):
    config = {
        "project_type": template.split("-")[0],
        "FBRouter": template.endswith("fbr"),
        "useCSR": False,
        "client_framework": "none",
        "orm": "SQLAlchemy",
        "db_url": "sqlite:///dev.db",
    }
    _render_local_template(template, tmp_path, config, "demo")
    spec = importlib.util.spec_from_file_location(f"scaffold_{template}", tmp_path / model)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.UserModel.__table__


@pytest.mark.parametrize(("template", "model"), TEMPLATES)
def test_sqlalchemy_model_names_every_constraint(tmp_path, template, model):
    table = _users_table(tmp_path, template, model)
    assert [c.name for c in table.constraints if c.name is None] == []
