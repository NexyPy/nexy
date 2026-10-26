"""Find what is wrong with a Python file before the dev server is asked to reload it."""

from __future__ import annotations

import ast
import linecache
import traceback
from dataclasses import dataclass
from pathlib import Path

from rich.markup import escape

from nexy.helpers.common.code_frame import Rows, print_frame, rows_around, rows_of_file
from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.modules.i18n import t

_FOREIGN_PARTS = {".venv", "venv", "site-packages", "node_modules"}


@dataclass(frozen=True)
class Problem:
    """An error in one file of the project."""

    location: str
    kind: str
    message: str
    line: int | None = None
    column: int | None = None
    rows: Rows = ()

    def format(self) -> str:
        return f"{self.location}  {self.kind}: {self.message}"


def project_path(filename: str, root: Path) -> str | None:
    """The path of *filename* inside the project, or None for code that is not the project's."""
    try:
        relative = Path(filename).resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return None
    if _FOREIGN_PARTS.intersection(relative.parts):
        return None
    return relative.as_posix()


def _syntax_problem(error: SyntaxError, location: str, lines: list[str]) -> Problem:
    line = error.lineno
    place = f"{location}:{line}" if line else location
    rows = rows_around(lines, line) if line else ()
    return Problem(place, type(error).__name__, error.msg, line, error.offset, rows)


def find_syntax_problem(path: str, root: Path | None = None) -> Problem | None:
    """Parse *path* without running it; None when it is valid or cannot be read."""
    try:
        source = Path(path).read_bytes()
    except OSError:
        return None
    location = project_path(path, root or Path.cwd()) or path
    try:
        ast.parse(source, filename=path)
    except SyntaxError as error:
        return _syntax_problem(error, location, source.decode("utf-8", "replace").splitlines())
    except ValueError as error:
        return Problem(location, type(error).__name__, str(error))
    return None


def describe(error: BaseException, root: Path | None = None) -> Problem:
    """Where in the project *error* came from, for an exception raised while importing it."""
    root = root or Path.cwd()
    if isinstance(error, SyntaxError) and error.filename:
        location = project_path(error.filename, root) or error.filename
        return _syntax_problem(error, location, linecache.getlines(error.filename))
    for frame in reversed(traceback.extract_tb(error.__traceback__)):
        inside = project_path(frame.filename, root)
        if inside:
            line = frame.lineno or 0
            rows = rows_of_file(frame.filename, line)
            return Problem(f"{inside}:{line}", type(error).__name__, str(error), line, None, rows)
    return Problem("-", type(error).__name__, str(error))


def report(problem: Problem, note: str | None = None) -> None:
    """Print a problem as the dev server shows it: where, what, the code around it, then a note."""
    label = t("dev.error_label", "error")
    what = f"[red]{label}[/red] {escape(problem.location)}  [bold]{escape(problem.kind)}[/bold]"
    console.print(tagged("nexy", f"{what}: {escape(problem.message)}", "red"))
    if problem.rows:
        console.print()
        print_frame(problem.rows, problem.line, problem.column)
        console.print()
    if note:
        console.print(f"  [dim]{escape(note)}[/dim]")
