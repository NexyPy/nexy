"""Every test gets an empty database of its own, in a temporary folder."""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["DATABASE_URL"] = "sqlite://"  # in memory until the fixture points it at a file


@pytest.fixture(autouse=True)
def empty_database(tmp_path, monkeypatch):
    from sqlmodel import create_engine
    from src.configs import db
    from src.services import todos

    engine = create_engine(f"sqlite:///{tmp_path / 'todos.db'}")
    monkeypatch.setattr(db, "engine", engine)
    monkeypatch.setattr(todos, "engine", engine)
    db.create_tables()
