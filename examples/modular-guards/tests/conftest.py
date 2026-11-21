"""The API, called the way a client calls it, with no server to start."""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
os.environ["NEWSROOM_KEYS"] = "writer-test-key:writer,editor-test-key:editor"

WRITER = {"X-Api-Key": "writer-test-key"}
EDITOR = {"X-Api-Key": "editor-test-key"}


@pytest.fixture(scope="session")
def app_client():
    from fastapi.testclient import TestClient
    from nexy.helpers.fs.vfs import VFS
    from nexy.modules.builder import Builder

    # `nx dev` and `nx build` compile the .nexy views a controller renders with useViews. The
    # tests compile them once, the same way, before the app starts.
    Builder().build(showlog=False)
    VFS().flush_to_disk()

    from nexy.app import app

    # No redirect followed: each test calls the exact address a client must use.
    with TestClient(app, follow_redirects=False) as client:
        yield client


@pytest.fixture
def client(app_client):
    """The API with the two stories it starts with: no test sees what another one wrote."""
    from src.apps.stories import store

    store.reset()
    return app_client
