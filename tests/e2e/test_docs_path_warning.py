"""Starting a project with a page at /docs says the API reference hides it (#81)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from tests.e2e.project import REPO, scaffold, write

_START = """
import sys
sys.path.insert(0, ".")
from nexy.core.config import Config
Config()
from nexy.modules.builder import Builder
Builder().build(showlog=False)
from nexy.modules.routers.app import AppServer
AppServer().run()
"""


def _start(project: Path) -> str:
    done = subprocess.run(
        [sys.executable, "-c", _START],
        cwd=project,
        env={**os.environ, "PYTHONPATH": str(REPO), "PYTHONIOENCODING": "utf-8", "COLUMNS": "300"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
        check=False,
    )
    assert done.returncode == 0, done.stderr[-1500:]
    return done.stdout


def test_a_page_at_docs_is_named_at_startup(tmp_path):
    scaffold(tmp_path, "web-fbr", "none")
    write(tmp_path, "src/routes/docs.nexy", "<h1>Guide</h1>\n")
    assert "src/routes/docs.nexy is never served at /docs" in _start(tmp_path)


def test_a_project_without_one_starts_silently(tmp_path):
    scaffold(tmp_path, "web-fbr", "none")
    assert "is never served" not in _start(tmp_path)
