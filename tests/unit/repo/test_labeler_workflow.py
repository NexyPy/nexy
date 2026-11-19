"""The Labeler workflow labels a pull request without running its code (#298)."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]


def _workflow() -> dict:
    return yaml.safe_load((ROOT / ".github" / "workflows" / "labeler.yml").read_text("utf-8"))


def _steps() -> list[dict]:
    return [step for job in _workflow()["jobs"].values() for step in job["steps"]]


def test_labeler_workflow_runs_on_a_pull_request_from_a_fork_too():
    # YAML 1.1 reads the bare key `on` as the boolean true.
    assert "pull_request_target" in _workflow()[True]


def test_labeler_workflow_never_checks_out_the_pull_request():
    assert not [step for step in _steps() if "checkout" in step.get("uses", "")]


def test_labeler_workflow_pins_the_action_by_commit():
    uses = [step["uses"] for step in _steps()]
    assert all(len(use.split("@")[1]) == 40 for use in uses)


def test_labeler_workflow_can_only_write_labels():
    assert _workflow()["permissions"] == {"contents": "read", "pull-requests": "write"}
