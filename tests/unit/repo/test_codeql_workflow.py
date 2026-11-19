"""CodeQL scans every language of the repository, on pull requests as well as after the merge."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]


def _workflow() -> dict:
    return yaml.safe_load((ROOT / ".github" / "workflows" / "codeql.yml").read_text("utf-8"))


def test_codeql_runs_on_a_pull_request_to_develop():
    # YAML 1.1 reads the bare key `on` as the boolean true.
    assert "develop" in _workflow()[True]["pull_request"]["branches"]


@pytest.mark.parametrize("language", ["python", "javascript-typescript", "actions"])
def test_codeql_scans_the_language(language):
    assert language in _workflow()["jobs"]["analyze"]["strategy"]["matrix"]["language"]
