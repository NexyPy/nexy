"""The steps that turn a user's NexyConfig into the settings the rest of Nexy reads."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from nexy.core.config_loader import ConfigLoader
from nexy.core.models import FrontendFramework

REACT = FrontendFramework(name="react", render="", extension=["jsx", "tsx"])


def _target(**changes):
    base = {
        "useFF": None,
        "useCSR": False,
        "useRouter": None,
        "useAliases": None,
        "useMarkdownExtensions": [],
        "useTocDepth": "2-6",
        "useTocTitle": "Contents",
        "useTocAuto": True,
        "excludeDirs": ["docs"],
        "ALIASES": {},
        "MARKDOWN_EXTENSIONS": ["extra"],
        "TOC_DEPTH": "",
        "TOC_TITLE": "",
        "TOC_AUTO": True,
        "ROUTE_FILE_EXTENSIONS": [],
        "TARGET_EXTENSIONS": [],
        "FRONTEND_EXTENSIONS": {".json": "json"},
        "FRAMEWORK_REGISTRY": {},
        "FRAMEWORK_ROUTE_EXTENSIONS": [".vue"],
        "WATCH_EXTENSIONS": [".nexy", ".py"],
        "WATCH_EXTENSIONS_GLOB": [],
        "WATCH_EXCLUDE_PATTERNS": ["**/.git/**"],
        "LAYOUT_FILE_NAMES": [],
        "ROUTE_FILE_EXCEPTIONS": [],
        "_load_error": "unset",
    }
    return SimpleNamespace(**{**base, **changes})


def _loader(target, **user):
    loader = ConfigLoader(target)
    loader.user = SimpleNamespace(**user)
    return loader


class TestFrameworks:
    def test_the_framework_adds_its_extensions_to_the_routes(self):
        target = _target(useFF=REACT)
        _loader(target)._derive_frameworks()
        assert target.ROUTE_FILE_EXTENSIONS == [".nexy", ".md", ".mdx", ".py", ".jsx", ".tsx"]

    def test_the_registry_is_keyed_by_lowercase_name(self):
        target = _target(useFF=REACT)
        registry = _loader(target)._derive_frameworks()
        assert list(registry) == ["react"]

    def test_the_extension_map_points_each_extension_at_its_framework(self):
        target = _target(useFF=REACT)
        _loader(target)._derive_frameworks()
        assert target.FRONTEND_EXTENSIONS[".tsx"] == "react"

    def test_python_is_never_a_compile_target(self):
        target = _target(useFF=REACT)
        _loader(target)._derive_frameworks()
        assert ".py" not in target.TARGET_EXTENSIONS

    def test_client_routing_stops_watching_nexy_files(self):
        target = _target(useFF=REACT, useCSR=True)
        _loader(target)._derive_frameworks()
        assert ".nexy" not in target.WATCH_EXTENSIONS


class TestSpecialNames:
    def test_a_server_project_has_nexy_layouts_and_framework_ones(self):
        target = _target()
        _loader(target)._derive_special_names({"react": REACT})
        assert target.LAYOUT_FILE_NAMES == ["layout.nexy", "layout.jsx", "layout.tsx"]

    def test_a_client_project_has_no_nexy_layout(self):
        target = _target(useCSR=True)
        _loader(target)._derive_special_names({"react": REACT})
        assert "layout.nexy" not in target.LAYOUT_FILE_NAMES

    def test_a_layout_is_never_a_route(self):
        target = _target()
        _loader(target)._derive_special_names({})
        assert "layout.nexy" in target.ROUTE_FILE_EXCEPTIONS


class TestWatching:
    def test_each_watched_extension_becomes_a_glob(self):
        target = _target()
        _loader(target)._derive_watching()
        assert target.WATCH_EXTENSIONS_GLOB == ["*.nexy", "*.py"]

    def test_the_user_can_replace_the_globs(self):
        target = _target()
        _loader(target, useWatchExtensions="*.py")._derive_watching()
        assert target.WATCH_EXTENSIONS_GLOB == ["*.py"]

    def test_an_excluded_directory_becomes_a_pattern_once(self):
        target = _target()
        loader = _loader(target)
        loader._derive_watching()
        loader._derive_watching()
        assert target.WATCH_EXCLUDE_PATTERNS.count("**/docs/**") == 1


class TestValidation:
    def test_client_routing_without_a_framework_is_an_error(self):
        target = _target(useCSR=True)
        assert _loader(target)._valid() is False
        assert "useCSR requires a client framework" in target._load_error

    def test_a_valid_configuration_passes(self):
        assert _loader(_target(useFF=REACT, useCSR=True))._valid() is True


@pytest.mark.parametrize("missing", [object()])
def test_a_module_without_the_class_is_an_error(missing):
    target = _target()
    assert ConfigLoader(target)._find_user_class(missing) is False
    assert "missing NexyConfig class" in target._load_error


class TestSharedDefaultsAreNeverMutated:
    """A project's settings must not leak into the defaults every other load starts from."""

    def test_framework_extensions_leave_the_default_route_list_alone(self):
        target = _target(useFF=REACT)
        default = target.FRAMEWORK_ROUTE_EXTENSIONS
        _loader(target)._derive_frameworks()
        assert default == [".vue"]

    def test_framework_extensions_leave_the_default_watch_list_alone(self):
        target = _target(useFF=REACT)
        default = target.WATCH_EXTENSIONS
        _loader(target)._derive_frameworks()
        assert default == [".nexy", ".py"]

    def test_excluded_directories_leave_the_default_patterns_alone(self):
        target = _target()
        default = target.WATCH_EXCLUDE_PATTERNS
        _loader(target)._derive_watching()
        assert default == ["**/.git/**"]

    def test_user_aliases_are_copied(self):
        aliases = {"@": "src"}
        target = _target(useAliases=aliases)
        _loader(target)._derive_text_options()
        target.ALIASES["~"] = "lib"
        assert aliases == {"@": "src"}

    def test_user_markdown_extensions_are_copied(self):
        extensions = ["toc"]
        target = _target(useMarkdownExtensions=extensions)
        _loader(target)._derive_text_options()
        target.MARKDOWN_EXTENSIONS.append("extra")
        assert extensions == ["toc"]

    def test_user_exclude_patterns_are_copied(self):
        patterns = ["**/x/**"]
        target = _target()
        _loader(target, useWatchExcludePatterns=patterns)._derive_watching()
        assert patterns == ["**/x/**"]
