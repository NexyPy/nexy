"""The site, asked for its pages the way a browser asks, with no server to start."""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from nexy.modules.runtime.cache import REVALIDATE_CACHE


@pytest.fixture(scope="session")
def client():
    from nexy.app import app

    with TestClient(app, follow_redirects=False) as client:
        yield client


@pytest.fixture(autouse=True)
def empty_cache():
    """The pages kept by `revalidate` live in the process: no test sees another test's pages."""
    REVALIDATE_CACHE.clear()
    yield
    REVALIDATE_CACHE.clear()


@pytest.fixture
def cached():
    """Whether the page of an address is kept in memory."""
    return lambda path: REVALIDATE_CACHE.get(path) is not None
