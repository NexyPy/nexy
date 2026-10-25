"""Client routing gets a document shell when the project has no layout.

A framework route with no ``layout.*`` compiles to a bare ``<ncc>`` fragment.
That is the right output for a ``.nexy``-hosted page, but with ``useCSR`` the
route *is* the page and the browser needs a full document with the Vite tags.
"""

import importlib
from pathlib import Path

import pytest

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
    def test_default_project_has_shell(self, nexy_project, tmp_path):
        nexy_project()
        _compile_tsx(tmp_path)
        assert "__nexy_shell" in VFS().read("__nexy__/src/routes/home.py")

    def test_shell_source_is_valid_python(self):
        from nexy.modules.compiler.document_shell import CSR_SHELL_HEADER

        compile(CSR_SHELL_HEADER, "shell.py", "exec")

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
    def test_root_layout_tsx_owns_the_document_instead_of_the_shell(
        self, nexy_project, tmp_path, monkeypatch
    ):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        monkeypatch.chdir(tmp_path)
        layout = tmp_path / "src" / "routes" / "layout.tsx"
        layout.parent.mkdir(parents=True, exist_ok=True)
        layout.write_text("export default function Layout() { return null }\n", encoding="utf-8")
        install_vfs_importer()
        _compile_tsx(tmp_path)
        source = VFS().read("__nexy__/src/routes/home.py")
        assert "__render_document" in source
        assert "__nexy_shell" not in source

    def test_solid_root_layout_owns_the_document_too(self, nexy_project, tmp_path, monkeypatch):
        nexy_project("useCSR = True\nuseFF = solid()", imports="from nexy.frontend import solid\n")
        monkeypatch.chdir(tmp_path)
        layout = tmp_path / "src" / "routes" / "layout.tsx"
        layout.parent.mkdir(parents=True, exist_ok=True)
        layout.write_text("export default function Layout() { return null }\n", encoding="utf-8")
        install_vfs_importer()
        _compile_tsx(tmp_path)
        source = VFS().read("__nexy__/src/routes/home.py")
        assert "__render_document" in source and "__nexy_shell" not in source

    @pytest.mark.parametrize(
        ("framework", "layout", "page", "body"),
        [
            ("preact", "layout.tsx", "home.tsx", "export default function X() { return null }\n"),
            ("vue", "layout.vue", "home.vue", "<template><div /></template>\n"),
            ("svelte", "layout.svelte", "home.svelte", "<div></div>\n"),
        ],
    )
    def test_preact_vue_and_svelte_root_layouts_own_the_document_too(
        self, nexy_project, tmp_path, monkeypatch, framework, layout, page, body
    ):
        nexy_project(
            f"useCSR = True\nuseFF = {framework}()",
            imports=f"from nexy.frontend import {framework}\n",
        )
        monkeypatch.chdir(tmp_path)
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True, exist_ok=True)
        (routes / layout).write_text(body, encoding="utf-8")
        (routes / page).write_text(body, encoding="utf-8")
        install_vfs_importer()
        VFS().clear()
        FrontendRouteCompiler().compile(input=f"src/routes/{page}")
        source = VFS().read(f"__nexy__/src/routes/{Path(page).stem}.py")
        assert "__render_document" in source and "__nexy_shell" not in source

    def test_a_root_layout_of_another_framework_does_not_own_the_document(
        self, nexy_project, tmp_path, monkeypatch
    ):
        nexy_project("useCSR = True\nuseFF = vue()", imports="from nexy.frontend import vue\n")
        monkeypatch.chdir(tmp_path)
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True, exist_ok=True)
        (routes / "layout.tsx").write_text("export default () => null\n", encoding="utf-8")
        (routes / "home.vue").write_text("<template><div /></template>\n", encoding="utf-8")
        install_vfs_importer()
        VFS().clear()
        FrontendRouteCompiler().compile(input="src/routes/home.vue")
        assert "__render_document" not in VFS().read("__nexy__/src/routes/home.py")

    def test_without_a_root_layout_the_built_in_shell_is_used(
        self, nexy_project, tmp_path, monkeypatch
    ):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        monkeypatch.chdir(tmp_path)
        install_vfs_importer()
        _compile_tsx(tmp_path)
        assert "__nexy_shell" in VFS().read("__nexy__/src/routes/home.py")

    def test_layout_file_name_is_framework_owned_in_csr(self, nexy_project):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        assert "layout.tsx" in Config().LAYOUT_FILE_NAMES
        assert "layout.nexy" not in Config().LAYOUT_FILE_NAMES


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


class TestShellBehaviour:
    @staticmethod
    def _shell():
        from nexy.modules.compiler.document_shell import CSR_SHELL_FUNCTION, CSR_SHELL_HEADER

        namespace: dict = {}
        exec(CSR_SHELL_HEADER, namespace)  # noqa: S102 - trusted generated source
        return namespace[CSR_SHELL_FUNCTION]

    def test_fragment_is_wrapped_in_a_document(self, nexy_project):
        nexy_project("")
        html = self._shell()("<p>x</p>")
        assert html.startswith("<!DOCTYPE html>") and "<p>x</p>" in html

    def test_full_document_is_not_wrapped_twice(self, nexy_project):
        nexy_project("")
        page = "<!DOCTYPE html><html><body>own</body></html>"
        assert self._shell()(page) == page
        assert self._shell()("\n  <html><body></body></html>").count("<html") == 1
