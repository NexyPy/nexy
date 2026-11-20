"""Every test starts from the database `nexy migrate --upgrade` makes: the table and its orders.

The migrations run once into a file of their own; each test then gets a fresh copy of that file.
"""

import os
import sqlite3
import sys
import tempfile
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATABASE = Path(tempfile.mkdtemp()) / "orders.db"

# Before src.configs.db makes its engine: the tests never touch dev.db.
os.environ["DATABASE_URL"] = f"sqlite:///{DATABASE.as_posix()}"
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from src.configs.db import engine
from src.models.order_model import OrderModel


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
def empty() -> None:
    """No order at all: a test that needs some writes its own with `order`."""
    with Session(engine) as session:
        session.exec(delete(OrderModel))
        session.commit()


@pytest.fixture
def order(empty):
    def write(
        day: str,
        channel: str = "Online",
        product: str = "Decaf 250g",
        units: int = 1,
        revenue_cents: int = 1500,
    ) -> None:
        with Session(engine) as session:
            session.add(
                OrderModel(
                    placed_on=date.fromisoformat(day),
                    channel=channel,
                    region="North",
                    product=product,
                    units=units,
                    revenue_cents=revenue_cents,
                )
            )
            session.commit()

    return write


@pytest.fixture(scope="session")
def app():
    from nexy.app import app

    return app


@pytest.fixture
def call(app):
    """Call an action the way the page does: a POST of JSON to the path Nexy gave it."""
    from nexy.decorators import ACTIONS_STORE

    with TestClient(app) as client:

        def post(action: str, **given):
            path = ACTIONS_STORE.template_context()["__actions_path"][action]
            return client.post(path, json=given, headers={"accept": "application/json"})

        yield post
