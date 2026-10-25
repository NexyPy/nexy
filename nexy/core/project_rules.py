"""Consistency between ``useCSR`` and the files under ``src/routes/``.

A Nexy project is in one of two modes, like a Next.js project is either server-rendered pages or a
client app:

* ``useCSR = False``: pages are ``.nexy``, ``.md`` or ``.mdx`` and the root ``layout.nexy`` owns the
  HTML document. Client components (React, Vue...) are allowed as islands imported by those pages,
  but they are never routes.
* ``useCSR = True``: pages are the client framework's own files and the root ``layout.<ext>`` owns
  the document. No ``.nexy`` view exists. ``.py`` files are API routes in both modes.

Mixing the two is rejected before the server starts, with the list of offending files.
"""

from __future__ import annotations

from pathlib import Path

from nexy.core.config import Config

_CLIENT_ROUTE_SUFFIXES = (".tsx", ".jsx", ".vue", ".svelte")
_LIST_LIMIT = 5


def _route_files(routes: Path) -> list[Path]:
    """Every file under *routes* that is not hidden by a leading ``_`` or ``.``."""
    found: list[Path] = []
    for path in sorted(routes.rglob("*")):
        relative = path.relative_to(routes).parts
        if path.is_file() and not any(part.startswith(("_", ".")) for part in relative):
            found.append(path)
    return found


def _names(routes: Path, files: list[Path]) -> str:
    shown = [file.relative_to(routes).as_posix() for file in files[:_LIST_LIMIT]]
    more = len(files) - len(shown)
    return ", ".join(shown) + (f" and {more} more" if more > 0 else "")


def project_problems(root: Path | None = None) -> list[str]:
    """Human-readable problems, empty when the project respects its mode."""
    Config()
    routes = (root or Path.cwd()) / Config.ROUTER_PATH
    if not routes.is_dir():
        return []

    files = _route_files(routes)
    if Config.useCSR:
        views = [file for file in files if file.suffix == ".nexy"]
        if views:
            return [
                "useCSR = True means client routes only, but these .nexy files are in "
                f"{Config.ROUTER_PATH}/: {_names(routes, views)}. Write them as framework "
                "components (the root layout.tsx owns the HTML document), or set useCSR = False."
            ]
        return []

    clients = [file for file in files if file.suffix in _CLIENT_ROUTE_SUFFIXES]
    if clients:
        return [
            "useCSR = False means server-rendered pages, but these client files are in "
            f"{Config.ROUTER_PATH}/: {_names(routes, clients)}. Move components to src/components/ "
            "and import them from a .nexy page, or set useCSR = True for client routes."
        ]
    return []
