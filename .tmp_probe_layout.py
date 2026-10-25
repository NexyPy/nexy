"""Probe: CSR project with layout.tsx + home.tsx -> what HTML comes out?"""
import importlib
from pathlib import Path
import tempfile

from nexy.core.config import Config
from nexy.helpers.fs.vfs import VFS
from nexy.modules.compiler.frontend_route import FrontendRouteCompiler
from nexy.modules.runtime.importer import install_vfs_importer

TSX = "export default function Home() { return null }\n"
LAYOUT = "export default function Layout({ children }) { return <div className='chrome'>{children}</div>; }\n"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        cfg = root / "nexyconfig.py"
        cfg.write_text(
            "from nexy.frontend import react\n"
            "class NexyConfig:\n"
            "    useCSR = True\n"
            "    useFF = react()\n",
            encoding="utf-8",
        )
        import os
        os.chdir(tmp)

        Config._loaded = False  # type: ignore[attr-defined]
        try:
            del Config._loaded
        except AttributeError:
            pass
        # force reload
        Config.__init__(Config())  # may re-read nexyconfig

        routes = root / "src" / "routes"
        routes.mkdir(parents=True, exist_ok=True)
        (routes / "layout.tsx").write_text(LAYOUT, encoding="utf-8")
        (routes / "home.tsx").write_text(TSX, encoding="utf-8")

        VFS().clear()
        install_vfs_importer()
        print("LAYOUT_FILE_NAMES:", Config.LAYOUT_FILE_NAMES)

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


if __name__ == "__main__":
    main()
