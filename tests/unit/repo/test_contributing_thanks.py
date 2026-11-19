"""The release process of CONTRIBUTING.md thanks the contributors of each release."""

from __future__ import annotations

from pathlib import Path

CONTRIBUTING = Path(__file__).resolve().parents[3] / "CONTRIBUTING.md"


def test_release_process_runs_the_contributors_script():
    release = CONTRIBUTING.read_text("utf-8").split("## Release process", 1)[1]
    assert "python scripts/contributors.py" in release
