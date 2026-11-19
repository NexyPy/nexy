"""Every new contributor gets the same welcome when a good first issue is assigned to them."""

from __future__ import annotations

from pathlib import Path

import pytest

WELCOME = Path(__file__).resolve().parents[3] / ".github" / "CONTRIBUTOR_WELCOME.md"


@pytest.mark.parametrize("placeholder", ["{{assignee}}", "{{number}}"])
def test_welcome_names_the_contributor_and_the_issue(placeholder):
    assert placeholder in WELCOME.read_text("utf-8")


@pytest.mark.parametrize(
    "link",
    [
        "https://www.linkedin.com/company/nexy-dev/",
        "https://www.reddit.com/r/nexyframework/",
        "CONTRIBUTING.md",
    ],
)
def test_welcome_points_to_the_community(link):
    assert link in WELCOME.read_text("utf-8")


def test_welcome_says_a_star_or_a_follow_is_never_required():
    assert "None of this is required to contribute" in WELCOME.read_text("utf-8")


def test_welcome_says_an_idle_issue_is_freed_after_14_days():
    assert "14 days" in WELCOME.read_text("utf-8")
