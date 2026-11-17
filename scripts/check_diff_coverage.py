"""Fail when a line this change adds to nexy/ never runs in a test, or a branch is never taken.

The coverage floor of pyproject.toml guards the whole package; this gate guards the change: every
added executable line must run, and every branch it opens must be taken, in at least one test.

Usage (after `pytest --cov=nexy --cov-report=json:.coverage.json`):
    python scripts/check_diff_coverage.py [--base origin/develop] [--report .coverage.json]
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

PACKAGE = "nexy/"
SKIPPED = ("nexy/modules/cli/templates/",)
_FILE = re.compile(r"^\+\+\+ b/(.+)$")
_HUNK = re.compile(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@")


def _checked(path: str) -> bool:
    return path.startswith(PACKAGE) and path.endswith(".py") and not path.startswith(SKIPPED)


def added_lines(diff: str) -> dict[str, set[int]]:
    """The line numbers each file of the package gains in a `git diff -U0`."""
    lines: dict[str, set[int]] = {}
    current: set[int] | None = None
    for row in diff.splitlines():
        if row.startswith("+++ "):
            match = _FILE.match(row)
            current = lines.setdefault(match[1], set()) if match and _checked(match[1]) else None
        elif current is not None and (hunk := _HUNK.match(row)):
            start, count = int(hunk[1]), int(hunk[2] or 1)
            current.update(range(start, start + count))
    return {path: numbers for path, numbers in lines.items() if numbers}


def has_code(path: str) -> bool:
    """False for a module that holds nothing but a docstring."""
    body = ast.parse(Path(path).read_text(encoding="utf-8")).body
    docstring = (
        bool(body) and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
    )
    return len(body) > int(docstring)


def _branch_gap(path: str, start: int, end: int) -> str:
    target = "the exit" if end < 0 else f"line {end}"
    return f"{path}:{start} has a branch no test takes (to {target})"


def _file_gaps(path: str, numbers: set[int], measured: dict[str, Any]) -> list[str]:
    missing = sorted(numbers.intersection(measured["missing_lines"]))
    found = [f"{path}:{line} never runs in a test" for line in missing]
    for start, end in measured["missing_branches"]:
        if start in numbers and start not in missing:
            found.append(_branch_gap(path, start, end))
    return found


def gaps(
    changed: dict[str, set[int]],
    report: dict[str, Any],
    has_code: Callable[[str], bool] = has_code,
) -> list[str]:
    """One sentence per added line or branch that no test runs."""
    found: list[str] = []
    for path, numbers in sorted(changed.items()):
        measured = report["files"].get(path)
        if measured is not None:
            found.extend(_file_gaps(path, numbers, measured))
        elif has_code(path):
            found.append(f"{path} is never imported by a test")
    return found


def _diff(base: str) -> str:
    merge_base = subprocess.run(
        ["git", "merge-base", base, "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    command = ["git", "diff", "-U0", "--no-color", merge_base, "--", PACKAGE]
    return subprocess.run(command, capture_output=True, text=True, check=True).stdout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="origin/develop")
    parser.add_argument("--report", default=".coverage.json")
    args = parser.parse_args(argv)
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    found = gaps(added_lines(_diff(args.base)), report)
    for gap in found:
        print(f"error: {gap}")
    if found:
        print(f"{len(found)} added line(s) or branch(es) run in no test: write the test first.")
        return 1
    print("Every added line of nexy/ runs in a test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
