"""The version of Nexy the documentation describes, read from pyproject.toml.

The badge next to the logo names the minor line (`V2.2`), not the patch: a reader wants to know
which documentation they are reading, not which build made the site.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _minor(version: str) -> str:
    major, minor, *_ = version.split(".")
    return f"V{major}.{minor}"


def version() -> str:
    """`V2.2` for a project at `2.2.1`."""
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return _minor(data["project"]["version"])


VERSION = version()
