"""The board, asked for its pages the way a browser asks, on a database of its own per test."""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def database(tmp_path, monkeypatch):
    """A new board for each test, with the cards every board starts with."""
    from src.board import store

    monkeypatch.setattr(store, "DATABASE", tmp_path / "board.db")
    return tmp_path / "board.db"


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient
    from nexy.app import app

    with TestClient(app, follow_redirects=False) as client:
        yield client
