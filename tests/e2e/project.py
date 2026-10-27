"""Build a throw-away Nexy project, then request it in a fresh interpreter.

Nexy resolves imports relative to the working directory, so each project gets its own process.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from nexy.modules.cli.init.template_setup import _render_local_template

REPO = Path(__file__).resolve().parents[2]

_RUNNER = """
import json, sys
sys.path.insert(0, ".")
from nexy.core.config import Config
Config()
from nexy.modules.builder import Builder
Builder().build()
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer
requests = json.loads(sys.argv[1])
out = []
with TestClient(AppServer().run(), raise_server_exceptions=False) as client:
    for path, headers in requests:
        response = client.get(path, headers=headers, follow_redirects=False)
        out.append([response.status_code, dict(response.headers), response.text])
sys.stdout.write("@@" + json.dumps(out) + "@@")
"""


def scaffold(
    dest: Path,
    template: str = "api-fbr",
    framework: str = "none",
    *,
    use_csr: bool = False,
) -> None:
    config = {
        "client_framework": framework,
        "FBRouter": template.endswith("fbr"),
        "project_type": template.split("-")[0],
        "orm": "None",
        "useCSR": use_csr,
    }
    _render_local_template(template, dest, config, "demo")


def write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def request(
    project: Path, *requests: tuple[str, dict[str, str]]
) -> list[tuple[int, dict[str, str], str]]:
    """GET each ``(path, headers)`` against the project; return status, headers and body."""
    done = subprocess.run(
        [sys.executable, "-c", _RUNNER, json.dumps(requests)],
        cwd=project,
        env={**os.environ, "PYTHONPATH": str(REPO), "PYTHONIOENCODING": "utf-8"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
        check=False,
    )
    assert "@@" in done.stdout, done.stderr[-1500:]
    answers: list[Any] = json.loads(done.stdout.split("@@")[1])
    return [(status, headers, body) for status, headers, body in answers]
