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


@pytest.fixture(autouse=True)
def empty_cache():
    """Each test starts with no stored page. The cache lives in the server process; a test that
    moves the clock would otherwise leave a copy the next test reads as fresh."""
    from nexy.modules.runtime.cache import REVALIDATE_CACHE

    REVALIDATE_CACHE.clear()
