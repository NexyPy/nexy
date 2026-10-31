"""Forgetting the project's modules, so a dev restart imports the code as it is now."""

from __future__ import annotations

import contextlib
import sys
from collections.abc import Iterable
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
    targets = _project_targets(base)
    purged = [name for name, _ in targets]
    bytecode = [location for _, module in targets for location in _module_locations(module)]
    for name in purged:
        del sys.modules[name]
    drop_bytecode(bytecode)
    forget_actions(purged)
    forget_orm_tables()
    return purged


def _project_targets(base: str) -> list[tuple[str, Any]]:
    """The project modules to forget, with their objects: decisions need the parent alive."""
    return [
        (name, module)
        for name, module in list(sys.modules.items())
        if not (name == "nexy" or name.startswith(("nexy.", "__nexy__")))
        and _is_project_module(module, base)
    ]


def drop_bytecode(locations: Iterable[str]) -> None:
    """Delete the cached bytecode of the purged sources.

    A ``.pyc`` header records its source with one-second granularity: a file saved twice
    within the same second with the same size would be re-imported from the stale cache,
    and the restart would serve the previous code.
    """
    from importlib.util import cache_from_source

    for location in locations:
        if not Path(location).is_file():
            continue  # a namespace package folder holds no bytecode
        # an unwritable cache only ever costs a recompile
        with contextlib.suppress(OSError):
            Path(cache_from_source(location)).unlink(missing_ok=True)


def forget_actions(removed: list[str]) -> None:
    """Forget the actions the removed modules defined.

    ``ACTIONS_STORE`` lives in the framework, so dropping the modules is not enough:
    an action that no longer exists would keep its endpoint and its line in
    ``actions.ts`` for the whole dev session. Actions of modules that were kept
    (none, or outside the project) stay registered.
    """
    if not removed:
        return
    from nexy.modules.routers.actions.store import ACTIONS_STORE

    dropped = set(removed)
    stale = {
        func_id
        for func_id in (*ACTIONS_STORE.registry, *ACTIONS_STORE.path_map)
        if func_id.rsplit(".", 1)[0] in dropped
    }
    for func_id in stale:
        ACTIONS_STORE.registry.pop(func_id, None)
        ACTIONS_STORE.path_map.pop(func_id, None)


def forget_orm_tables() -> None:
    """Empty the table registry SQLModel shares between all models.

    The project's model modules are dropped from ``sys.modules``, but SQLModel lives in the
    environment and keeps every table it saw. Importing ``class User(SQLModel, table=True)`` a
    second time would then fail with "Table 'user' is already defined for this MetaData instance",
    and so would every module that imports it. Nothing happens when the project does not use it.
    """
    sqlmodel = sys.modules.get("sqlmodel")
    if sqlmodel is None:
        return
    sqlmodel.SQLModel.metadata.clear()
    sqlmodel.SQLModel._sa_registry.dispose()


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
