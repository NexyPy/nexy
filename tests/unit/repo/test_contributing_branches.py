"""CONTRIBUTING.md describes two long-lived branches: `develop` for work, `main` for releases."""

from __future__ import annotations

from pathlib import Path

CONTRIBUTING = Path(__file__).resolve().parents[3] / "CONTRIBUTING.md"


def test_contributing_names_no_staging_branch():
    assert "staging" not in CONTRIBUTING.read_text("utf-8")


def test_release_goes_from_develop_into_main():
    release = CONTRIBUTING.read_text("utf-8").split("## Release process", 1)[1]
    assert "from `develop` into `main`" in release
