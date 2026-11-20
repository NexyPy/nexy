"""Every test gets an empty database of its own, in a temporary folder."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def empty_database(tmp_path, monkeypatch):
    from sqlmodel import create_engine
    from src.configs import db

    monkeypatch.setattr(db, "engine", create_engine(f"sqlite:///{tmp_path / 'store.db'}"))
    db.create_tables()
