"""The tests run from the root of the project, as `nx dev` does: `src` and `nexyconfig.py` sit there."""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def client():
    """The blog, asked for its pages the way a browser asks, with no server to start."""
    from nexy.app import app

    with TestClient(app) as client:
        yield client
