"""Turning the raw batch of a file watcher into one clear change per file."""

from __future__ import annotations

import os
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Literal

from watchfiles import Change

from nexy.modules.cli.devtools.watch.paths import normalize_path

Kind = Literal["created", "modified", "deleted"]


@dataclass(frozen=True)
class FileChange:
    """What happened to one file in a batch."""

    kind: Kind
    path: str


def _kind(changes: set[Change], still_there: bool) -> Kind:
    """One verdict for a file: an atomic save (added and deleted together) is a modification."""
    if not still_there:
        return "deleted"
    if Change.added in changes and Change.deleted not in changes:
        return "created"
    return "modified"


def classify(
    batch: Iterable[tuple[Change, str]],
    exists: Callable[[str], bool] = os.path.exists,
) -> list[FileChange]:
    """One `FileChange` per path of *batch*, sorted by path."""
    by_path: dict[str, set[Change]] = defaultdict(set)
    for change, raw in batch:
        by_path[normalize_path(raw)].add(change)
    return [FileChange(_kind(by_path[path], exists(path)), path) for path in sorted(by_path)]
