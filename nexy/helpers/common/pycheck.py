"""Find what is wrong with a Python file before the dev server is asked to reload it."""

from __future__ import annotations

import ast
import traceback
from dataclasses import dataclass
from pathlib import Path

_FOREIGN_PARTS = {".venv", "venv", "site-packages", "node_modules"}


@dataclass(frozen=True)
class Problem:
    """An error in one file of the project."""

    location: str
    kind: str
    message: str

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


def _syntax_problem(error: SyntaxError, location: str) -> Problem:
    line = f":{error.lineno}" if error.lineno else ""
    return Problem(f"{location}{line}", type(error).__name__, error.msg)


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
        return _syntax_problem(error, location)
    except ValueError as error:
        return Problem(location, type(error).__name__, str(error))
    return None


def describe(error: BaseException, root: Path | None = None) -> Problem:
    """Where in the project *error* came from, for an exception raised while importing it."""
    root = root or Path.cwd()
    if isinstance(error, SyntaxError) and error.filename:
        location = project_path(error.filename, root) or error.filename
        return _syntax_problem(error, location)
    for frame in reversed(traceback.extract_tb(error.__traceback__)):
        inside = project_path(frame.filename, root)
        if inside:
            return Problem(f"{inside}:{frame.lineno}", type(error).__name__, str(error))
    return Problem("-", type(error).__name__, str(error))
