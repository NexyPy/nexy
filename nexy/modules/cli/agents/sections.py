"""The parts of a skill that fit one project: a part written for one mode reaches only that mode.

A skill marks such a part between two lines of its own::

    <!-- nexy:server -->
    ...
    <!-- /nexy:server -->

``server`` is a server-rendered project, ``client`` a client-routed one (``useCSR = True``),
``web`` either of them and ``api`` a project without views. Text without a marker reaches every
project. The markers are HTML comments, so a skill reads the same in the repository; they never
reach a project.
"""

from __future__ import annotations

import re
from pathlib import Path

from nexy.modules.cli.agents.profile import Profile

TAGS = ("server", "client", "web", "api")
MARKER = re.compile(r"^<!-- (/?)nexy:(\w+) -->$")
_BLANK_RUN = re.compile(r"\n{3,}")


def modes_of(profile: Profile) -> set[str]:
    """The modes whose parts a project keeps."""
    if profile.kind == "api":
        return {"api"}
    return {"web", "client" if profile.client_routed else "server"}


def fit(text: str, modes: set[str]) -> str:
    """*text* without its parts for other modes, and without any marker line."""
    kept: list[str] = []
    current: str | None = None
    for line in text.splitlines(keepends=True):
        marker = MARKER.match(line.strip())
        if marker:
            current = None if marker[1] else marker[2]
        elif current is None or current in modes:
            kept.append(line)
    return _BLANK_RUN.sub("\n\n", "".join(kept))


def fit_tree(folder: Path, modes: set[str]) -> None:
    """Fit every Markdown file under *folder* to *modes*, in place."""
    for path in folder.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        path.write_text(fit(text, modes), encoding="utf-8", newline="\n")
