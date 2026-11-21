"""An island's server HTML is the component with its own defaults, never a placeholder (#591)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
NODE = shutil.which("node")


def _rendered() -> list[str]:
    done = subprocess.run(
        [NODE, str(HERE / "island_snapshot.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
        cwd=HERE,
    )
    assert "@@" in done.stdout, (done.stdout + done.stderr)[-1500:]
    return done.stdout.split("@@")[1:3]


def test_a_react_snapshot_shows_the_defaults_of_the_component():
    assert _rendered()[0] == '<button type="button" class="a b">count: 0</button>'


def test_a_preact_snapshot_shows_the_defaults_of_the_component():
    assert _rendered()[1] == '<button type="button">count: 0</button>'
