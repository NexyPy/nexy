"""The workflows that talk to contributors speak as the Nexy bot once it is set up."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
ACTION = "actions/create-github-app-token@64ab729a6294000f5aa4a4bc0b73d1f32bc45510"
# workflow file: the permissions its bot token gets
WORKFLOWS = {
    "take": {"permission-issues": "write"},
    "welcome": {"permission-issues": "write"},
    "assign": {"permission-issues": "write", "permission-pull-requests": "write"},
}


def _steps(name: str) -> list[dict]:
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / f"{name}.yml").read_text("utf-8"))
    return next(iter(workflow["jobs"].values()))["steps"]


def _bot(name: str) -> dict:
    return next(step for step in _steps(name) if step.get("id") == "bot")


@pytest.mark.parametrize("name", WORKFLOWS)
def test_bot_token_comes_from_the_pinned_action(name):
    assert _bot(name)["uses"] == ACTION


@pytest.mark.parametrize("name", WORKFLOWS)
def test_bot_token_is_asked_only_once_the_app_is_set_up(name):
    assert _bot(name)["if"] == "${{ vars.NEXY_BOT_CLIENT_ID != '' }}"


@pytest.mark.parametrize("name", WORKFLOWS)
def test_bot_token_gets_only_the_permissions_of_the_workflow(name):
    given = {key: value for key, value in _bot(name)["with"].items() if key.startswith("perm")}
    assert given == WORKFLOWS[name]


@pytest.mark.parametrize("name", WORKFLOWS)
def test_bot_token_is_the_one_gh_uses(name):
    tokens = [step["env"]["GH_TOKEN"] for step in _steps(name) if "GH_TOKEN" in step.get("env", {})]
    assert tokens == ["${{ steps.bot.outputs.token || github.token }}"]
