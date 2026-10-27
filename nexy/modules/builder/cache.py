"""The build cache: which route files are unchanged since the last build."""

from __future__ import annotations

import json
from pathlib import Path

_CONFIG_KEY = "__config__"


class BuildCache:
    """Fingerprints by path, kept in `__nexy__/build-cache.json` between `nx build` runs.

    In dev mode the compiled output lives only in memory, so a cache read from disk would skip
    compilation entirely and leave the VFS empty: a dev cache starts empty and is never saved.
    """

    def __init__(self, file: Path, persistent: bool) -> None:
        self._file = file
        self._persistent = persistent
        self.entries: dict[str, str] = self._read() if persistent else {}

    def _read(self) -> dict[str, str]:
        try:
            loaded = json.loads(self._file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return loaded if isinstance(loaded, dict) else {}

    def start(self, config_fingerprint: str, incremental: bool) -> None:
        """Forget everything when the configuration changed; remember its fingerprint."""
        if incremental and self.entries.get(_CONFIG_KEY) != config_fingerprint:
            self.entries = {}
        self.entries[_CONFIG_KEY] = config_fingerprint

    def is_current(self, path: str, fingerprint: str) -> bool:
        return self.entries.get(path) == fingerprint

    def remember(self, path: str, fingerprint: str) -> None:
        self.entries[path] = fingerprint

    def save(self) -> None:
        if not self._persistent:
            return
        self._file.parent.mkdir(parents=True, exist_ok=True)
        self._file.write_text(json.dumps(self.entries, ensure_ascii=False), encoding="utf-8")
