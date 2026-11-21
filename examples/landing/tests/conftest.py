"""Every test starts from the database `nexy migrate --upgrade` makes: an empty waitlist.

The migrations run once into a file of their own; each test then gets a fresh copy of that file.
"""

import os
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATABASE = Path(tempfile.mkdtemp()) / "waitlist.db"

# Before src.configs.db makes its engine: the tests never touch dev.db.
os.environ["DATABASE_URL"] = f"sqlite:///{DATABASE.as_posix()}"
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.subscriber_model import SubscriberModel


def copy(source: Path, target: Path) -> None:
    """Copy a database through SQLite: Windows refuses to overwrite a file a connection holds."""
    with sqlite3.connect(source) as origin, sqlite3.connect(target) as copied:
        origin.backup(copied)
    origin.close()
    copied.close()


@pytest.fixture(scope="session")
def migrated() -> Path:
    """The database after every migration, kept aside to copy."""
    command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
    engine.dispose()
    kept = DATABASE.with_name("migrated.db")
    copy(DATABASE, kept)
    return kept


@pytest.fixture(autouse=True)
def fresh_database(migrated: Path) -> None:
    engine.dispose()
    copy(migrated, DATABASE)


@pytest.fixture
def emails():
    """The addresses on the list, in the order they joined."""

    def read() -> list[str]:
        with Session(engine) as session:
            query = select(SubscriberModel.email).order_by(SubscriberModel.id)
            return list(session.exec(query))

    return read


@pytest.fixture(scope="session")
def client():
    """The site, asked for its pages the way a browser asks, with no server to start."""
    from nexy.app import app

    with TestClient(app, follow_redirects=False) as client:
        yield client


@pytest.fixture
def call(client):
    """Call an action the way the page does: a POST of JSON to the path Nexy gave it."""
    from nexy.decorators import ACTIONS_STORE

    def post(action: str, **given):
        path = ACTIONS_STORE.template_context()["__actions_path"][action]
        return client.post(path, json=given, headers={"accept": "application/json"})

    return post
