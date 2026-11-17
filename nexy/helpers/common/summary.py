"""The list a build leaves: one line of counts, then the files it made, as uv lists packages."""

from __future__ import annotations

from rich.console import Console
from rich.markup import escape

from nexy.helpers.common.console import console as _console
from nexy.helpers.common.formatting import artifact_size

MAX_SHOWN = 3


def _file_line(path: str) -> str:
    size = artifact_size(path)
    return f" [green]+[/green] {escape(path)}" + (f"  [dim]{size}[/dim]" if size else "")


def print_summary(
    title: str,
    counts: list[str],
    files: list[str],
    *,
    more: str = "and {count} more",
    console: Console | None = None,
) -> None:
    """``title: counts``, then the first files and how many more (*more* is translated)."""
    out = console or _console
    out.print(f"{title}: [bold]{escape(', '.join(counts))}[/bold]")
    for path in files[:MAX_SHOWN]:
        out.print(_file_line(path))
    if len(files) > MAX_SHOWN:
        out.print(f"   [dim]{more.format(count=len(files) - MAX_SHOWN)}[/dim]")
