"""Every test starts from an empty `notes` table, in a database the migrations made, never dev.db."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATABASE = Path(tempfile.mkdtemp()) / "notes.db"

# Before src.configs.db reads it: the tests never touch dev.db.
os.environ["DATABASE_URL"] = f"sqlite://{DATABASE.as_posix()}"
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

from aerich import Command
from fastapi.testclient import TestClient

from src.configs.db import TORTOISE_ORM, run
from src.models.note_model import NoteModel


@pytest.fixture(scope="session", autouse=True)
def tables() -> None:
    """The migrations of migrations/, as `nx migrate --upgrade` runs them: a model that drifts
    from them fails here."""
    run(migrate())


async def migrate() -> None:
    command = Command(tortoise_config=TORTOISE_ORM, app="models", location="./migrations")
    await command.init()
    await command.upgrade(run_in_transaction=True)


@pytest.fixture(autouse=True)
def empty() -> None:
    run(NoteModel.all().delete())


@pytest.fixture(scope="session")
def client():
    from nexy.app import app

    with TestClient(app) as browser:
        yield browser


@pytest.fixture
def call(client):
    """Call an action the way the page does: a POST of JSON to the path Nexy gave it."""
    from nexy.decorators import ACTIONS_STORE

    def post(action: str, **given):
        path = ACTIONS_STORE.template_context()["__actions_path"][action]
        return client.post(path, json=given, headers={"accept": "application/json"})

    return post
