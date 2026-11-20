"""Every test starts from the database `nexy migrate --upgrade` makes: the tables and the products.

The migrations run once into a file of their own; each test then gets a fresh copy of that file.
"""

import os
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATABASE = Path(tempfile.mkdtemp()) / "shop.db"

# Before src.configs.db makes its engine: the tests never touch dev.db.
os.environ["DATABASE_URL"] = f"sqlite:///{DATABASE.as_posix()}"
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from src.configs.db import engine


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


@pytest.fixture(scope="session")
def app():
    from nexy.app import app

    return app


@pytest.fixture
def browser(app):
    """A browser with no cookie yet: the cart it fills is its own."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def call(browser):
    """Call an action the way the page does: a POST of JSON to the path Nexy gave it."""
    from nexy.decorators import ACTIONS_STORE

    def post(action: str, client=None, **given):
        path = ACTIONS_STORE.template_context()["__actions_path"][action]
        return (client or browser).post(path, json=given, headers={"accept": "application/json"})

    return post
