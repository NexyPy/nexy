"""The Speed workflow publishes the times of scripts/measure_speed.py on a push to main (#297)."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]


def _workflow() -> dict:
    return yaml.safe_load((ROOT / ".github" / "workflows" / "speed.yml").read_text("utf-8"))


def _runs() -> list[str]:
    return [step.get("run", "") for step in _workflow()["jobs"]["measure"]["steps"]]


def test_speed_workflow_runs_on_a_push_to_main():
    # YAML 1.1 reads the bare key `on` as the boolean true.
    assert _workflow()[True]["push"]["branches"] == ["main"]


def test_speed_workflow_writes_the_table_to_the_summary():
    assert any("measure_speed.py" in run and "$GITHUB_STEP_SUMMARY" in run for run in _runs())


def test_speed_workflow_only_reads_the_repository():
    assert _workflow()["permissions"] == {"contents": "read"}
