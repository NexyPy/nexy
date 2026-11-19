"""The dependency firewall checks a lock change on its pull request, before the merge."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]


def _triggers() -> dict:
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "socket.yml").read_text("utf-8"))
    # YAML 1.1 reads the bare key `on` as the boolean true.
    return workflow[True]


def test_socket_workflow_runs_on_a_pull_request_that_changes_the_lock():
    assert "uv.lock" in _triggers()["pull_request"]["paths"]


def test_socket_workflow_checks_the_same_files_before_and_after_the_merge():
    assert _triggers()["pull_request"]["paths"] == _triggers()["push"]["paths"]
