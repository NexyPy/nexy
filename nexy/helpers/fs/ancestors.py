"""Walking from a folder up to the folder where a search must stop."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path


def walk_up(start: Path, stop: Path) -> Iterator[Path]:
    """*start*, then each parent, ending with *stop* (or earlier at the filesystem root).

    Nothing is yielded when *start* is not inside *stop*.
    """
    current, stop = start.resolve(), stop.resolve()
    while current.is_relative_to(stop):
        yield current
        if current == stop or current.parent == current:
            return
        current = current.parent
