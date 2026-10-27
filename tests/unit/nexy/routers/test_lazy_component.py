import sys

from nexy.helpers.fs.vfs import VFS
from nexy.modules.routers.fbrouter.handlers import lazy_component
from nexy.modules.runtime.importer import install_vfs_importer


def _clean():
    VFS().clear()
    install_vfs_importer()


def test_lazy_component_returns_original_first():
    _clean()
    VFS().write("__nexy__/src/routes/hello.py", "def Hello(): return 'old'")
    VFS().write("__nexy__/src/routes/__init__.py", "")
    VFS().write("__nexy__/src/__init__.py", "")
    VFS().write("__nexy__/__init__.py", "")

    sys.modules.pop("__nexy__.src.routes.hello", None)
    sys.modules.pop("__nexy__.src.routes", None)
    sys.modules.pop("__nexy__.src", None)

    import __nexy__.src.routes.hello as mod

    lazy = lazy_component("__nexy__.src.routes.hello", "Hello", mod.Hello)
    assert lazy() == "old"


def test_lazy_component_resolves_fresh_after_recompile():
    _clean()
    VFS().write("__nexy__/src/routes/hello.py", "def Hello(): return 'old'")
    VFS().write("__nexy__/src/routes/__init__.py", "")
    VFS().write("__nexy__/src/__init__.py", "")
    VFS().write("__nexy__/__init__.py", "")

    sys.modules.pop("__nexy__.src.routes.hello", None)
    sys.modules.pop("__nexy__.src.routes", None)
    sys.modules.pop("__nexy__.src", None)

    import __nexy__.src.routes.hello as mod

    lazy = lazy_component("__nexy__.src.routes.hello", "Hello", mod.Hello)
    assert lazy() == "old"

    VFS().write("__nexy__/src/routes/hello.py", "def Hello(): return 'new'")
    sys.modules.pop("__nexy__.src.routes.hello", None)

    assert lazy() == "new"
