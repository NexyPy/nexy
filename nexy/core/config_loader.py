"""Reads nexyconfig.py and derives the settings that follow from it onto `Config`."""

from __future__ import annotations

import importlib.util
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
}
_ALWAYS_ROUTE_EXCEPTIONS = ("__init__.py", "dependencies.py", "middleware.py")


def import_nexyconfig() -> Any | None:
    """The user's nexyconfig module, or the example one, or None."""
    try:
        import nexyconfig

        return nexyconfig
    except ModuleNotFoundError:
        return _import_example()


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
        module = import_nexyconfig()
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
            t.ALIASES = t.useAliases
        if t.useMarkdownExtensions:
            t.MARKDOWN_EXTENSIONS = t.useMarkdownExtensions
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
        t = self.target
        for framework in frameworks:
            for ext in map(rules.dotted, framework.extension or []):
                if ext not in t.FRAMEWORK_ROUTE_EXTENSIONS:
                    t.FRAMEWORK_ROUTE_EXTENSIONS.append(ext)
                if ext not in t.WATCH_EXTENSIONS:
                    t.WATCH_EXTENSIONS.append(ext)

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
            t.WATCH_EXCLUDE_PATTERNS = excluded
        for directory in t.excludeDirs or []:
            pattern = f"**/{directory}/**"
            if pattern not in t.WATCH_EXCLUDE_PATTERNS:
                t.WATCH_EXCLUDE_PATTERNS.append(pattern)
