"""Every file of the repository has an owner, so a review request always reaches someone (#298)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _rules() -> list[list[str]]:
    lines = (ROOT / ".github" / "CODEOWNERS").read_text("utf-8").splitlines()
    return [line.split() for line in lines if line.strip() and not line.startswith("#")]


def test_codeowners_gives_every_file_an_owner():
    assert ["*", "@Espoir-Loem"] in _rules()
