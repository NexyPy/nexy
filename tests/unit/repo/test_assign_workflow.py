"""The Assign workflow leaves every issue and pull request unassigned."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]


def _job() -> dict:
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "assign.yml").read_text("utf-8"))
    return workflow["jobs"]["assign"]


def test_assign_workflow_keeps_the_required_check_name():
    assert _job()["name"] == "Give it an owner"


def test_assign_workflow_never_runs_an_assignment_command():
    script = " ".join(step.get("run", "") for step in _job()["steps"])
    assert "--add-assignee" not in script
