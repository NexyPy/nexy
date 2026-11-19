"""The Assign workflow gives everything an owner, except a good first issue (#301)."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]


def _job() -> dict:
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "assign.yml").read_text("utf-8"))
    return workflow["jobs"]["assign"]


def test_assign_workflow_leaves_a_good_first_issue_unassigned():
    assert "!contains(github.event.issue.labels.*.name, 'good first issue')" in _job()["if"]
