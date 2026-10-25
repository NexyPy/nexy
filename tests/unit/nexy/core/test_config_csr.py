"""useCSR turns the route pipeline into a client-routing project.

The single source of truth is ``Config.ROUTE_FILE_EXTENSIONS``: route
discovery, the builder and the manifest all derive from it. These tests pin
that derivation so ``.nexy`` cannot leak back in through a special name.
"""

from nexy.core.config import Config

_REACT = """
from nexy.frontend import react
"""


class TestCsrRouteExtensions:
    def test_default_keeps_nexy_routes(self, nexy_project):
        nexy_project()
        assert ".nexy" in Config().ROUTE_FILE_EXTENSIONS

    def test_csr_drops_nexy_routes(self, nexy_project):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        assert ".nexy" not in Config().ROUTE_FILE_EXTENSIONS

    def test_csr_keeps_framework_routes(self, nexy_project):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        assert ".tsx" in Config().ROUTE_FILE_EXTENSIONS

    def test_csr_drops_nexy_from_build_targets(self, nexy_project):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        assert ".nexy" not in Config().TARGET_EXTENSIONS


class TestCsrSpecialNames:
    def test_default_layout_names_include_nexy(self, nexy_project):
        nexy_project()
        assert "layout.nexy" in Config().LAYOUT_FILE_NAMES

    def test_csr_drops_layout_nexy(self, nexy_project):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        assert "layout.nexy" not in Config().LAYOUT_FILE_NAMES

    def test_csr_drops_errors_and_loading_nexy(self, nexy_project):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        assert "errors.nexy" not in Config().ERROR_FILE_NAMES
        assert "loading.nexy" not in Config().LOADING_FILE_NAMES


class TestCsrWatch:
    def test_csr_stops_watching_nexy(self, nexy_project):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        assert not any(".nexy" in pattern for pattern in Config().WATCH_EXTENSIONS_GLOB)

    def test_csr_keeps_watching_python(self, nexy_project):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        assert any(".py" in pattern for pattern in Config().WATCH_EXTENSIONS_GLOB)


class TestCsrValidation:
    def test_csr_without_framework_is_rejected(self, nexy_project):
        nexy_project("useCSR = True")
        Config()
        assert "useCSR requires a client framework" in (Config.get_load_error() or "")

    def test_csr_with_framework_loads_clean(self, nexy_project):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        Config()
        assert Config.get_load_error() is None

    def test_csr_with_modular_router_is_rejected(self, nexy_project):
        nexy_project(
            "useCSR = True\nuseFF = react()\nuseRouter = object()",
            imports=_REACT,
        )
        Config()
        assert "file-based routing" in (Config.get_load_error() or "")

    def test_require_valid_raises_on_csr_without_framework(self, nexy_project):
        nexy_project("useCSR = True")
        Config()
        try:
            Config.require_valid()
        except ValueError as exc:
            assert "useCSR requires a client framework" in str(exc)
        else:
            raise AssertionError("require_valid accepted an impossible configuration")

    def test_require_valid_ignores_missing_config_file(self, nexy_project):
        nexy_project()
        Config()
        Config.require_valid()
