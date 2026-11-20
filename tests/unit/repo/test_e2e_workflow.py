"""The browser suite runs on a pull request that can break it, and not on one that cannot.

`.github/workflows/e2e.yml` boots uvicorn, Vite and Chromium. A pull request that changes the code
or the suite gets it before the merge; a pull request that only changes the docs does not.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]


def _triggers() -> dict:
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "e2e.yml").read_text("utf-8"))
    # YAML 1.1 reads the bare key `on` as the boolean true.
    return workflow.get("on", workflow.get(True)) or {}


def _glob(pattern: str) -> re.Pattern[str]:
    """A GitHub `paths` pattern: `**` crosses folders, `*` stays in one."""
    parts = re.split(r"(\*\*/?|\*)", pattern)
    regex = {"**/": "(?:.*/)?", "**": ".*", "*": "[^/]*"}
    return re.compile("".join(regex.get(part, re.escape(part)) for part in parts) + r"\Z")


def _runs_on(path: str) -> bool:
    paths = _triggers().get("pull_request", {}).get("paths", [])
    return any(_glob(pattern).match(path) for pattern in paths)


@pytest.mark.parametrize(
    "path",
    [
        "nexy/modules/routers/app.py",
        "nexy/modules/frontend/client/router.ts",
        "tests/e2e/test_client_routing.py",
        ".github/workflows/e2e.yml",
    ],
)
def test_a_pull_request_that_touches_the_stack_runs_the_browser_suite(path):
    assert _runs_on(path)


@pytest.mark.parametrize(
    "path",
    ["docs/routing/fbr/navigation/linking-and-navigating.md", "docs/fr/README.md", "README.md"],
)
def test_a_docs_only_pull_request_does_not(path):
    assert not _runs_on(path)


def test_a_newer_push_to_the_pull_request_cancels_the_older_run():
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "e2e.yml").read_text("utf-8"))
    # Only a pull request: a push to main and the nightly run each finish.
    cancel = str(workflow.get("concurrency", {}).get("cancel-in-progress", ""))
    assert cancel == "${{ github.event_name == 'pull_request' }}"


def test_e2e_runs_on_a_push_to_main():
    assert _triggers()["push"]["branches"] == ["main"]
