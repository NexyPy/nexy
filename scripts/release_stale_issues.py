"""Free a contributor issue its assignee has not worked on for 14 days.

The `Release stale issues` workflow runs it once a day. An open issue labelled `good first issue`
or `help wanted` and assigned to someone other than the maintainer is stale when, for 14 days,
that person neither commented on it nor opened a pull request that mentions it. The assignee is
removed with a kind note, so the issue shows as free again and they can `/take` it back.
"""

from __future__ import annotations

import json
import subprocess  # nosec B404 - runs the gh CLI with fixed arguments
from datetime import UTC, datetime, timedelta
from typing import Any

MAINTAINER = "Espoir-Loem"
LABELS = ("good first issue", "help wanted")
IDLE = timedelta(days=14)


def _at(event: dict[str, Any]) -> datetime:
    return datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))


def _by(event: dict[str, Any], login: str) -> bool:
    """An assignment to *login*, or a comment *login* wrote."""
    if event.get("event") == "assigned":
        return bool(event.get("assignee", {}).get("login") == login)
    return event.get("event") == "commented" and event.get("actor", {}).get("login") == login


def _open_pull_request(event: dict[str, Any], login: str) -> bool:
    """A pull request by *login*, still open, that mentions the issue."""
    if event.get("event") != "cross-referenced":
        return False
    issue = event.get("source", {}).get("issue", {})
    mine = issue.get("user", {}).get("login") == login
    return mine and "pull_request" in issue and issue.get("state") == "open"


def is_stale(events: list[dict[str, Any]], login: str, now: datetime) -> bool:
    """True when *login* was assigned and did nothing on the issue for 14 days."""
    if any(_open_pull_request(event, login) for event in events):
        return False
    moments = [_at(event) for event in events if _by(event, login)]
    return bool(moments) and now - max(moments) > IDLE


def note(login: str) -> str:
    return (
        f"@{login}, this issue had no update for 14 days, so it is free again for someone else. "
        "No problem at all: comment `/take` to have it back whenever you can work on it."
    )


def contributors(issue: dict[str, Any]) -> list[str]:
    return [person["login"] for person in issue["assignees"] if person["login"] != MAINTAINER]


def _gh(*args: str) -> str:
    done = subprocess.run(["gh", *args], check=True, capture_output=True, text=True)  # nosec B603 B607
    return done.stdout


def _issues() -> list[dict[str, Any]]:
    found: dict[int, dict[str, Any]] = {}
    for label in LABELS:
        listed = _gh("issue", "list", "--label", label, "--json", "number,assignees")
        found.update({issue["number"]: issue for issue in json.loads(listed)})
    return list(found.values())


def _timeline(number: int) -> list[dict[str, Any]]:
    pages = _gh(
        "api", "--paginate", "--slurp", f"repos/{{owner}}/{{repo}}/issues/{number}/timeline"
    )
    return [event for page in json.loads(pages) for event in page]


def _now() -> datetime:
    return datetime.now(UTC)


def main() -> None:
    for issue in _issues():
        number = str(issue["number"])
        for login in contributors(issue):
            if is_stale(_timeline(issue["number"]), login, _now()):
                _gh("issue", "edit", number, "--remove-assignee", login)
                _gh("issue", "comment", number, "--body", note(login))


if __name__ == "__main__":
    main()
