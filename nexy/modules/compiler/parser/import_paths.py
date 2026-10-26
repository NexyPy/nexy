"""Where an import in a .nexy file points: its path in the project, and its Python module name."""

from __future__ import annotations

import os
import pathlib
import re


def _is_alias(import_str: str, aliases: dict[str, str]) -> bool:
    return any(import_str.startswith(alias) for alias in aliases)


def _resolve_alias(import_str: str, aliases: dict[str, str], root: pathlib.Path) -> str:
    """The project-relative path of an import that starts with a configured alias."""
    alias, replacement = next(
        (alias, target) for alias, target in aliases.items() if import_str.startswith(alias)
    )
    resolved = root / import_str.replace(alias, replacement, 1)
    return resolved.absolute().relative_to(root).as_posix()


def _resolve_relative(current_file: str, import_str: str, root: pathlib.Path) -> str:
    """The path of a relative import, project-relative when it stays inside the project."""
    resolved = pathlib.Path(current_file).absolute().parent.joinpath(import_str).resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return os.path.normpath(resolved).replace("\\", "/")


def resolve_import(current_file: str, import_str: str, aliases: dict[str, str]) -> str:
    """The full relative path of an import, with aliases and relative paths resolved."""
    is_alias = _is_alias(import_str, aliases)
    if import_str[0] in ("@", "$", "~") and not is_alias:
        raise ImportError(f"Alias '{import_str.split('/')[0]}' not configured.")
    root = pathlib.Path.cwd().absolute()
    if is_alias:
        return _resolve_alias(import_str, aliases, root)
    if import_str.startswith(("./", "../")):
        return _resolve_relative(current_file, import_str, root)
    return import_str


def namespace_prefix(namespace: str, is_nexy: bool) -> str:
    """``__nexy__.`` for a compiled .nexy module, nothing for a Python one."""
    dotted = namespace.replace("\\", "/").replace("/", ".").strip(".")
    return f"{dotted}." if is_nexy and dotted else ""


def module_name(rel_path: str, namespace: str, is_nexy: bool) -> str:
    """The dotted module a ``.nexy`` or ``.py`` file is imported as."""
    base = re.sub(r"\.(nexy|py)$", "", rel_path)
    dotted = re.sub(r"\.+", ".", base.replace("\\", "/").replace("/", ".")).strip(".")
    return namespace_prefix(namespace, is_nexy) + dotted
