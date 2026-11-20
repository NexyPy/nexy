"""The tests of every example pass with the Nexy of this branch.

An example is a project of its own, with its own `tests/`: a change to Nexy that breaks one of them
fails here, before a person who copies the example finds out.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SUITES = sorted(path.parent.name for path in (ROOT / "examples").glob("*/tests"))


@pytest.mark.parametrize("example", SUITES)
def test_the_example_passes_its_own_tests(example: str, tmp_path: Path) -> None:
    done = subprocess.run(  # nosec B603 - the test runner of this interpreter, fixed arguments
        [sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
        cwd=ROOT / "examples" / example,
        capture_output=True,
        text=True,
        check=False,
        # The whole environment: Windows needs SYSTEMROOT to open a socket at all.
        env={**os.environ, "TMPDIR": str(tmp_path), "PYTHONPATH": str(ROOT)},
    )
    assert done.returncode == 0, done.stdout[-2000:] + done.stderr[-2000:]
