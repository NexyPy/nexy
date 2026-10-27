"""Forgetting the project's modules, so a dev restart imports the code as it is now."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


def purge_project_modules(root: Path | None = None) -> list[str]:
    """Drop project-local modules so the dev restart re-imports fresh code.

    Framework modules (``nexy`` / ``nexy.*``) and environment directories
    (``.venv``, ``site-packages``, ``node_modules``) are never dropped:
    re-importing them mid-run would leave already-imported modules holding a
    stale ``Config`` class.

    Args:
        root: Project root to purge from. Defaults to the current directory.

    Returns:
        The names removed from ``sys.modules``.
    """
    base = (root or Path.cwd()).resolve().as_posix()
    # Decide first, delete after: a namespace package computes its path from its parent, so the
    # parent must still be there when the package is looked at.
    purged = [
        name
        for name, module in list(sys.modules.items())
        if not (name == "nexy" or name.startswith(("nexy.", "__nexy__")))
        and _is_project_module(module, base)
    ]
    for name in purged:
        del sys.modules[name]
    return purged


def _module_locations(module: Any) -> list[str]:
    """Where a module lives: its file, or the folders of a namespace package (no ``__file__``).

    A folder without ``__init__.py`` (``src/routes``) is a namespace package. It must be purged
    with its regular parent (``src``): left alone, it keeps a dead reference to the parent and the
    next import of a route fails with ``KeyError: 'src'``.
    """
    module_file = getattr(module, "__file__", None)
    if module_file:
        return [str(module_file)]
    try:
        return [str(entry) for entry in getattr(module, "__path__", [])]
    except Exception:  # a namespace path that cannot be recomputed is not ours to keep
        return []


def _is_project_module(module: Any, base: str) -> bool:
    skip_markers = ("/.venv/", "/venv/", "/site-packages/", "/node_modules/")
    for location in _module_locations(module):
        posix = Path(location).resolve().as_posix()
        if not (posix.startswith(base + "/") or posix == base):
            continue
        if not any(marker in posix + "/" for marker in skip_markers):
            return True
    return False
