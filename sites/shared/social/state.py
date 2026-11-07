"""What has already gone out, in a file git keeps, so nothing is sent twice.

The key is `posts/<slug>/<lang>/<platform>`: the same post in French on LinkedIn is a different
publication from the same post in English on Bluesky, and each one is marked on its own.
"""

from __future__ import annotations

import json
from pathlib import Path

from sites.shared.social import Item

__all__ = ["STATE", "key", "load", "mark", "save", "sent"]

STATE = ".published.json"


def load(path: Path) -> dict[str, str]:
    """What was published, read from disk; an absent file means nothing was."""
    if not path.is_file():
        return {}
    loaded: dict[str, str] = json.loads(path.read_text(encoding="utf-8"))
    return loaded


def save(path: Path, state: dict[str, str]) -> None:
    """Write the state back, sorted, so a diff of the file reads like a log."""
    path.write_text(json.dumps(dict(sorted(state.items())), indent=2) + "\n", encoding="utf-8")


def key(item: Item, platform: str) -> str:
    """How one publication is named: the slug, the language and the network."""
    return f"{item.category}/{item.slug}/{item.lang}/{platform}"


def sent(state: dict[str, str], item: Item, platform: str) -> bool:
    """True when this exact post, in this language, already went out on that network."""
    return key(item, platform) in state


def mark(state: dict[str, str], item: Item, platform: str, when: str) -> dict[str, str]:
    """The same state with one more publication, dated."""
    return {**state, key(item, platform): when}
