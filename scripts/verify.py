"""Run every quality gate in order, stopping at the first failure.

One command proves the working state; the CI matrix runs the same gates.
Usage: python scripts/verify.py
"""

import subprocess
import sys

GATES: list[tuple[str, list[str]]] = [
    ("lint", ["-m", "ruff", "check", "nexy/", "tests/"]),
    ("format", ["-m", "ruff", "format", "nexy/", "tests/", "--check"]),
    ("typecheck", ["-m", "mypy", "nexy", "--strict"]),
    ("structure", ["scripts/audit_structure.py", "--check"]),
    ("test", ["-m", "pytest", "tests/", "-q"]),
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
