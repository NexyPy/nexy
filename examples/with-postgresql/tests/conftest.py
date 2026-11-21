"""The project, with an empty database for each test.

The tests run on whatever DATABASE_URL names: SQLite in a temporary file when it is unset (CI),
PostgreSQL when it points at one. The same tests, the same code.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/test.db")


@pytest.fixture(autouse=True)
def empty_tables():
    from sqlmodel import SQLModel

    from src.configs.db import create_tables, engine

    create_tables()
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient
    from nexy.app import app

    with TestClient(app, follow_redirects=False) as client:
        yield client


def add_address(client):
    import re

    return re.search(r'<form method="post" action="([^"]+)"', client.get("/").text).group(1)
