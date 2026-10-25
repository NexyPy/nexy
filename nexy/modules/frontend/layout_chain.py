"""Nested framework layouts: the chain of ``layout.*`` files above a page.

A framework page is mounted as one island. Its ancestor layouts of the same framework family are
composed around it on the client, outermost first, like Next.js nested layouts. The document itself
(``<!DOCTYPE html>``, ``<head>``, ``<body>``) stays in the server ``layout.nexy``.
"""

import hashlib
from pathlib import Path

# Page extension -> extensions a layout of the same family may use.
_FAMILY: dict[str, tuple[str, ...]] = {
    ".tsx": (".tsx", ".jsx"),
    ".jsx": (".tsx", ".jsx"),
    ".vue": (".vue",),
    ".svelte": (".svelte",),
}
_LAYOUT_NAMES: frozenset[str] = frozenset(
    f"layout{ext}" for exts in _FAMILY.values() for ext in exts
)


def layout_key(route_file: str) -> str:
    """The md5 key the client uses to import a route file (same as ``data-nexy-key``)."""
    return hashlib.md5(route_file.encode("utf-8"), usedforsecurity=False).hexdigest()


def framework_layout_chain(page: Path, routes_root: Path) -> list[str]:
    """Route-file paths (``/src/routes/.../layout.vue``) wrapping *page*, outermost first.

    Returns an empty list for pages without a framework family, for layout files themselves, and
    for files outside *routes_root*.
    """
    extensions = _FAMILY.get(page.suffix.lower())
    if extensions is None or page.name.lower() in _LAYOUT_NAMES:
        return []
    try:
        rel_dir = page.resolve().parent.relative_to(routes_root.resolve())
    except ValueError:
        return []

    chain: list[str] = []
    current = routes_root
    for part in ("", *rel_dir.parts):
        current = current / part if part else current
        for ext in extensions:
            candidate = current / f"layout{ext}"
            if candidate.is_file():
                rel = candidate.resolve().relative_to(routes_root.resolve()).as_posix()
                chain.append(f"/{routes_root.as_posix().strip('/')}/{rel}")
                break
    return chain
