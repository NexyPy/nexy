"""Dependabot keeps the action pins and the locks current, one grouped pull request a month.

See #298.
"""

from __future__ import annotations

import subprocess
from pathlib import Path, PurePosixPath

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]


def _updates() -> dict[str, dict]:
    config = yaml.safe_load((ROOT / ".github" / "dependabot.yml").read_text("utf-8"))
    return {update["package-ecosystem"]: update for update in config["updates"]}


@pytest.mark.parametrize("ecosystem", ["github-actions", "uv", "npm"])
def test_dependabot_updates_the_ecosystem(ecosystem):
    assert ecosystem in _updates()


def test_dependabot_opens_its_pull_requests_against_develop():
    assert {update["target-branch"] for update in _updates().values()} == {"develop"}


def test_dependabot_groups_each_ecosystem_in_one_pull_request():
    assert all(len(update["groups"]) == 1 for update in _updates().values())


def test_dependabot_updates_every_pnpm_lock_but_the_examples():
    tracked = subprocess.run(
        ["git", "ls-files", "*pnpm-lock.yaml"], capture_output=True, text=True, check=True, cwd=ROOT
    ).stdout.split()
    kept = [lock for lock in tracked if not lock.startswith("examples/")]
    # git gives / on every system; Path would write backslashes on Windows.
    locks = sorted(f"/{PurePosixPath(lock).parent}" for lock in kept)
    assert _updates()["npm"]["directories"] == locks


def test_dependabot_sends_a_javascript_major_release_on_its_own():
    assert _updates()["npm"]["groups"]["javascript"]["update-types"] == ["minor", "patch"]
