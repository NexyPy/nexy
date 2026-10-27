"""The components a .nexy file imports: they are compiled first, so the import finds them."""

from __future__ import annotations

import pathlib
import re
from collections.abc import Callable, Iterator

from nexy.core.config import Config
from nexy.helpers.fs.vfs import VFS

_CODE_FENCE = re.compile(
    r"^(?:```|~~~)\S*[ \t]*\n.*?^(?:```|~~~)[ \t]*$",
    re.MULTILINE | re.DOTALL,
)
_IMPORT_FROM = re.compile(r'^\s*from\s+["\'](?P<path>[^"\']+)["\']\s+import', re.MULTILINE)
_ALIAS = re.compile(r"^[@~$]")
_NOT_COMPONENT_SOURCES = (".tsx", ".vue", ".svelte", ".md")


def resolve_dependency(current: str, import_path: str) -> str | None:
    """The project-relative path an import points at (an alias or a relative path), else None."""
    config = Config()
    root = pathlib.Path(config.PROJECT_ROOT).resolve()
    if _ALIAS.match(import_path):
        for alias, replacement in config.ALIASES.items():
            if import_path.startswith(alias):
                target = root / import_path.replace(alias, replacement, 1)
                return target.relative_to(root).as_posix()
    if import_path.startswith(("./", "../")):
        try:
            current_file = pathlib.Path(current).resolve()
            return (current_file.parent / import_path).resolve().relative_to(root).as_posix()
        except ValueError:
            return None
    return None


def _imported_components(path: str, source: str) -> Iterator[str]:
    """The .nexy files imported by *source*, ignoring examples inside code fences."""
    for found in _IMPORT_FROM.finditer(_CODE_FENCE.sub("\n", source)):
        dependency = resolve_dependency(path, found.group("path"))
        if dependency and dependency.endswith(".nexy"):
            yield dependency


def _compiled_module(dependency: str) -> str:
    """Where the compiled Python module of a .nexy dependency is written."""
    namespace = Config.NAMESPACE.strip("/")
    html = f"{namespace}/{dependency}".replace(".nexy", ".html")
    return str(pathlib.Path(html).with_suffix(".py"))


def compile_dependencies(
    path: str, compile_one: Callable[[str], None], seen: set[str] | None = None
) -> None:
    """Compile what *path* imports, depth first, each file once; *compile_one* compiles a file."""
    seen = set() if seen is None else seen
    resolved = str(pathlib.Path(path).resolve())
    if resolved in seen or path.endswith(_NOT_COMPONENT_SOURCES):
        return
    seen.add(resolved)
    try:
        source = pathlib.Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return
    vfs = VFS()
    for dependency in _imported_components(path, source):
        if not vfs.exists(_compiled_module(dependency)):
            compile_dependencies(dependency, compile_one, seen)
            compile_one(dependency)
