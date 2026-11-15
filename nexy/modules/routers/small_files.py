"""Small public files kept in memory, with the headers a FileResponse would send.

Starlette's FileResponse runs its stat, open, each read and its close in the thread pool: about
sixteen hops for a 4 KB file, which made a logo slower to serve than a rendered page. A file under
`max_file` is read once and answered from memory; its stat on each request notices a change.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from starlette.responses import FileResponse

_Stamp = tuple[int, int]


@dataclass(frozen=True)
class CachedFile:
    stamp: _Stamp
    headers: list[tuple[bytes, bytes]]
    body: bytes


class SmallFiles:
    """Files up to `max_file` bytes each, `max_total` bytes in all; larger ones are not kept."""

    def __init__(self, max_file: int = 256 * 1024, max_total: int = 32 * 1024 * 1024) -> None:
        self.max_file = max_file
        self.max_total = max_total
        self._entries: dict[Path, CachedFile] = {}
        self._total = 0

    def get(self, path: Path, stat: os.stat_result) -> CachedFile | None:
        """The file as it is on disk now, or None when it is too large to keep."""
        if stat.st_size > self.max_file:
            return None
        known = self._entries.get(path)
        if known is not None and known.stamp == (stat.st_mtime_ns, stat.st_size):
            return known
        return self._load(path, stat)

    def _load(self, path: Path, stat: os.stat_result) -> CachedFile | None:
        body = path.read_bytes()
        previous = self._entries.pop(path, None)
        self._total -= len(previous.body) if previous else 0
        if len(body) != stat.st_size or self._total + len(body) > self.max_total:
            return None
        headers = FileResponse(path, stat_result=stat).raw_headers
        entry = CachedFile((stat.st_mtime_ns, stat.st_size), headers, body)
        self._entries[path] = entry
        self._total += len(body)
        return entry
