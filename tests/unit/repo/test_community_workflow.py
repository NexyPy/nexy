"""The weekly community report edits only the issue it wrote (#462 review)."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]


def _script() -> str:
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "community.yml").read_text("utf-8"))
    return "\n".join(step.get("run", "") for step in workflow["jobs"]["report"]["steps"])


def test_community_report_keeps_only_the_exact_title():
    assert "select(.title == env.TITLE)" in _script()


def test_community_report_keeps_only_an_issue_the_workflow_wrote():
    assert '--author "app/github-actions"' in _script()


def test_community_report_reads_last_week_from_a_closed_report_too():
    assert "--state all" in _script()
