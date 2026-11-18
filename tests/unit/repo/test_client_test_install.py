"""The client tests install with pnpm, like every other JavaScript package of the repository."""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]


def _steps() -> list[dict]:
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "ci.yml").read_text("utf-8"))
    return [step for job in workflow["jobs"].values() for step in job.get("steps", [])]


def test_ci_installs_the_client_tests_from_their_pnpm_lock():
    runs = [step.get("run", "") for step in _steps()]
    assert "pnpm install --frozen-lockfile --dir tests/client" in runs


def test_no_npm_lock_is_left_in_the_repository():
    tracked = subprocess.run(
        ["git", "ls-files", "*package-lock.json"],
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
    ).stdout.split()
    assert tracked == []
