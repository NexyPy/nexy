"""scripts/contributors.py writes the Thanks section of a release from its merged pull requests."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "contributors.py"


@pytest.fixture(name="credits", scope="module")
def _credits() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("contributors", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _pr(number: int, login: str, title: str = "feat: a change", bot: bool = False) -> dict:
    return {"number": number, "title": title, "author": {"login": login, "is_bot": bot}}


def test_thanks_names_a_contributor_and_their_pull_request(credits):
    text = credits.thanks([_pr(351, "tharunsridhar", "feat(server): add health endpoints")])
    assert "- @tharunsridhar: feat(server): add health endpoints (#351)" in text


def test_thanks_leaves_the_maintainer_out(credits):
    assert credits.thanks([_pr(1, "Espoir-Loem")]) == ""


def test_thanks_leaves_bots_out(credits):
    assert credits.thanks([_pr(2, "dependabot", bot=True)]) == ""


def test_thanks_opens_with_a_heading(credits):
    assert credits.thanks([_pr(3, "ana")]).startswith("### Thanks\n")


def test_thanks_lists_a_contributor_once_per_pull_request_in_order(credits):
    text = credits.thanks([_pr(9, "ana"), _pr(4, "bob"), _pr(5, "ana")])
    assert [line[:9] for line in text.splitlines()[2:]] == ["- @ana: f", "- @ana: f", "- @bob: f"]
