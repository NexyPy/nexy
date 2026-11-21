"""The site, asked for its pages the way a browser asks, with no server to start."""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient
    from nexy.app import app

    with TestClient(app, follow_redirects=False) as client:
        yield client
