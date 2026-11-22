"""Audit the lowest versions Nexy allows, not only the locked ones (#601).

A lock that passes its audit says nothing of the floors: a user whose resolver lands on them gets
what they allow. The floors of `pyproject.toml`, and those `nx new` writes in a project's
`package.json`, are checked against OSV, the database pip-audit and npm audit read.
"""

from __future__ import annotations

import json
import re
import time
import tomllib
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
TEMPLATE = (
    ROOT / "nexy" / "modules" / "cli" / "templates" / "_shared" / "web" / "package.json.jinja2"
)
OSV = "https://api.osv.dev/v1/querybatch"
# Documented in SECURITY.md ("Dependency audit register"), as for the lock audit.
IGNORED = {"PYSEC-2022-252"}
ATTEMPTS = 3
_PYTHON_FLOOR = re.compile(r"([A-Za-z0-9_.-]+)(?:\[[^\]]*\])?\s*>=\s*([0-9][^,;\s]*)")
_NPM_FLOOR = re.compile(r'"([@a-z0-9/._-]+)":\s*"\^([0-9][^"]*)"')


def python_floors(pyproject: Path) -> dict[str, str]:
    """The lowest version of each runtime dependency that has one."""
    dependencies = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["dependencies"]
    found = (_PYTHON_FLOOR.match(dependency) for dependency in dependencies)
    return {match[1]: match[2] for match in found if match}


def npm_floors(template: Path) -> dict[str, str]:
    """The lowest version of each package a caret range allows."""
    return dict(_NPM_FLOOR.findall(template.read_text(encoding="utf-8")))


def _post(body: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        OSV, json.dumps(body).encode(), {"Content-Type": "application/json"}
    )
    for attempt in range(1, ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(request, timeout=60) as answer:  # nosec B310: fixed https URL
                return dict(json.load(answer))
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == ATTEMPTS:
                raise
            print(f"[audit] OSV unreachable, retrying ({attempt}/{ATTEMPTS})")
            time.sleep(attempt * 10)
    raise AssertionError("unreachable")


def advisories(
    ecosystem: str,
    floors: dict[str, str],
    post: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, list[str]]:
    """The advisories of each floor, by package; a package without one is left out."""
    queries = [
        {"package": {"name": n, "ecosystem": ecosystem}, "version": v} for n, v in floors.items()
    ]
    results = (post or _post)({"queries": queries})["results"]
    found: dict[str, list[str]] = {}
    for name, result in zip(floors, results, strict=False):
        ids = [vuln["id"] for vuln in result.get("vulns", []) if vuln["id"] not in IGNORED]
        if ids:
            found[name] = ids
    return found


def main() -> int:
    """Print each floor with an advisory; fail when there is one."""
    found = {
        **{
            f"{n} (pyproject.toml)": ids
            for n, ids in advisories("PyPI", python_floors(PYPROJECT)).items()
        },
        **{f"{n} (nx new)": ids for n, ids in advisories("npm", npm_floors(TEMPLATE)).items()},
    }
    for name, ids in found.items():
        print(f"[audit] floor {name}: {', '.join(ids)}")
    if not found:
        print("[audit] no floor has a known advisory")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
