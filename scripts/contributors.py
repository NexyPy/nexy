"""Write the Thanks section of a release: every pull request a contributor got merged since a tag.

    python scripts/contributors.py v2.6.4

It prints a Markdown section to paste under the version in CHANGELOG.md and in the GitHub
Release, or nothing when only the maintainer and bots merged. A contributor sees their name in the
notes of the release that ships their work.
"""

from __future__ import annotations

import argparse
import json
import subprocess  # nosec B404 - runs git and the gh CLI with fixed arguments
from typing import Any

MAINTAINER = "Espoir-Loem"


def _credited(pr: dict[str, Any]) -> bool:
    author = pr["author"]
    return not author.get("is_bot") and author["login"] != MAINTAINER


def thanks(prs: list[dict[str, Any]]) -> str:
    """The section, by contributor then by pull request number; empty when nobody is credited."""
    credited = sorted(
        (pr for pr in prs if _credited(pr)),
        key=lambda pr: (pr["author"]["login"].lower(), pr["number"]),
    )
    if not credited:
        return ""
    lines = [f"- @{pr['author']['login']}: {pr['title']} (#{pr['number']})" for pr in credited]
    return "\n".join(["### Thanks", "", *lines, ""])


def _run(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout  # nosec B603


def merged_since(tag: str) -> list[dict[str, Any]]:
    """The pull requests merged after the commit of *tag*, into any branch: a release pull request
    is the maintainer's, so nothing is counted twice."""
    since = _run("git", "log", "-1", "--format=%cI", tag).strip()
    found = _run(
        "gh",
        "pr",
        "list",
        "--state",
        "merged",
        "--limit",
        "500",
        "--search",
        f"merged:>{since}",
        "--json",
        "number,title,author",
    )
    return list(json.loads(found))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tag", help="the previous release, such as v2.6.4")
    print(thanks(merged_since(parser.parse_args().tag)), end="")


if __name__ == "__main__":
    main()
