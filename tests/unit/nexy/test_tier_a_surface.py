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
