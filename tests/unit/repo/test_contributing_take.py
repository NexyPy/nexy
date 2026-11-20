"""CONTRIBUTING.md tells a contributor how to take an issue, and when it is freed."""

from __future__ import annotations

from pathlib import Path

import pytest

CONTRIBUTING = Path(__file__).resolve().parents[3] / "CONTRIBUTING.md"


@pytest.mark.parametrize("words", ["`/take`", "14 days", "difficulty:beginner", "projects/2"])
def test_contributing_explains_how_to_take_an_issue(words):
    assert words in CONTRIBUTING.read_text("utf-8")
