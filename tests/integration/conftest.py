from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nexy.helpers.fs.vfs import VFS

# Verbatim shape of the documented user-facing .nexy format
# (examples/minimal): frontmatter logic block, then template body.
MINIMAL_INDEX_NEXY = """---
greeting: prop[str] = "Hello World!"
def shout(text: str) -> str:
    return text.upper()
---
<section>
    <h1>{{ shout(greeting) }}</h1>
</section>
"""

MINIMAL_BROKEN_NEXY = "---\ndef broken(\n---\n<section></section>"


@pytest.fixture
def nexy_app(nexy_project) -> Iterator[TestClient]:
    """A fully assembled FastAPI app (AppServer) behind TestClient.

    The app is reassembled per test in the sandboxed cwd of nexy_project,
    so it picks up project-local configuration and middleware wiring.
    """
    from nexy.routers.app import AppServer

    nexy_project("")  # no overrides: framework defaults
    with TestClient(AppServer().run()) as client:
        yield client


@pytest.fixture
def builder_project(nexy_project, tmp_path: Path) -> Path:
    """A minimal single-route user project for Builder runs.

    Isolates the shared VFS: no dev-mode writes, an empty store, and a
    cleanup restoring the dev-mode default (False).
    """
    from nexy.modules.builder import Builder  # noqa: F401  (import sanity under cwd)

    nexy_project("")
    VFS.set_dev_mode(False)
    VFS().clear()
    routes_dir = tmp_path / "src" / "routes"
    routes_dir.mkdir(parents=True)
    (routes_dir / "index.nexy").write_text(MINIMAL_INDEX_NEXY, encoding="utf-8")
    yield routes_dir
    VFS().clear(clear_disk=True)
