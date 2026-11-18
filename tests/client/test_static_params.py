"""A dynamic client route is pre-rendered once per static param set, and keeps its shell."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
NODE = shutil.which("node")
HELLO = "src/routes/blog/[slug]/blog/hello.html"
SHELL = "src/routes/blog/[slug].shell.html"


def _written(kind: str) -> list[str]:
    done = subprocess.run(
        [NODE, str(HERE / "static_params.mjs"), kind],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
        cwd=HERE,
    )
    assert "@@" in done.stdout, (done.stdout + done.stderr)[-1500:]
    report = json.loads(done.stdout.split("@@")[1])
    assert report["error"] is None, report["error"]
    return report["written"]


def test_static_params_write_one_document_per_path():
    assert HELLO in _written("sync")


def test_async_static_params_write_one_document_per_path():
    assert HELLO in _written("async")


def test_a_route_with_static_params_keeps_its_shell():
    assert SHELL in _written("sync")
