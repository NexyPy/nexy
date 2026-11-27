"""Read the registry token without ever printing it."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

TOKEN_ENV = "NEXY_REGISTRY_TOKEN"
LOGIN_FILE = Path(".config/nexy/registry-token")


def resolve_token(env: Mapping[str, str], home: Path) -> str:
    """Return the token from the environment, or from a login file."""
    return env.get(TOKEN_ENV, "").strip() or _from_login(home)


def _from_login(home: Path) -> str:
    try:
        return (home / LOGIN_FILE).read_text(encoding="utf-8").strip()
    except OSError:
        return ""
