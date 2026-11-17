"""A Nexy application is ready in under a second, from a fresh Python process.

The project promises sub-second startup (AGENTS.md). This measures it in a new interpreter, as a
server worker starts, and keeps the fastest of a few runs so a busy machine does not fail it.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

BUDGET_SECONDS = 1.0
RUNS = 3
BUILD = "from nexy.modules.routers.app import AppServer; AppServer().run()"


def _project(root: Path) -> Path:
    page = root / "src/routes/index.py"
    page.parent.mkdir(parents=True)
    page.write_text('async def GET():\n    return {"ok": True}\n', encoding="utf-8")
    (root / "nexyconfig.py").write_text(
        "from nexy.core.models import NexyConfigModel\n\n\n"
        "class NexyConfig(NexyConfigModel):\n    useVite: bool = False\n",
        encoding="utf-8",
    )
    return root


def _startup(root: Path) -> float:
    started = time.perf_counter()
    subprocess.run([sys.executable, "-c", BUILD], cwd=root, check=True, capture_output=True)
    return time.perf_counter() - started


def test_startup_budget_an_application_is_ready_in_under_a_second(tmp_path):
    root = _project(tmp_path)
    assert min(_startup(root) for _ in range(RUNS)) < BUDGET_SECONDS
