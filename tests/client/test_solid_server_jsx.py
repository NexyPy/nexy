"""A Solid island gets its server HTML at build: its JSX goes through Solid's compiler (#563)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
NODE = shutil.which("node")


def _rendered() -> str:
    done = subprocess.run(
        [NODE, str(HERE / "solid_server_jsx.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
        cwd=HERE,
    )
    assert "@@" in done.stdout, (done.stdout + done.stderr)[-1500:]
    return done.stdout.split("@@")[1]


def test_a_solid_component_renders_on_the_server():
    assert _rendered() == '<p class="hello">hello you</p><span>2</span>'
