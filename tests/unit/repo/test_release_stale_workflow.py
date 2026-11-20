"""The Release stale issues workflow runs scripts/release_stale_issues.py once a day."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]


def _workflow() -> dict:
    text = (ROOT / ".github" / "workflows" / "release-stale.yml").read_text("utf-8")
    return yaml.safe_load(text)


def test_release_stale_workflow_runs_every_day():
    # YAML 1.1 reads the bare key `on` as the boolean true.
    assert _workflow()[True]["schedule"][0]["cron"].endswith("* * *")


def test_release_stale_workflow_runs_the_script():
    steps = _workflow()["jobs"]["release"]["steps"]
    assert steps[-1]["run"] == "python3 scripts/release_stale_issues.py"


def test_release_stale_workflow_can_only_touch_issues():
    assert _workflow()["permissions"] == {"issues": "write"}
