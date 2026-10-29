"""Finds the route files of the project, compiles and imports them, and sorts out what each is."""

from __future__ import annotations

import importlib
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType

from nexy.core.config import Config
from nexy.core.string import Pathname, StringTransform
from nexy.helpers.common.console import console
from nexy.helpers.common.pycheck import describe, report
from nexy.modules.routers.fbrouter.discovery import RouteDiscovery
from nexy.modules.routers.fbrouter.error_pages import SpecialPage

# Route files that could not be compiled or imported by the last scan, as "path: reason".
# `nx start` refuses to serve a project that has any; `nx dev` keeps going and reports them.
LOAD_FAILURES: list[str] = []

_UI_ROUTE_EXTS = (".nexy", ".mdx", ".md", ".tsx", ".vue", ".svelte")
_FRAMEWORK_ROUTE_EXTS = (".tsx", ".vue", ".svelte", ".mdx")


@dataclass
class RouteModule:
    """An imported route file: where it is served and which function renders it."""

    module: ModuleType
    type: str
    pathname: str
    comp_name: str
    import_path: str
    source: str


@dataclass
class ScanResult:
    """What one scan found: the routes, and the special pages by kind."""

    routes: list[RouteModule] = field(default_factory=list)
    errors: list[SpecialPage] = field(default_factory=list)
    notfound: list[SpecialPage] = field(default_factory=list)
    loading: list[SpecialPage] = field(default_factory=list)
    forbidden: list[SpecialPage] = field(default_factory=list)
    unauthorized: list[SpecialPage] = field(default_factory=list)


def route_clean_path(path: str) -> str:
    """Strip the router prefix and the file extension.

    Only the extension is removed: dots inside a dynamic segment such as ``[...path]`` are part
    of the route path and must survive, so splitting on the first ``.`` is wrong.
    """
    relative = path.replace(f"{Config.NAMESPACE}src/routes", "").replace("src/routes", "")
    return relative.rsplit(".", 1)[0]


def describe_import_error(error: BaseException) -> str:
    """``Type: message`` plus the file and line that raised it (a bare ``'src'`` says nothing)."""
    text = f"{type(error).__name__}: {error}"
    frames = traceback.extract_tb(error.__traceback__)
    if not frames:
        return text
    return f"{text} ({Path(frames[-1].filename).name}:{frames[-1].lineno})"


def _first_function(module: ModuleType) -> str | None:
    """The first public function the module defines itself: a framework route's component."""
    for name in dir(module):
        value = getattr(module, name, None)
        if name.startswith("_") or value.__class__.__name__ != "function":
            continue
        if getattr(value, "__module__", "") == module.__name__:
            return name
    return None


def component_name(module: ModuleType, wanted: str, extension: str) -> str:
    """*wanted*, or for a framework route the function the file defines when it has no such name."""
    if getattr(module, wanted, None) is None and extension in _FRAMEWORK_ROUTE_EXTS:
        return _first_function(module) or wanted
    return wanted


def _is_special(name: str) -> bool:
    return (
        name in Config.NOTFOUND_FILE_NAMES
        or name in Config.ERROR_FILE_NAMES
        or name in Config.LOADING_FILE_NAMES
        or name in Config.FORBIDDEN_FILE_NAMES
        or name in Config.UNAUTHORIZED_FILE_NAMES
    )


class RouteScanner:
    """Turns the files RouteDiscovery finds into `RouteModule`s and special pages."""

    def __init__(self, discovery: RouteDiscovery) -> None:
        self._discovery = discovery
        self._names = StringTransform()

    def scan(self) -> ScanResult:
        LOAD_FAILURES.clear()
        result = ScanResult()
        for path in self._discovery.scan():
            self._take(path, result)
        return result

    def _take(self, path: Path, result: ScanResult) -> None:
        located = self._locate(path)
        if located is None:
            return
        kind, import_path = located
        module = self._import(path, import_path)
        if module is None:
            return
        if _is_special(path.name.lower()):
            self._add_special(path, module, result)
        else:
            result.routes.append(self._route(path, module, kind, import_path))

    def _locate(self, path: Path) -> tuple[str, str] | None:
        """(kind, import path) of a route file, compiling it first when it is a page."""
        text = path.as_posix()
        if not text.endswith(_UI_ROUTE_EXTS):
            return "api", text.replace("/", ".").removesuffix(".py")
        mapped = self._names.normalize_route_path_for_namespace(text)
        import_path = f"{Config.NAMESPACE}{mapped}".replace("/", ".").rsplit(".", 1)[0]
        return ("component", import_path) if self._compile(path) else None

    @staticmethod
    def _compile(path: Path) -> bool:
        try:
            from nexy.modules.compiler import Compiler

            Compiler().compile(input=str(path))
        except Exception as error:
            console.print(f"  [red]ERROR[/red] {path.name} ({path}): compile failed - {error}")
            LOAD_FAILURES.append(f"{path}: compile failed - {error}")
            return False
        return True

    @staticmethod
    def _import(path: Path, import_path: str) -> ModuleType | None:
        try:
            return importlib.import_module(import_path)
        except Exception as error:
            report(describe(error))
            LOAD_FAILURES.append(f"{path}: {describe_import_error(error)}")
            return None

    def _add_special(self, path: Path, module: ModuleType, result: ScanResult) -> None:
        name = path.name.lower()
        scope = Pathname(path.parent.as_posix().replace("src/routes", "") or "/").process()
        page = SpecialPage(scope, module, self._names.get_component_name(name.split(".")[0]))
        if name in Config.ERROR_FILE_NAMES:
            result.errors.append(page)
        elif name in Config.NOTFOUND_FILE_NAMES:
            result.notfound.append(page)
        elif name in Config.FORBIDDEN_FILE_NAMES:
            result.forbidden.append(page)
        elif name in Config.UNAUTHORIZED_FILE_NAMES:
            result.unauthorized.append(page)
        else:
            result.loading.append(page)

    def _route(self, path: Path, module: ModuleType, kind: str, import_path: str) -> RouteModule:
        clean = route_clean_path(path.as_posix())
        stem = clean.split("/")[-1] if clean else ""
        wanted = self._names.get_component_name(stem)
        comp = component_name(module, wanted, path.suffix.lower())
        return RouteModule(
            module, kind, Pathname(clean).process(), comp, import_path, path.as_posix()
        )
