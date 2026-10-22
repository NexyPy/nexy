from nexy.modules.frontend.base import BaseFrontendGenerator


class _StubGenerator(BaseFrontendGenerator):
    def generate(self) -> None:  # abstract method implemented for tests
        pass


class TestFrontendBase:
    def test_get_ff_returns_none_by_default(self, nexy_project) -> None:
        nexy_project("")  # no useFF configured

        assert _StubGenerator()._get_ff() is None

    def test_get_frameworks_empty_without_ff(self, nexy_project) -> None:
        nexy_project("")

        assert _StubGenerator()._get_frameworks() == set()

    def test_get_ff_reads_single_framework(self, nexy_project) -> None:
        nexy_project(
            "useFF = FrontendFramework(name='react', render='static')",
            imports="from nexy.core.models import FrontendFramework",
        )

        ff = _StubGenerator()._get_ff()

        assert ff is not None and ff.name == "react"
        assert _StubGenerator()._get_frameworks() == {"react"}

    def test_get_ff_picks_first_of_list(self, nexy_project) -> None:
        nexy_project(
            "useFF = [FrontendFramework(name='react', render='static'),"
            " FrontendFramework(name='vue', render='static')]",
            imports="from nexy.core.models import FrontendFramework",
        )

        ff = _StubGenerator()._get_ff()

        assert ff is not None and ff.name == "react"


class TestRouterCompatibilityShim:
    def test_shim_reexports_fbrouter_instance(self, nexy_project, tmp_path) -> None:
        # Importing nexy.router eagerly instantiates the singleton, which
        # scans src/routes at import time (real behaviour of the shim).
        nexy_project("")
        (tmp_path / "src" / "routes").mkdir(parents=True)

        from nexy.modules.routers.fbrouter import FBRouter
        from nexy.router import FileBasedRouter, FileRouter

        assert isinstance(FileBasedRouter, FBRouter)
        assert FileRouter is FBRouter


class TestCoreTypes:
    def test_jsonresponse_is_plain_dict_alias(self) -> None:
        from nexy.core.types import JsonResponse

        value: JsonResponse = {"a": 1}

        assert isinstance(value, dict)


class TestScriptPlaceholder:
    def test_script_class_exists_without_behavior(self) -> None:
        from nexy.script import Script

        assert Script() is not None
