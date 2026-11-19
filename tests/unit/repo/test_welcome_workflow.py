"""The Welcome workflow posts the contributor welcome when a good first issue is assigned."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]


def _workflow() -> dict:
    return yaml.safe_load((ROOT / ".github" / "workflows" / "welcome.yml").read_text("utf-8"))


def _job() -> dict:
    return _workflow()["jobs"]["welcome"]


def test_welcome_workflow_runs_when_an_issue_is_assigned():
    # YAML 1.1 reads the bare key `on` as the boolean true.
    assert _workflow()[True]["issues"]["types"] == ["assigned"]


def test_welcome_workflow_waits_for_a_good_first_issue():
    assert "contains(github.event.issue.labels.*.name, 'good first issue')" in _job()["if"]


def test_welcome_workflow_skips_the_maintainer():
    assert "github.event.assignee.login != 'Espoir-Loem'" in _job()["if"]


def test_welcome_workflow_posts_the_shared_welcome():
    assert ".github/CONTRIBUTOR_WELCOME.md" in _job()["steps"][-1]["run"]


def test_welcome_workflow_never_pastes_the_login_into_the_script():
    assert "${{" not in _job()["steps"][-1]["run"]
