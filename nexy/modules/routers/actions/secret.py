"""The secret that makes the path of an action specific to one project."""

from __future__ import annotations

import contextlib
import os
import secrets
from pathlib import Path

_ENV = "NEXY_ACTION_SECRET"
_FILE = Path("__nexy__") / "action.key"
_cached: str | None = None


def action_secret() -> str:
    """`NEXY_ACTION_SECRET`, else a random key kept in `__nexy__/action.key`."""
    global _cached
    if _cached is None:
        _cached = os.environ.get(_ENV) or _read_or_create()
    return _cached


def _read_or_create() -> str:
    with contextlib.suppress(OSError):
        existing = _FILE.read_text(encoding="utf-8").strip()
        if existing:
            return existing
    key = secrets.token_hex(32)
    with contextlib.suppress(OSError):
        _FILE.parent.mkdir(parents=True, exist_ok=True)
        _FILE.write_text(key, encoding="utf-8")
    return key


def forget_secret() -> None:
    """Read the secret again on next use (tests, and a project folder change)."""
    global _cached
    _cached = None
