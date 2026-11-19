"""The Take workflow runs scripts/take_issue.py on a new issue comment."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]


def _workflow() -> dict:
    return yaml.safe_load((ROOT / ".github" / "workflows" / "take.yml").read_text("utf-8"))


def _step() -> dict:
    return _workflow()["jobs"]["take"]["steps"][-1]


def test_take_workflow_runs_on_a_new_comment():
    # YAML 1.1 reads the bare key `on` as the boolean true.
    assert _workflow()[True]["issue_comment"]["types"] == ["created"]


def test_take_workflow_skips_pull_requests():
    assert "!github.event.issue.pull_request" in _workflow()["jobs"]["take"]["if"]


def test_take_workflow_runs_the_script():
    assert _step()["run"] == "python3 scripts/take_issue.py"


def test_take_workflow_passes_the_comment_through_env_only():
    assert _step()["env"]["BODY"] == "${{ github.event.comment.body }}"


def test_take_workflow_can_only_touch_issues():
    assert _workflow()["permissions"] == {"issues": "write"}
