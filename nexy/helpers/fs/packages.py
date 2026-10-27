"""Make every folder of the project's Python code a package.

A folder without ``__init__.py`` is a namespace package: it imports, but it cannot be reloaded
reliably when the dev server restarts. Nexy creates the missing files, so a route written in
``src/routes/users.py`` works the same in ``nx dev``, ``nx build`` and ``nx start``.
"""

from __future__ import annotations

import contextlib
import os
from pathlib import Path

_SKIPPED = {"__pycache__", "node_modules", "__nexy__"}
_PACKAGE_SUFFIXES = {".py", ".nexy"}


def _holds_code(files: list[str]) -> bool:
    return any(Path(name).suffix in _PACKAGE_SUFFIXES for name in files)


def ensure_packages(base: Path) -> list[Path]:
    """Create the missing ``__init__.py`` in `base` and in each folder under it with .py/.nexy.

    Returns the files it created. A missing `base` is not an error.
    """
    if not base.is_dir():
        return []
    created: list[Path] = []
    for folder, subfolders, files in os.walk(base):
        subfolders[:] = [d for d in subfolders if d not in _SKIPPED and not d.startswith(".")]
        path = Path(folder)
        if "__init__.py" in files or not (path == base or _holds_code(files)):
            continue
        init = path / "__init__.py"
        init.write_text("", encoding="utf-8")
        created.append(init)
    return created


def ensure_project_packages() -> None:
    """`ensure_packages` for the project's ``src/``; a read-only checkout is left as it is."""
    with contextlib.suppress(OSError):
        ensure_packages(Path("src"))
