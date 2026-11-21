"""The project, called the way a client calls it, with no server to start."""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
os.environ["LIBRARY_STAFF_TOKEN"] = "staff-test-token"
STAFF = {"X-Staff-Token": "staff-test-token"}


@pytest.fixture(scope="session")
def app_client():
    from fastapi.testclient import TestClient
    from nexy.app import app

    with TestClient(app, follow_redirects=False) as client:
        yield client


@pytest.fixture
def client(app_client):
    """Every book back on the shelf it started on: no test sees another one's loans."""
    from src.library.catalogue import BOOKS

    for book in BOOKS:
        book.on_loan = book.id == 2
    return app_client
