"""Client routing gets a document shell when the project has no layout.

A framework route with no ``layout.*`` compiles to a bare ``<ncc>`` fragment.
That is the right output for a ``.nexy``-hosted page, but with ``useCSR`` the
route *is* the page and the browser needs a full document with the Vite tags.
"""

import importlib
from pathlib import Path

from nexy.core.config import Config
from nexy.helpers.fs.vfs import VFS
from nexy.modules.compiler.frontend_route import FrontendRouteCompiler
from nexy.modules.compiler.markdown_route import MarkdownRouteCompiler
from nexy.modules.runtime.importer import install_vfs_importer

_REACT = """
from nexy.frontend import react
"""

_TSX = "export default function Page() { return null }\n"


def _compile_tsx(tmp_path: Path, rel_file: str = "src/routes/home.tsx") -> None:
    src = tmp_path / rel_file
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(_TSX, encoding="utf-8")
    VFS().clear()
    FrontendRouteCompiler().compile(input=rel_file)


class TestShellInGeneratedSource:
    def test_default_project_has_no_shell(self, nexy_project, tmp_path):
        nexy_project()
        _compile_tsx(tmp_path)
        assert "__nexy_shell" not in VFS().read("__nexy__/src/routes/home.py")

    def test_csr_project_has_shell(self, nexy_project, tmp_path):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        _compile_tsx(tmp_path)
        assert "def __nexy_shell(children: str) -> str:" in VFS().read(
            "__nexy__/src/routes/home.py"
        )

    def test_csr_generated_module_is_valid_python(self, nexy_project, tmp_path):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        _compile_tsx(tmp_path)
        compile(VFS().read("__nexy__/src/routes/home.py"), "home.py", "exec")


class TestShellRuntime:
    def test_csr_page_renders_a_document(self, nexy_project, tmp_path, monkeypatch):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        monkeypatch.chdir(tmp_path)
        install_vfs_importer()
        _compile_tsx(tmp_path)
        module = importlib.import_module("__nexy__.src.routes.home")
        html = module.Home()
        assert html.startswith("<!DOCTYPE html>")
        assert "<body>" in html and "</body></html>" in html

    def test_csr_page_keeps_the_hydration_container(self, nexy_project, tmp_path, monkeypatch):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        monkeypatch.chdir(tmp_path)
        install_vfs_importer()
        _compile_tsx(tmp_path)
        module = importlib.import_module("__nexy__.src.routes.home")
        assert "<ncc" in module.Home()


class TestShellEscapeHatch:
    def test_user_layout_wins_over_the_shell(self, nexy_project, tmp_path, monkeypatch):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        monkeypatch.chdir(tmp_path)
        layout = tmp_path / "src" / "routes" / "layout.tsx"
        layout.parent.mkdir(parents=True, exist_ok=True)
        layout.write_text("export default function Layout() { return null }\n", encoding="utf-8")
        install_vfs_importer()
        _compile_tsx(tmp_path)
        source = VFS().read("__nexy__/src/routes/home.py")
        assert "__nexy_shell" not in source
        assert "import Layout as __Layout" in source

    def test_layout_file_name_is_framework_owned_in_csr(self, nexy_project):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        assert "layout.tsx" in Config().LAYOUT_FILE_NAMES


class TestShellMarkdown:
    def test_csr_markdown_page_renders_a_document(self, nexy_project, tmp_path, monkeypatch):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        monkeypatch.chdir(tmp_path)
        md = tmp_path / "src" / "routes" / "docs.md"
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text("# Docs\n", encoding="utf-8")
        VFS().clear()
        MarkdownRouteCompiler().compile(input="src/routes/docs.md")
        source = VFS().read("__nexy__/src/routes/docs.py")
        assert "def __nexy_shell(children: str) -> str:" in source
        compile(source, "docs.py", "exec")
