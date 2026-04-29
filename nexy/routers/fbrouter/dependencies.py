import importlib
from pathlib import Path
from typing import Any, Callable, List
from nexy.core.config import Config

class RouteDependencies:
    @staticmethod
    def collect(source_path: str) -> List[Callable[..., Any]]:
        """Collects 'dependencies' list from dependencies.py files in the directory tree."""
        deps: List[Callable[..., Any]] = []
        try:
            path = Path(source_path)
            root = Path(Config.ROUTER_PATH).resolve()
            current = path.parent.resolve()

            chain: List[Path] = []
            while str(current).startswith(str(root)):
                chain.append(current)
                if current == root:
                    break
                current = current.parent

            for directory in reversed(chain):
                dep_file = directory / "dependencies.py"
                if dep_file.is_file():
                    rel = directory.as_posix().replace("/", ".")
                    module_path = f"{rel}.dependencies"
                    try:
                        mod = importlib.import_module(module_path)
                        candidates = getattr(mod, "dependencies", None)
                        if isinstance(candidates, (list, tuple)):
                            deps.extend([c for c in candidates if callable(c)])
                    except Exception:
                        continue
        except Exception:
            return deps
        return deps