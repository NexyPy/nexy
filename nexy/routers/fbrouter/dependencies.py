import importlib
from collections.abc import Callable
from pathlib import Path
from typing import Any

from nexy.core.config import Config


class RouteDependencies:
    @staticmethod
    def collect(source_path: str) -> list[Callable[..., Any]]:
        """
        Collects 'dependencies' list from dependencies.py files following
        the directory hierarchy, exactly like layout.nexy inheritance.
        """
        deps: list[Callable[..., Any]] = []
        try:
            path = Path(source_path).resolve()
            root = Path(Config.ROUTER_PATH).resolve()
            current = path.parent.resolve()

            chain: list[Path] = []
            limit_dir = root.parent

            while str(current).startswith(str(limit_dir)):
                chain.append(current)
                if current in (root, limit_dir):
                    break
                current = current.parent

            for directory in reversed(chain):
                dep_file = directory / "dependencies.py"

                if dep_file.is_file():
                    try:
                        rel_path = dep_file.relative_to(Path.cwd())
                        raw_path = rel_path.as_posix()

                        normalized_path = raw_path.replace(".py", "").replace("/", ".")

                        try:
                            mod = importlib.import_module(normalized_path)
                        except ImportError as e:
                            # A route can live without a sibling dependencies module.
                            print(e)
                        candidates = getattr(mod, "dependencies", None)
                        if isinstance(candidates, (list, tuple)):
                            deps.extend([c for c in candidates if callable(c)])

                    except (OSError, ValueError):
                        continue

        except (OSError, ValueError):
            return deps

        return deps
