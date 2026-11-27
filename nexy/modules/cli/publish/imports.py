"""Find relative imports a release would not be able to satisfy."""

from __future__ import annotations

import ast
from pathlib import Path


def undeclared_imports(root: Path, files: tuple[str, ...]) -> tuple[str, ...]:
    """Return the relative import targets missing from the declared files."""
    declared = set(files)
    missing: set[str] = set()
    for name in files:
        if not name.endswith(".py"):
            continue
        tree = _tree(root / name)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level:
                missing.update(_candidates(root, name, node, declared))
    return tuple(sorted(missing))


def _tree(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None


def _candidates(
    root: Path, source: str, node: ast.ImportFrom, declared: set[str]
) -> tuple[str, ...]:
    base = source.split("/")[:-1]
    parents = node.level - 1
    if parents > len(base):
        return ()
    base = base[: len(base) - parents] if parents else base
    names = node.module.split(".") if node.module else [alias.name for alias in node.names]
    return _all(root, base, names, declared)


def _all(root: Path, base: list[str], names: list[str], declared: set[str]) -> tuple[str, ...]:
    found: list[str] = []
    for name in names:
        if name != "*":
            found.extend(_missing(root, base, name, declared))
    return tuple(found)


def _missing(root: Path, base: list[str], name: str, declared: set[str]) -> tuple[str, ...]:
    parts = base + name.split(".")
    package = "/".join((*parts, "__init__.py"))
    module = "/".join(parts) + ".py"
    path = package if (root / package).is_file() else module
    return () if path in declared else (path,)
