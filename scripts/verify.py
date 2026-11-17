"""Run every quality gate in order, stopping at the first failure.

One command proves the working state; the CI matrix runs the same gates.
Usage: python scripts/verify.py
"""

import subprocess
import sys

GATES: list[tuple[str, list[str]]] = [
    ("lint", ["-m", "ruff", "check", "nexy/", "tests/", "sites/", "scripts/"]),
    ("format", ["-m", "ruff", "format", "nexy/", "tests/", "sites/", "scripts/", "--check"]),
    ("typecheck", ["-m", "mypy", "nexy", "--strict"]),
    (
        "typecheck-sites",
        [
            "-m",
            "mypy",
            "sites/shared/social",
            "scripts/publish_social.py",
            "scripts/make_com_media.py",
            "scripts/check_diff_coverage.py",
            "--strict",
        ],
    ),
    ("structure", ["scripts/audit_structure.py", "--check"]),
    ("com", ["scripts/publish_social.py", "--check"]),
    # The suite runs once, with coverage: the floor of pyproject.toml guards the package, and
    # diff-coverage reads the same report to require a test for every line this change adds.
    (
        "test",
        ["-m", "pytest", "tests/", "-q", "--cov=nexy", "--cov-report=json:.coverage.json"],
    ),
    ("diff-coverage", ["scripts/check_diff_coverage.py", "--report", ".coverage.json"]),
    ("security", ["-m", "bandit", "-r", "nexy/", "-c", ".bandit", "-q"]),
]


def main() -> int:
    for name, args in GATES:
        print(f"[verify] {name}: python {' '.join(args)}")
        result = subprocess.run([sys.executable, *args], check=False)
        if result.returncode != 0:
            print(f"[verify] FAILED at {name}")
            return result.returncode
        print(f"[verify] {name}: ok")
    print("[verify] all gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
