"""The Nexy Vite plugin builds the static pages after `vite build`, never when `vite` dev stops."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
NODE = shutil.which("node")
BUILDING = "[nexy] Building client bundles..."


def _close(command: str) -> dict:
    done = subprocess.run(
        [NODE, str(HERE / "vite_plugin.mjs"), command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
        cwd=HERE,
    )
    assert "@@" in done.stdout, (done.stdout + done.stderr)[-1500:]
    return json.loads(done.stdout.split("@@")[1])


def test_closing_the_dev_server_builds_nothing():
    assert _close("serve") == {"logged": [], "ran": [], "error": None}


def test_closing_a_build_builds_the_client_bundles():
    assert BUILDING in _close("build")["logged"]
