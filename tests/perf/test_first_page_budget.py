"""The first page of a new project answers with HTML in under a second.

The project promises a sub-second first page (AGENTS.md). This measures a new process that builds
the application and requests `/`, as `FIRST_PAGE` does in `scripts/measure_speed.py`, and keeps the
fastest of a few runs so a busy machine does not fail it.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

BUDGET_SECONDS = 1.0
RUNS = 3
PAGE = "---\ntitle = 'Home'\n---\n<h1>{{ title }}</h1>\n"
CONFIG = (
    "from nexy.core.models import NexyConfigModel\n\n\n"
    "class NexyConfig(NexyConfigModel):\n    useVite: bool = False\n"
)
REQUEST = (
    "from fastapi.testclient import TestClient\n"
    "from nexy.modules.routers.app import AppServer\n"
    "print(TestClient(AppServer().run()).get('/').status_code)\n"
)


def _project(root: Path) -> Path:
    page = root / "src/routes/index.nexy"
    page.parent.mkdir(parents=True)
    page.write_text(PAGE, encoding="utf-8")
    (root / "nexyconfig.py").write_text(CONFIG, encoding="utf-8")
    return root


def _request(root: Path) -> tuple[float, int]:
    started = time.perf_counter()
    result = subprocess.run(  # nosec B603 - this interpreter, a string of this file
        [sys.executable, "-c", REQUEST], cwd=root, check=True, capture_output=True, text=True
    )
    status = int(result.stdout.splitlines()[-1])
    return time.perf_counter() - started, status


def test_first_page_budget_a_new_process_serves_html_under_a_second(tmp_path):
    root = _project(tmp_path)
    assert min(_request(root)[0] for _ in range(RUNS)) < BUDGET_SECONDS


def test_first_page_answers_200(tmp_path):
    root = _project(tmp_path)
    assert _request(root)[1] == 200
