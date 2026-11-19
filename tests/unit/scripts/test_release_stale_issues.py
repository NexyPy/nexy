"""scripts/release_stale_issues.py frees a contributor issue nobody worked on for 14 days."""

from __future__ import annotations

import importlib.util
import sys
import types
from datetime import UTC, datetime
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "release_stale_issues.py"
NOW = datetime(2026, 12, 1, tzinfo=UTC)


@pytest.fixture(name="stale", scope="module")
def _stale() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("release_stale_issues", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _assigned(login: str, day: int) -> dict:
    return {
        "event": "assigned",
        "assignee": {"login": login},
        "created_at": f"2026-11-{day:02d}T10:00:00Z",
    }


def _comment(login: str, day: int) -> dict:
    return {
        "event": "commented",
        "actor": {"login": login},
        "created_at": f"2026-11-{day:02d}T10:00:00Z",
    }


def _pr(login: str, state: str = "open") -> dict:
    issue = {"pull_request": {}, "state": state, "user": {"login": login}}
    return {
        "event": "cross-referenced",
        "created_at": "2026-11-20T10:00:00Z",
        "source": {"issue": issue},
    }


def test_an_issue_assigned_15_days_ago_with_nothing_since_is_stale(stale):
    assert stale.is_stale([_assigned("ana", 16)], "ana", NOW)


def test_an_issue_assigned_10_days_ago_is_not_stale(stale):
    assert not stale.is_stale([_assigned("ana", 21)], "ana", NOW)


def test_a_comment_by_the_assignee_keeps_the_issue(stale):
    assert not stale.is_stale([_assigned("ana", 1), _comment("ana", 25)], "ana", NOW)


def test_a_comment_by_someone_else_does_not_keep_it(stale):
    assert stale.is_stale([_assigned("ana", 1), _comment("bob", 25)], "ana", NOW)


def test_an_open_pull_request_by_the_assignee_keeps_the_issue(stale):
    assert not stale.is_stale([_assigned("ana", 1), _pr("ana")], "ana", NOW)


def test_a_closed_pull_request_does_not_keep_it(stale):
    assert stale.is_stale([_assigned("ana", 1), _pr("ana", "closed")], "ana", NOW)


def test_an_issue_never_assigned_to_them_is_left_alone(stale):
    assert not stale.is_stale([], "ana", NOW)


def test_the_note_invites_them_back(stale):
    assert "/take" in stale.note("ana")


def _issue(*logins: str) -> dict:
    return {"number": 7, "assignees": [{"login": login} for login in logins]}


def test_contributors_leaves_the_maintainer_out(stale):
    assert stale.contributors(_issue("Espoir-Loem", "ana")) == ["ana"]


def test_main_frees_a_stale_issue(stale, monkeypatch):
    calls: list[tuple[str, ...]] = []
    monkeypatch.setattr(stale, "_issues", lambda: [_issue("ana")])
    monkeypatch.setattr(stale, "_timeline", lambda _number: [_assigned("ana", 1)])
    monkeypatch.setattr(stale, "_gh", lambda *args: calls.append(args))
    monkeypatch.setattr(stale, "_now", lambda: NOW)
    stale.main()
    assert calls[0] == ("issue", "edit", "7", "--remove-assignee", "ana")
