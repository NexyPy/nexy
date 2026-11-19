"""CI runs on the two long-lived branches, `develop` and `main`, and on nothing that is gone."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]


def _workflow() -> dict:
    return yaml.safe_load((ROOT / ".github" / "workflows" / "ci.yml").read_text("utf-8"))


def test_ci_checks_pull_requests_into_develop_and_main():
    # YAML 1.1 reads the bare key `on` as the boolean true.
    assert _workflow()[True]["pull_request"]["branches"] == ["main", "develop"]


def test_ci_pushes_name_no_removed_branch():
    assert "V2" not in _workflow()[True]["push"]["branches"]
