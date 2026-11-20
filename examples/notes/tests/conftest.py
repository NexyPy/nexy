"""Every test starts from an empty `notes` table in a database of its own, never dev.db."""

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

from fastapi.testclient import TestClient
from tortoise import Tortoise

from src.configs.db import run
from src.models.note_model import NoteModel


@pytest.fixture(scope="session", autouse=True)
def tables() -> None:
    """The tables of the models; the migrations in migrations/ make the same ones for nx dev."""
    run(Tortoise.generate_schemas())


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
