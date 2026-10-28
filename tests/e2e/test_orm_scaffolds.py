"""A project scaffolded with an ORM works: its users route shows what the database holds.

The scaffold tests elsewhere build every template with no ORM. Each case here scaffolds a project
with one, creates its table the way its own configuration describes, adds a user through the
model and asks for the users route, in the project's interpreter as `nx dev` would run it.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from nexy.helpers.common.executables import find_tool
from nexy.modules.cli.init.databases import default_url
from nexy.modules.cli.init.template_setup import (
    _render_local_template,
    generate_post_init_files,
    init_migration,
)

REPO = Path(__file__).resolve().parents[2]
ORMS = ["SQLModel", "SQLAlchemy", "Tortoise-ORM"]

# (template, route that lists the users, module that holds the model)
TEMPLATES = [
    ("web-fbr", "/users", "src.models.user_model"),
    ("web-modular", "/users", "src.apps.users.user_model"),
    ("api-fbr", "/", "src.models.user_model"),
    ("api-modular", "/users", "src.apps.users.user_model"),
]


def prepare_code(orm: str, models: str) -> str:
    """Create the table and one user with the ORM, using what the scaffold wrote."""
    if orm == "SQLModel":
        return f"""
from sqlmodel import Session, SQLModel
from src.configs.db import engine
from {models} import UserModel
SQLModel.metadata.create_all(engine)
with Session(engine) as session:
    session.add(UserModel(name="Ada", email="ada@example.com"))
    session.commit()
"""
    if orm == "SQLAlchemy":
        return f"""
from sqlalchemy.orm import Session
from src.configs.db import engine
from {models} import Base, UserModel
Base.metadata.create_all(engine)
with Session(engine) as session:
    session.add(UserModel(name="Ada", email="ada@example.com"))
    session.commit()
"""
    return f"""
from tortoise import Tortoise
from src.configs.db import run
from {models} import UserModel


async def seed():
    await Tortoise.generate_schemas()
    await UserModel.create(name="Ada", email="ada@example.com")


run(seed())
"""


def request_code(route: str) -> str:
    return f"""
import json, sys
from nexy.core.config import Config
Config()
from nexy.modules.builder import Builder
Builder().build()
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer
with TestClient(AppServer().run(), raise_server_exceptions=False) as client:
    answer = client.get({route!r})
sys.stdout.write("@@" + json.dumps([answer.status_code, answer.text]) + "@@")
"""


def _scaffold(dest: Path, template: str, orm: str) -> None:
    config = {
        "client_framework": "none",
        "FBRouter": template.endswith("fbr"),
        "project_type": template.split("-")[0],
        "orm": orm,
        "useCSR": False,
    }
    _render_local_template(template, dest, config, "demo")


def _run(project: Path, code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", "import sys\nsys.path.insert(0, '.')\n" + code],
        cwd=project,
        env={**os.environ, "PYTHONPATH": str(REPO), "PYTHONIOENCODING": "utf-8"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
        check=False,
    )


@pytest.mark.parametrize("orm", ORMS)
@pytest.mark.parametrize(("template", "route", "models"), TEMPLATES)
def test_the_users_route_shows_the_user_of_the_database(tmp_path, template, route, models, orm):
    _scaffold(tmp_path, template, orm)
    prepared = _run(tmp_path, prepare_code(orm, models))
    assert prepared.returncode == 0, prepared.stderr[-1500:]
    done = _run(tmp_path, request_code(route))
    assert "@@" in done.stdout, done.stderr[-1500:]
    status, body = json.loads(done.stdout.split("@@")[1])
    assert (status, "Ada" in body) == (200, True), body[:300]


RELOAD = """
import json, sys
from nexy.modules.cli.devtools.watch.purge import purge_project_modules

def names():
    from src.configs.db import run
    from src.services.user_service import UserService
    return [user.name for user in run(UserService.get_all())]

before = names()
purge_project_modules()
after = names()
sys.stdout.write("@@" + json.dumps([before, after]) + "@@")
"""


def test_tortoise_still_answers_after_nexy_dev_imports_the_project_again(tmp_path):
    _scaffold(tmp_path, "web-fbr", "Tortoise-ORM")
    prepared = _run(tmp_path, prepare_code("Tortoise-ORM", "src.models.user_model"))
    assert prepared.returncode == 0, prepared.stderr[-1500:]
    done = _run(tmp_path, RELOAD)
    assert "@@" in done.stdout, done.stderr[-1500:]
    assert json.loads(done.stdout.split("@@")[1]) == [["Ada"], ["Ada"]]


def _real_tools(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run alembic or aerich from this environment, as `uv run` would from the project's."""
    exe = find_tool(args[0]) or args[0]
    return subprocess.run(
        [exe, *args[1:]],
        cwd=cwd,
        env={**os.environ, "PYTHONPATH": str(REPO), "PYTHONIOENCODING": "utf-8"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
        check=False,
    )


@pytest.mark.parametrize("orm", ORMS)
@pytest.mark.parametrize("template", ["web-fbr", "web-modular", "api-fbr", "api-modular"])
def test_a_new_project_has_its_tables_without_a_manual_migration(tmp_path, template, orm):
    route = {"web-fbr": "/users", "web-modular": "/users", "api-fbr": "/", "api-modular": "/users"}
    _scaffold(tmp_path, template, orm)
    url = default_url("sqlite", orm)
    generate_post_init_files(tmp_path, orm, url)
    migration = init_migration(orm, tmp_path, url, _real_tools)
    assert migration.done, migration.problem
    done = _run(tmp_path, request_code(route[template]))
    assert "@@" in done.stdout, done.stderr[-1500:]
    assert json.loads(done.stdout.split("@@")[1])[0] == 200
