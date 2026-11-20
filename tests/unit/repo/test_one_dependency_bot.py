"""Dependabot alone updates the dependencies (#298): a second bot would open the same PRs."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_renovate_is_not_configured_next_to_dependabot():
    assert not (ROOT / "renovate.json").exists()
