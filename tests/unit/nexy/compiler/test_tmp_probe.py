"""Probe: CSR project with layout.tsx + home.tsx -> what HTML comes out?"""
import importlib
from pathlib import Path

from nexy.helpers.fs.vfs import VFS
from nexy.modules.compiler.frontend_route import FrontendRouteCompiler
from nexy.modules.runtime.importer import install_vfs_importer

TSX = "export default function Home() { return null }\n"
LAYOUT = (
    "export default function Layout({ children }) { "
    "return <div className='chrome'>{children}</div>; }\n"
)


def test_probe(nexy_project, tmp_path: Path) -> None:
    from nexy.core.config import Config

    nexy_project("useCSR = True\nuseFF = react()", imports="from nexy.frontend import react")
    routes = tmp_path / "src" / "routes"
    routes.mkdir(parents=True, exist_ok=True)
    (routes / "layout.tsx").write_text(LAYOUT, encoding="utf-8")
    (routes / "home.tsx").write_text(TSX, encoding="utf-8")

    VFS().clear()
    install_vfs_importer()
    print("LAYOUT_FILE_NAMES:", Config().LAYOUT_FILE_NAMES)

    FrontendRouteCompiler().compile(input="src/routes/layout.tsx")
    FrontendRouteCompiler().compile(input="src/routes/home.tsx")

    print("=== layout.py ===")
    print(VFS().read("__nexy__/src/routes/layout.py"))
    print("=== layout.html ===")
    print(VFS().read("__nexy__/src/routes/layout.html"))
    print("=== home.py ===")
    print(VFS().read("__nexy__/src/routes/home.py"))

    mod = importlib.import_module("__nexy__.src.routes.home")
    html = mod.Home()
    print("=== Home() OUTPUT ===")
    print(html)
    assert False, "show output"
