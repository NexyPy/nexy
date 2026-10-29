"""``middleware.py`` files: HTTP middleware scoped to a routes directory.

A ``middleware.py`` exports ``async def middleware(request, call_next)``, the signature of
Starlette's ``@app.middleware("http")``. It wraps every request whose URL is under the directory's
URL, and the files stack from the routes root down, outermost first, like layouts and
``dependencies.py``.

A file applies to the routes whose source file is in its directory, groups included - the rule
layouts follow. A request whose URL matches no route has no source directory, so it falls back to
the URL prefix of the directories that are not route groups (a group has no URL of its own):
``[slug]`` matches one segment and ``[...rest]`` matches the remainder.
"""

from __future__ import annotations

import importlib.util
import inspect
import re
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import compile_path
from starlette.types import ASGIApp, Receive, Scope, Send

Routes = Callable[[], Iterable[tuple[str, tuple[str, ...]]]]
Dispatch = Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]

FILE_NAME = "middleware.py"
FUNCTION_NAME = "middleware"
# A middleware guards routes, not Vite or the HMR socket: these URLs are never wrapped.
_FRAMEWORK_PREFIXES = (
    "/__nexy__/",
    "/_nexy/",
    "/node_modules/",
    "/@vite/",
    "/@id/",
    "/@fs/",
    "/@react-refresh",
)
# Static files live here, but a page can too (`routes/assets/index.nexy`): a page that matches
# the URL keeps its guard. A catch-all page does not count, or it would guard every asset.
_STATIC_PREFIXES = ("/public/", "/assets/")


class MiddlewareFileError(Exception):
    """A ``middleware.py`` that cannot be used."""


@dataclass(frozen=True)
class Entry:
    directory: tuple[str, ...]
    pattern: re.Pattern[str]
    dispatch: Dispatch


def _is_group(part: str) -> bool:
    return part.startswith("(") and part.endswith(")")


def url_pattern(parts: tuple[str, ...]) -> re.Pattern[str]:
    """Regex for the URL prefix of a routes directory given as path parts."""
    segments: list[str] = []
    for part in parts:
        if _is_group(part):
            continue
        if part.startswith("[[...") and part.endswith("]]"):
            segments.append(".*")
        elif part.startswith("[...") and part.endswith("]"):
            segments.append(".+")
        elif part.startswith("[") and part.endswith("]"):
            segments.append("[^/]+")
        else:
            segments.append(re.escape(part))
    prefix = "".join(f"/{segment}" for segment in segments)
    return re.compile(rf"^{prefix}(?:/|$)" if prefix else r"^/")


def _load(path: Path, routes_root: Path) -> Dispatch:
    relative = path.relative_to(routes_root).as_posix()
    spec = importlib.util.spec_from_file_location(f"_nexy_middleware_{abs(hash(relative))}", path)
    if spec is None or spec.loader is None:
        raise MiddlewareFileError(f"{relative}: cannot be imported")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    function: Any = getattr(module, FUNCTION_NAME, None)
    if function is None or not callable(function):
        raise MiddlewareFileError(
            f"{relative} must define `async def {FUNCTION_NAME}(request, call_next)`"
        )
    if not inspect.iscoroutinefunction(function):
        raise MiddlewareFileError(f"{relative}: `{FUNCTION_NAME}` must be async")
    return function  # type: ignore[no-any-return]


def discover(routes_root: Path) -> list[Entry]:
    """Every ``middleware.py`` under *routes_root*, shallowest directory first."""
    entries: list[Entry] = []
    for path in routes_root.rglob(FILE_NAME):
        relative = path.relative_to(routes_root).parent.parts
        if any(part.startswith(("_", ".")) for part in relative):
            continue
        entries.append(Entry(relative, url_pattern(relative), _load(path, routes_root)))
    return sorted(entries, key=lambda entry: (len(entry.directory), entry.directory))


class DirectoryMiddleware:
    """ASGI layer applying the matching ``middleware.py`` chain to each HTTP request."""

    def __init__(self, app: ASGIApp, entries: list[Entry], routes: Routes = lambda: ()) -> None:
        """*routes* yields ``(url template, source directory parts)`` for every file route."""
        self.app = app
        self.entries = entries
        self._routes = routes
        self._compiled: list[tuple[re.Pattern[str], tuple[str, ...], bool]] = []
        self._compiled_from = -1
        self._chains: dict[tuple[int, ...], ASGIApp] = {}

    def _source_directory(self, path: str) -> tuple[str, ...] | None:
        known = list(self._routes())
        if len(known) != self._compiled_from:
            self._compiled = [
                (compile_path(url)[0], directory, ":path}" in url) for url, directory in known
            ]
            self._compiled_from = len(known)
        for regex, directory, _catch_all in self._compiled:
            if regex.match(path):
                return directory
        return None

    def _is_page(self, path: str) -> bool:
        """True when a route that is not a catch-all serves *path*."""
        self._source_directory(path)
        return any(regex.match(path) for regex, _, catch_all in self._compiled if not catch_all)

    def _is_internal(self, path: str) -> bool:
        if path.startswith(_FRAMEWORK_PREFIXES):
            return True
        return path.startswith(_STATIC_PREFIXES) and not self._is_page(path)

    def _matching(self, path: str) -> tuple[int, ...]:
        directory = self._source_directory(path)
        if directory is not None:
            return tuple(
                i
                for i, e in enumerate(self.entries)
                if directory[: len(e.directory)] == e.directory
            )
        return tuple(
            i
            for i, e in enumerate(self.entries)
            if not any(_is_group(part) for part in e.directory) and e.pattern.match(path)
        )

    def _chain(self, matched: tuple[int, ...]) -> ASGIApp:
        chain = self._chains.get(matched)
        if chain is None:
            chain = self.app
            for index in reversed(matched):
                chain = BaseHTTPMiddleware(chain, dispatch=self.entries[index].dispatch)
            self._chains[matched] = chain
        return chain

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and not self._is_internal(scope["path"]):
            matched = self._matching(scope["path"])
            if matched:
                await self._chain(matched)(scope, receive, send)
                return
        await self.app(scope, receive, send)
