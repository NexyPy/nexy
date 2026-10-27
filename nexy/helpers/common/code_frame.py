"""Show the line of a file that has a problem, with the lines around it, in the terminal."""

from __future__ import annotations

import linecache
from collections.abc import Sequence

from rich.markup import escape

from nexy.helpers.common.console import console

Rows = tuple[tuple[int, str], ...]
RADIUS = 3


def rows_around(lines: Sequence[str], line: int, radius: int = RADIUS) -> Rows:
    """The numbered lines from *radius* before *line* to *radius* after it (1-based)."""
    first, last = max(1, line - radius), min(len(lines), line + radius)
    return tuple((number, lines[number - 1].rstrip("\r\n")) for number in range(first, last + 1))


def rows_of_file(filename: str, line: int, radius: int = RADIUS) -> Rows:
    return rows_around(linecache.getlines(filename), line, radius)


def format_frame(rows: Rows, hit: int | None, column: int | None = None) -> list[str]:
    """Rich markup lines: a gutter with line numbers, `>` on the faulty line, a caret under it."""
    if not rows:
        return []
    width = len(str(rows[-1][0]))
    out = []
    for number, text in rows:
        mark, colour = (">", "red") if number == hit else (" ", "dim")
        out.append(f"  [{colour}]{mark} {number:>{width}} | {escape(text)}[/{colour}]")
        if number == hit and column:
            pad = " " * (width + 5 + _visual_column(text, column))
            out.append(f"  [red]{pad}^[/red]")
    return out


def _visual_column(text: str, column: int) -> int:
    """Characters to skip so the caret sits under the 1-based *column* (tabs count as one)."""
    return max(0, min(column, len(text) + 1) - 1)


def print_frame(rows: Rows, hit: int | None, column: int | None = None) -> None:
    for line in format_frame(rows, hit, column):
        console.print(line)
