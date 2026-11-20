"""A project scaffolded with an ORM works: it shows what the database holds.

The scaffold tests elsewhere build every template with no ORM. Each case here scaffolds a project
with one, creates its table the way its own configuration describes, adds a row through the model,
then asks for it, in the project's interpreter as `nx dev` would run it: an API lists its users on
a route, a web project lists its tasks through the `todos` action of its /todos page.
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

# template: (module that holds the model, its class, the fields of one row, the text it shows)
MODELS = {
    "web-fbr": ("src.models.todo_model", "TodoModel", 'title="Water the plants"', "Water"),
    "web-modular": ("src.apps.todos.todo_model", "TodoModel", 'title="Water the plants"', "Water"),
    "api-fbr": ("src.models.user_model", "UserModel", 'name="Ada", email="ada@example.com"', "Ada"),
    "api-modular": (
        "src.apps.users.user_model",
        "UserModel",
        'name="Ada", email="ada@example.com"',
        "Ada",
    ),
}
# How each template is asked for its rows: an API route, or the action of the /todos page.
ASK = {
    "web-fbr": ("action", "src.actions.todos.todos"),
    "web-modular": ("action", "src.apps.todos.todo_actions.todos"),
    "api-fbr": ("route", "/"),
    "api-modular": ("route", "/users"),
}


def prepare_code(orm: str, template: str) -> str:
    """Create the table and one row with the ORM, using what the scaffold wrote."""
    models, model, fields, _ = MODELS[template]
    if orm == "SQLModel":
        return f"""
from sqlmodel import Session, SQLModel
from src.configs.db import engine
from {models} import {model}
SQLModel.metadata.create_all(engine)
with Session(engine) as session:
    session.add({model}({fields}))
    session.commit()
"""
    if orm == "SQLAlchemy":
        return f"""
from sqlalchemy.orm import Session
from src.configs.db import engine
from {models} import Base, {model}
Base.metadata.create_all(engine)
with Session(engine) as session:
    session.add({model}({fields}))
    session.commit()
"""
    return f"""
from tortoise import Tortoise
from src.configs.db import run
from {models} import {model}


async def seed():
    await Tortoise.generate_schemas()
    await {model}.create({fields})


run(seed())
"""


def request_code(template: str) -> str:
    kind, target = ASK[template]
    if kind == "route":
        call = f"client.get({target!r})"
    else:
        call = f"client.post(ACTIONS_STORE.path_map[{target!r}], json={{}})"
    return f"""
import json, sys
from nexy.core.config import Config
Config()
from nexy.modules.builder import Builder
Builder().build()
from fastapi.testclient import TestClient
from nexy.modules.routers.actions.store import ACTIONS_STORE
from nexy.modules.routers.app import AppServer
with TestClient(AppServer().run(), raise_server_exceptions=False) as client:
    answer = {call}
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
@pytest.mark.parametrize("template", list(MODELS))
def test_the_project_shows_the_row_of_the_database(tmp_path, template, orm):
    _scaffold(tmp_path, template, orm)
    prepared = _run(tmp_path, prepare_code(orm, template))
    assert prepared.returncode == 0, prepared.stderr[-1500:]
    done = _run(tmp_path, request_code(template))
    assert "@@" in done.stdout, done.stderr[-1500:]
    status, body = json.loads(done.stdout.split("@@")[1])
    assert (status, MODELS[template][3] in body) == (200, True), body[:300]


RELOAD = """
import json, sys
from nexy.modules.cli.devtools.watch.purge import purge_project_modules

def names():
    from src.configs.db import run
    from src.services.todo_service import TodoService
    return [todo.title for todo in run(TodoService.all())]

before = names()
purge_project_modules()
after = names()
sys.stdout.write("@@" + json.dumps([before, after]) + "@@")
"""


def test_tortoise_still_answers_after_nexy_dev_imports_the_project_again(tmp_path):
    _scaffold(tmp_path, "web-fbr", "Tortoise-ORM")
    prepared = _run(tmp_path, prepare_code("Tortoise-ORM", "web-fbr"))
    assert prepared.returncode == 0, prepared.stderr[-1500:]
    done = _run(tmp_path, RELOAD)
    assert "@@" in done.stdout, done.stderr[-1500:]
    titles = ["Water the plants"]
    assert json.loads(done.stdout.split("@@")[1]) == [titles, titles]


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
    _scaffold(tmp_path, template, orm)
    url = default_url("sqlite", orm)
    generate_post_init_files(tmp_path, orm, url)
    migration = init_migration(orm, tmp_path, url, _real_tools)
    assert migration.done, migration.problem
    done = _run(tmp_path, request_code(template))
    assert "@@" in done.stdout, done.stderr[-1500:]
    assert json.loads(done.stdout.split("@@")[1])[0] == 200


ADD_ACTION = {
    "web-fbr": "src.actions.todos.add_todo",
    "web-modular": "src.apps.todos.todo_actions.add_todo",
}
ADD = """
import json, sys
from nexy.core.config import Config
Config()
from nexy.modules.builder import Builder
Builder().build()
from fastapi.testclient import TestClient
from nexy.modules.routers.actions.store import ACTIONS_STORE
from nexy.modules.routers.app import AppServer
with TestClient(AppServer().run(), raise_server_exceptions=False) as client:
    add = ACTIONS_STORE.path_map[{action!r}]
    answer = client.post(add, json={{"title": "Call the plumber"}})
sys.stdout.write("@@" + json.dumps([answer.status_code, answer.text]) + "@@")
"""


@pytest.mark.parametrize("orm", ORMS)
@pytest.mark.parametrize("template", ["web-fbr", "web-modular"])
def test_the_todos_page_adds_a_task_to_the_todos_table(tmp_path, template, orm):
    _scaffold(tmp_path, template, orm)
    prepared = _run(tmp_path, prepare_code(orm, template))
    assert prepared.returncode == 0, prepared.stderr[-1500:]
    done = _run(tmp_path, ADD.format(action=ADD_ACTION[template]))
    assert "@@" in done.stdout, done.stderr[-1500:]
    status, body = json.loads(done.stdout.split("@@")[1])
    titles = [todo["title"] for todo in json.loads(body)["items"]] if status == 200 else body
    assert titles == ["Water the plants", "Call the plumber"], body[:300]
