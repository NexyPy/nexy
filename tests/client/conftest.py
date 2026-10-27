"""The client tests need Node.js and the packages of this folder: without them they fail, not skip.

A suite that skips itself when its tools are missing reports green while testing nothing, which is
what happened on CI before the packages were installed there.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
# Node.js strips TypeScript types by itself from this version on: the tests import `.ts` files.
MINIMUM_NODE = (22, 18)


def _node_version(node: str) -> tuple[int, int] | None:
    done = subprocess.run([node, "--version"], capture_output=True, text=True, check=False)
    found = re.match(r"v(\d+)\.(\d+)", done.stdout.strip())
    return (int(found[1]), int(found[2])) if found else None


def missing_prerequisite() -> str | None:
    """What is missing to run the client tests, or None."""
    node = shutil.which("node")
    if node is None:
        return "Node.js is not installed: install Node.js 22.18 or newer"
    version = _node_version(node)
    if version is None or version < MINIMUM_NODE:
        return "Node.js is too old to run TypeScript: install Node.js 22.18 or newer"
    if not (HERE / "node_modules" / "jsdom").is_dir():
        return "the client test packages are missing: run `npm ci` in tests/client"
    return None


@pytest.fixture(autouse=True, scope="session")
def client_prerequisites() -> None:
    problem = missing_prerequisite()
    if problem:
        pytest.fail(problem, pytrace=False)
