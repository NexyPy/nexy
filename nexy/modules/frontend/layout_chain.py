"""Nested framework layouts: the chain of ``layout.tsx|jsx`` files above a page.

A JSX page is mounted as one island. Its ancestor layouts are composed around it
on the client, outermost first, like Next.js nested layouts. The document itself
(``<!DOCTYPE html>``, ``<head>``, ``<body>``) stays in the server ``layout.nexy``.
"""

import hashlib
from pathlib import Path

JSX_EXTS: tuple[str, ...] = (".tsx", ".jsx")
_LAYOUT_NAMES: tuple[str, ...] = tuple(f"layout{ext}" for ext in JSX_EXTS)


def layout_key(route_file: str) -> str:
    """The md5 key the client uses to import a route file (same as ``data-nexy-key``)."""
    return hashlib.md5(route_file.encode("utf-8"), usedforsecurity=False).hexdigest()


def framework_layout_chain(page: Path, routes_root: Path) -> list[str]:
    """Route-file paths (``/src/routes/.../layout.tsx``) wrapping *page*, outermost first.

    Returns an empty list for non-JSX pages, for layout files themselves, and
    for files outside *routes_root*.
    """
    if page.suffix.lower() not in JSX_EXTS or page.name.lower() in _LAYOUT_NAMES:
        return []
    try:
        rel_dir = page.resolve().parent.relative_to(routes_root.resolve())
    except ValueError:
        return []

    chain: list[str] = []
    current = routes_root
    for part in ("", *rel_dir.parts):
        current = current / part if part else current
        for name in _LAYOUT_NAMES:
            candidate = current / name
            if candidate.is_file():
                rel = candidate.resolve().relative_to(routes_root.resolve()).as_posix()
                chain.append(f"/{routes_root.as_posix().strip('/')}/{rel}")
                break
    return chain
