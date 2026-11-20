"""Answer `/take` on an issue: assign a free contributor issue to the person who asked.

The `Take` workflow runs it on each new issue comment, with the event in the environment:
LOGIN (who commented), BODY (the comment), NUMBER, ASSIGNEES (space-separated logins) and LABELS
(comma-separated names). An issue labelled `good first issue` or `help wanted`, assigned to nobody
and with no open pull request by someone else, goes to the commenter, who gets
`.github/CONTRIBUTOR_WELCOME.md`. Any other issue gets a short answer instead. The welcome is
posted here: the `Welcome` workflow leaves an assignment made by a bot alone, and one made with the
workflow token starts no workflow at all.
"""

from __future__ import annotations

import json
import os
import re
import subprocess  # nosec B404 - runs the gh CLI with fixed arguments
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MAINTAINER = "Espoir-Loem"
OPEN_LABELS = {"good first issue", "help wanted"}
BOARD = "https://github.com/orgs/NexyPy/projects/2"
WELCOME = Path(".github/CONTRIBUTOR_WELCOME.md")
COMMAND = re.compile(r"\s*/take(\s|$)")


@dataclass(frozen=True)
class Decision:
    action: str  # "assign", "reply" or "none"
    message: str = ""


def wants(body: str) -> bool:
    """True when the comment starts with the `/take` command."""
    return COMMAND.match(body) is not None


def pull_requests(events: list[dict[str, Any]], login: str) -> list[tuple[int, str]]:
    """(number, author) of each open pull request by someone else that mentions the issue."""
    found = []
    for event in events:
        source = event.get("source", {}).get("issue", {})
        author = source.get("user", {}).get("login", "")
        if "pull_request" in source and source.get("state") == "open" and author != login:
            found.append((source["number"], author))
    return found


def decide(
    login: str, assignees: str, labels: str, pulls: list[tuple[int, str]] | None = None
) -> Decision:
    """What to do with a `/take` from *login* on an issue with these assignees, labels and PRs."""
    taken = assignees.split()
    if login == MAINTAINER or login in taken:
        return Decision("none")
    if not OPEN_LABELS & {label.strip() for label in labels.split(",")}:
        return Decision("reply", f"This issue is not open to contributors yet: see {BOARD}.")
    if taken:
        owner = ", ".join(f"@{name}" for name in taken)
        return Decision("reply", f"{owner} already has this one. Free issues are on {BOARD}.")
    if pulls:
        number, author = pulls[0]
        said = f"@{author} already opened #{number} for this one. Free issues are on {BOARD}."
        return Decision("reply", said)
    return Decision("assign")


def welcome(template: Path, login: str, number: str) -> str:
    text = template.read_text(encoding="utf-8")
    return text.replace("{{assignee}}", login).replace("{{number}}", number)


def _gh(*args: str) -> None:
    subprocess.run(["gh", *args], check=True)  # nosec B603 B607 - fixed command, no shell


def _timeline(number: str) -> list[dict[str, Any]]:
    """The events of the issue, where a pull request that mentions it shows up."""
    path = f"repos/{{owner}}/{{repo}}/issues/{number}/timeline"
    done = subprocess.run(  # nosec B603 B607 - fixed command, no shell
        ["gh", "api", "--paginate", "--slurp", path], check=True, capture_output=True, text=True
    )
    return [event for page in json.loads(done.stdout) for event in page]


def main() -> None:
    env = os.environ
    if not wants(env["BODY"]):
        return
    login, number = env["LOGIN"], env["NUMBER"]
    pulls = pull_requests(_timeline(number), login)
    decision = decide(login, env.get("ASSIGNEES", ""), env.get("LABELS", ""), pulls)
    if decision.action == "assign":
        _gh("issue", "edit", number, "--add-assignee", login)
        _gh("issue", "comment", number, "--body", welcome(WELCOME, login, number))
    elif decision.action == "reply":
        _gh("issue", "comment", number, "--body", f"@{login} {decision.message}")


if __name__ == "__main__":
    main()
