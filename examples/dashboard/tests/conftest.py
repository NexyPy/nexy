"""Every test gets the demo data in a database of its own, seeded on a fixed day."""

import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

TODAY = date(2026, 11, 20)


@pytest.fixture(autouse=True)
def demo_database(tmp_path, monkeypatch):
    from sqlmodel import create_engine
    from src.configs import db
    from src.services.demo import prepare

    monkeypatch.setattr(db, "engine", create_engine(f"sqlite:///{tmp_path / 'dashboard.db'}"))
    prepare(TODAY)
