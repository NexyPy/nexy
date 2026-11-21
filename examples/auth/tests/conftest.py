"""The account pages, asked the way a browser asks, on a database of their own per test."""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SESSION_SECRET", "a-secret-for-the-tests-only")


@pytest.fixture(autouse=True)
def database(tmp_path, monkeypatch):
    """No account at the start of a test, and no failed sign-in remembered from another."""
    from src.accounts import store, throttle

    monkeypatch.setattr(store, "DATABASE", tmp_path / "auth.db")
    throttle.FAILURES.clear()
    return tmp_path / "auth.db"


@pytest.fixture
def client():
    """A browser of its own: its session cookie does not leak into another test."""
    from fastapi.testclient import TestClient
    from nexy.app import app

    with TestClient(app, follow_redirects=False) as client:
        yield client
