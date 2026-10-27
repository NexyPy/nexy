import importlib.util

import nexy


def test_all_exports_resolve() -> None:
    assert [name for name in nexy.__all__ if not hasattr(nexy, name)] == []


def test_app_is_not_listed_in_all() -> None:
    # `from nexy import app` would hand over the module, and `import *` would build the server.
    assert "app" not in nexy.__all__


def test_the_deployment_entry_point_module_exists() -> None:
    # `nexy.app:app` is the uvicorn target of every generated project; finding the module does
    # not import it, which would build the AppServer singleton.
    assert importlib.util.find_spec("nexy.app") is not None
