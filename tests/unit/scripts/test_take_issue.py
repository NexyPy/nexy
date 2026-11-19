"""scripts/take_issue.py: `/take` on an open contributor issue assigns it to the commenter."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "take_issue.py"
OPEN = "good first issue,difficulty:beginner"


@pytest.fixture(name="take", scope="module")
def _take() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("take_issue", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve their annotations through it
    spec.loader.exec_module(module)
    return module


def test_take_assigns_a_free_issue(take):
    assert take.decide("ana", "", OPEN).action == "assign"


def test_take_accepts_help_wanted_issues(take):
    assert take.decide("ana", "", "help wanted,difficulty:advanced").action == "assign"


def test_take_names_who_already_has_the_issue(take):
    assert "@bob" in take.decide("ana", "bob", OPEN).message


def test_take_does_not_assign_a_taken_issue(take):
    assert take.decide("ana", "bob", OPEN).action == "reply"


def test_take_ignores_a_second_take_by_the_assignee(take):
    assert take.decide("ana", "ana", OPEN).action == "none"


def test_take_refuses_an_issue_not_open_to_contributors(take):
    assert take.decide("ana", "", "bug,area:cli").action == "reply"


def test_take_points_a_refused_contributor_to_the_board(take):
    assert "projects/2" in take.decide("ana", "", "bug").message


def test_take_ignores_the_maintainer(take):
    assert take.decide("Espoir-Loem", "", OPEN).action == "none"


@pytest.mark.parametrize("body", ["/take", "/take\n", "  /take please"])
def test_wants_reads_a_take_command(take, body):
    assert take.wants(body)


@pytest.mark.parametrize("body", ["I will /take it", "/taken", "/takeover"])
def test_wants_ignores_other_comments(take, body):
    assert not take.wants(body)


def test_welcome_fills_the_login_and_the_number(take, tmp_path):
    template = tmp_path / "welcome.md"
    template.write_text("Thanks @{{assignee}}, #{{number}} is yours!", encoding="utf-8")
    assert take.welcome(template, "ana", "454") == "Thanks @ana, #454 is yours!"


def _run(take, monkeypatch, tmp_path, **env) -> list[tuple[str, ...]]:
    calls: list[tuple[str, ...]] = []
    template = tmp_path / "welcome.md"
    template.write_text("Thanks @{{assignee}}", encoding="utf-8")
    monkeypatch.setattr(take, "WELCOME", template)
    monkeypatch.setattr(take, "_gh", lambda *args: calls.append(args))
    for name, value in {"NUMBER": "7", "ASSIGNEES": "", "LABELS": OPEN, **env}.items():
        monkeypatch.setenv(name, value)
    take.main()
    return calls


def test_main_assigns_then_welcomes(take, monkeypatch, tmp_path):
    calls = _run(take, monkeypatch, tmp_path, LOGIN="ana", BODY="/take")
    assert calls == [
        ("issue", "edit", "7", "--add-assignee", "ana"),
        ("issue", "comment", "7", "--body", "Thanks @ana"),
    ]


def test_main_answers_a_take_on_a_taken_issue(take, monkeypatch, tmp_path):
    calls = _run(take, monkeypatch, tmp_path, LOGIN="ana", BODY="/take", ASSIGNEES="bob")
    assert calls[0][:3] == ("issue", "comment", "7")


def test_main_does_nothing_for_another_comment(take, monkeypatch, tmp_path):
    assert _run(take, monkeypatch, tmp_path, LOGIN="ana", BODY="Nice!") == []
