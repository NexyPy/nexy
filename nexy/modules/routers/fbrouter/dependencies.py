"""The `dependencies.py` files of a route's folders, outermost first."""

from __future__ import annotations

import importlib
from collections.abc import Callable
from pathlib import Path
from typing import Any

from nexy.core.config import Config
from nexy.helpers.fs.ancestors import walk_up


def _declared(dependencies_file: Path) -> list[Callable[..., Any]]:
    """The callables in the ``dependencies`` list of one file; none when it cannot be imported."""
    module_name = dependencies_file.relative_to(Path.cwd()).as_posix().replace(".py", "")
    try:
        module = importlib.import_module(module_name.replace("/", "."))
    except ImportError as error:
        # A route can live without a sibling dependencies module.
        print(error)
        return []
    candidates = getattr(module, "dependencies", None)
    return [c for c in candidates if callable(c)] if isinstance(candidates, (list, tuple)) else []


class RouteDependencies:
    @staticmethod
    def collect(source_path: str) -> list[Callable[..., Any]]:
        """Collects 'dependencies' lists from dependencies.py files following the directory
        hierarchy, exactly like layout.nexy inheritance.
        """
        collected: list[Callable[..., Any]] = []
        try:
            folder = Path(source_path).resolve().parent
            for directory in reversed(list(walk_up(folder, Path(Config.ROUTER_PATH)))):
                dependencies_file = directory / "dependencies.py"
                if dependencies_file.is_file():
                    collected += RouteDependencies._safely(dependencies_file)
        except (OSError, ValueError):
            pass
        return collected

    @staticmethod
    def _safely(dependencies_file: Path) -> list[Callable[..., Any]]:
        try:
            return _declared(dependencies_file)
        except (OSError, ValueError):
            return []
