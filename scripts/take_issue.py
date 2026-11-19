"""Answer `/take` on an issue: assign a free contributor issue to the person who asked.

The `Take` workflow runs it on each new issue comment, with the event in the environment:
LOGIN (who commented), BODY (the comment), NUMBER, ASSIGNEES (space-separated logins) and LABELS
(comma-separated names). An issue labelled `good first issue` or `help wanted` and assigned to
nobody goes to the commenter, who gets `.github/CONTRIBUTOR_WELCOME.md`. A taken issue or another
kind of issue gets a short answer instead. An assignment made with the workflow token starts no
other workflow, so the welcome is posted here and not by the `Welcome` workflow.
"""

from __future__ import annotations

import os
import re
import subprocess  # nosec B404 - runs the gh CLI with fixed arguments
from dataclasses import dataclass
from pathlib import Path

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


def decide(login: str, assignees: str, labels: str) -> Decision:
    """What to do with a `/take` from *login* on an issue with these assignees and labels."""
    taken = assignees.split()
    if login == MAINTAINER or login in taken:
        return Decision("none")
    if not OPEN_LABELS & {label.strip() for label in labels.split(",")}:
        return Decision("reply", f"This issue is not open to contributors yet: see {BOARD}.")
    if taken:
        owner = ", ".join(f"@{name}" for name in taken)
        return Decision("reply", f"{owner} already has this one. Free issues are on {BOARD}.")
    return Decision("assign")


def welcome(template: Path, login: str, number: str) -> str:
    text = template.read_text(encoding="utf-8")
    return text.replace("{{assignee}}", login).replace("{{number}}", number)


def _gh(*args: str) -> None:
    subprocess.run(["gh", *args], check=True)  # nosec B603 B607 - fixed command, no shell


def main() -> None:
    env = os.environ
    if not wants(env["BODY"]):
        return
    login, number = env["LOGIN"], env["NUMBER"]
    decision = decide(login, env.get("ASSIGNEES", ""), env.get("LABELS", ""))
    if decision.action == "assign":
        _gh("issue", "edit", number, "--add-assignee", login)
        _gh("issue", "comment", number, "--body", welcome(WELCOME, login, number))
    elif decision.action == "reply":
        _gh("issue", "comment", number, "--body", f"@{login} {decision.message}")


if __name__ == "__main__":
    main()
