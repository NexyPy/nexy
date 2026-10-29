"""Reads nexyconfig.py and derives the settings that follow from it onto `Config`."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from nexy.core import framework_rules as rules
from nexy.core.models import FrontendFramework, NexyConfigModel

MISSING_CONFIG_ERROR = "nexyconfig.py not found"
_SPECIAL_FILES = {
    "layout": ("LAYOUT_FILE_NAMES", "useLayoutExtensions"),
    "notfound": ("NOTFOUND_FILE_NAMES", "useNotFoundExtensions"),
    "errors": ("ERROR_FILE_NAMES", "useErrorsExtensions"),
    "loading": ("LOADING_FILE_NAMES", "useLoadingExtensions"),
    "forbidden": ("FORBIDDEN_FILE_NAMES", "useForbiddenExtensions"),
    "unauthorized": ("UNAUTHORIZED_FILE_NAMES", "useUnauthorizedExtensions"),
}
_ALWAYS_ROUTE_EXCEPTIONS = ("__init__.py", "dependencies.py", "middleware.py")


def _with(current: list[str], added: list[str]) -> list[str]:
    """A new list: *current* followed by what *added* has that it lacks, in order."""
    return list(dict.fromkeys([*current, *added]))


def import_nexyconfig() -> Any | None:
    """The user's nexyconfig module, or the example one, or None.

    Raises:
        ModuleNotFoundError: nexyconfig.py exists but imports a package this Python lacks. That is
            a problem to report, not a project without a config.
    """
    try:
        import nexyconfig

        return nexyconfig
    except ModuleNotFoundError as error:
        if error.name != "nexyconfig":
            raise
        return _import_example()


def _unloadable(error: ModuleNotFoundError) -> str:
    return (
        f"nexyconfig.py cannot be loaded: {error}. If it is a package, install it in this Python "
        f"({sys.executable}) or activate the project's virtual environment."
    )


def _import_example() -> Any | None:
    for candidate in ("nexyconfig.example.py", "nexyconfig.example"):
        path = Path(candidate)
        spec = (
            importlib.util.spec_from_file_location("nexyconfig", path) if path.is_file() else None
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    return None


class ConfigLoader:
    """Applies the user's `NexyConfig` to *target* (the `Config` class), one concern per step."""

    def __init__(self, target: Any) -> None:
        self.target = target
        self.user: Any = None

    def load(self) -> None:
        """Run every step; a bad configuration sets `target._load_error` and skips the rest."""
        try:
            module = import_nexyconfig()
        except ModuleNotFoundError as error:
            self.target._load_error = _unloadable(error)
            return
        if module is None:
            self.target._load_error = MISSING_CONFIG_ERROR
            return
        if not self._find_user_class(module):
            return
        self._take_user_values()
        if not self._valid():
            return
        self._derive_text_options()
        registry = self._derive_frameworks()
        self._derive_special_names(registry)
        self._derive_watching()
        self.target._load_error = None

    def _find_user_class(self, module: Any) -> bool:
        try:
            self.user = module.NexyConfig
        except AttributeError as error:
            self.target._load_error = f"nexyconfig.py missing NexyConfig class: {error}"
            return False
        return True

    def _take_user_values(self) -> None:
        for attribute in NexyConfigModel.__annotations__:
            value = getattr(self.user, attribute, None)
            if value is not None:
                setattr(self.target, attribute, value)

    def _valid(self) -> bool:
        t = self.target
        try:
            rules.require_one_framework(t.useFF)
            rules.require_csr_prerequisites(t.useCSR, t.useFF, t.useRouter)
        except ValueError as error:
            t._load_error = str(error)
            return False
        return True

    def _derive_text_options(self) -> None:
        t = self.target
        if t.useAliases:
            t.ALIASES = dict(t.useAliases)
        if t.useMarkdownExtensions:
            t.MARKDOWN_EXTENSIONS = list(t.useMarkdownExtensions)
        if t.useTocDepth:
            t.TOC_DEPTH = t.useTocDepth
        if t.useTocTitle:
            t.TOC_TITLE = t.useTocTitle
        if hasattr(self.user, "useTocAuto") and t.useTocAuto is not None:
            t.TOC_AUTO = t.useTocAuto

    def _derive_frameworks(self) -> dict[str, FrontendFramework]:
        """Route extensions, the extension-to-framework map and the watched extensions."""
        t = self.target
        frameworks = rules.as_list(t.useFF)
        t.ROUTE_FILE_EXTENSIONS = rules.route_extensions(
            frameworks[0] if frameworks else None, t.useCSR
        )
        registry = {framework.name.lower(): framework for framework in frameworks}
        t.FRONTEND_EXTENSIONS = rules.extension_map(t.FRONTEND_EXTENSIONS, frameworks)
        t.FRAMEWORK_REGISTRY = registry
        self._add_framework_extensions(frameworks)
        t.TARGET_EXTENSIONS = [ext for ext in t.ROUTE_FILE_EXTENSIONS if ext != ".py"]
        if t.useCSR:
            # Client routing owns the views: .nexy is not a source file any more, and no
            # layout.nexy exists. Watching .nexy would only trigger pointless rebuilds.
            t.WATCH_EXTENSIONS = [ext for ext in t.WATCH_EXTENSIONS if ext != ".nexy"]
        return registry

    def _add_framework_extensions(self, frameworks: list[FrontendFramework]) -> None:
        # New lists, never an append: the defaults are shared by every load of the class.
        t = self.target
        added = [rules.dotted(ext) for framework in frameworks for ext in framework.extension or []]
        t.FRAMEWORK_ROUTE_EXTENSIONS = _with(t.FRAMEWORK_ROUTE_EXTENSIONS, added)
        t.WATCH_EXTENSIONS = _with(t.WATCH_EXTENSIONS, added)

    def _derive_special_names(self, registry: dict[str, FrontendFramework]) -> None:
        t = self.target
        for prefix, (attribute, user_setting) in _SPECIAL_FILES.items():
            names = rules.special_names(
                prefix,
                registry,
                user_exts=getattr(self.user, user_setting, None),
                include_nexy=not t.useCSR,
            )
            setattr(t, attribute, names)
        t.ROUTE_FILE_EXCEPTIONS = list(
            dict.fromkeys([*_ALWAYS_ROUTE_EXCEPTIONS, *t.LAYOUT_FILE_NAMES])
        )

    def _derive_watching(self) -> None:
        t = self.target
        watched = getattr(self.user, "useWatchExtensions", None)
        if watched:
            t.WATCH_EXTENSIONS_GLOB = [watched] if isinstance(watched, str) else list(watched)
        else:
            t.WATCH_EXTENSIONS_GLOB = [f"*{ext}" for ext in t.WATCH_EXTENSIONS]
        excluded = getattr(self.user, "useWatchExcludePatterns", None)
        if excluded:
            t.WATCH_EXCLUDE_PATTERNS = list(excluded)
        patterns = [f"**/{directory}/**" for directory in t.excludeDirs or []]
        t.WATCH_EXCLUDE_PATTERNS = _with(t.WATCH_EXCLUDE_PATTERNS, patterns)
