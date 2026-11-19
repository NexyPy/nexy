"""CONTRIBUTING.md turns small confirmed bugs into beginner issues (Triage)."""

from __future__ import annotations

from pathlib import Path

CONTRIBUTING = Path(__file__).resolve().parents[3] / "CONTRIBUTING.md"


def _triage() -> str:
    return CONTRIBUTING.read_text("utf-8").split("## Triage", 1)[1].split("\n## ", 1)[0]


def test_triage_turns_a_small_bug_into_a_beginner_issue():
    assert "A small confirmed bug becomes a beginner issue" in _triage()


def test_triage_keeps_urgent_bugs_for_the_maintainer():
    assert "`priority:1`" in _triage()


def test_triage_is_in_the_table_of_contents():
    assert "- [Triage](#triage)" in CONTRIBUTING.read_text("utf-8")
