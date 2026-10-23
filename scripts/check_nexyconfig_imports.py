"""Verify every shipped nexyconfig.py template/example imports successfully.

Guards the public `nexy.frontend` surface against drift: if a template uses an
import path that does not resolve, this fails. Run from the repo root:

    uv run python scripts/check_nexyconfig_imports.py
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEARCH_ROOTS = ("templates", "examples")
SKIP_DIRS = {".venv", "node_modules", "__nexy__", ".git"}


def find_configs() -> list[Path]:
    found: list[Path] = []
    for root_name in SEARCH_ROOTS:
        root = ROOT / root_name
        if not root.is_dir():
            continue
        for path in root.rglob("nexyconfig.py"):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            found.append(path)
    return sorted(found)


def stub_project_src() -> None:
    """Provide a placeholder ``src`` package for project-local imports.

    Modular templates import ``src.apps[.home].app_module``, which only exists
    inside a scaffolded project. Registering those modules lets each config
    execute fully, so its ``nexy.*`` imports are proven to resolve — which is
    what this check guards.
    """
    if "src" in sys.modules:
        return
    packages = ("src", "src.apps", "src.apps.home")
    app_modules = ("src.apps.app_module", "src.apps.home.app_module")
    for name in packages:
        module = types.ModuleType(name)
        module.__path__ = []
        sys.modules[name] = module
    for name in app_modules:
        module = types.ModuleType(name)
        module.AppModule = type("AppModule", (), {})
        sys.modules[name] = module


def load(path: Path) -> None:
    name = f"_nexycfg_{abs(hash(path))}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def main() -> int:
    configs = find_configs()
    if not configs:
        print("no nexyconfig.py found under", SEARCH_ROOTS)
        return 1

    failures: list[tuple[Path, str]] = []
    for path in configs:
        stub_project_src()
        try:
            load(path)
        except Exception as exc:  # noqa: BLE001 - report every failure kind
            failures.append((path, f"{type(exc).__name__}: {exc}"))

    for path in configs:
        rel = path.relative_to(ROOT)
        error = next((e for p, e in failures if p == path), None)
        print(f"{'FAIL' if error else ' ok '} {rel}{' - ' + error if error else ''}")

    print(f"\n{len(configs) - len(failures)}/{len(configs)} ok")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
