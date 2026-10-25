"""Nested framework layouts: layout.tsx files above a page wrap it on the client."""

from pathlib import Path

from nexy.helpers.fs.vfs import VFS
from nexy.modules.compiler.frontend_route import FrontendRouteCompiler
from nexy.modules.frontend.layout_chain import framework_layout_chain, layout_key
from nexy.modules.frontend.manifest import RouteManifestBuilder
from nexy.modules.runtime.importer import install_vfs_importer

_REACT = "from nexy.frontend import react"
_COMP = "export default function C() { return null }\n"


def _write(root: Path, rel: str, content: str = _COMP) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestChain:
    def test_collects_layouts_outermost_first(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write(tmp_path, "src/routes/layout.tsx")
        _write(tmp_path, "src/routes/blog/layout.tsx")
        _write(tmp_path, "src/routes/blog/post.tsx")
        chain = framework_layout_chain(Path("src/routes/blog/post.tsx"), Path("src/routes"))
        assert chain == ["/src/routes/layout.tsx", "/src/routes/blog/layout.tsx"]

    def test_skips_directories_without_a_layout(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write(tmp_path, "src/routes/layout.tsx")
        _write(tmp_path, "src/routes/a/b/page.tsx")
        chain = framework_layout_chain(Path("src/routes/a/b/page.tsx"), Path("src/routes"))
        assert chain == ["/src/routes/layout.tsx"]

    def test_a_layout_has_no_chain_of_its_own(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write(tmp_path, "src/routes/layout.tsx")
        assert framework_layout_chain(Path("src/routes/layout.tsx"), Path("src/routes")) == []

    def test_only_jsx_pages_use_the_chain(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write(tmp_path, "src/routes/layout.tsx")
        _write(tmp_path, "src/routes/page.vue", "<template></template>")
        assert framework_layout_chain(Path("src/routes/page.vue"), Path("src/routes")) == []

    def test_a_page_outside_the_routes_directory_has_no_chain(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write(tmp_path, "src/other/page.tsx")
        assert framework_layout_chain(Path("src/other/page.tsx"), Path("src/routes")) == []


class TestManifest:
    def test_entries_carry_their_layouts(self, tmp_path, monkeypatch, nexy_project):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        monkeypatch.chdir(tmp_path)
        _write(tmp_path, "src/routes/layout.tsx")
        _write(tmp_path, "src/routes/blog/layout.tsx")
        _write(tmp_path, "src/routes/blog/post.tsx")
        entries = {e["path"]: e for e in RouteManifestBuilder().entries()}
        assert entries["/blog/post"]["layouts"] == [
            "/src/routes/layout.tsx",
            "/src/routes/blog/layout.tsx",
        ]

    def test_client_manifest_types_layouts(self, tmp_path, monkeypatch, nexy_project):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        monkeypatch.chdir(tmp_path)
        _write(tmp_path, "src/routes/layout.tsx")
        _write(tmp_path, "src/routes/index.tsx")
        text = RouteManifestBuilder().render_client() or ""
        assert "layouts: string[];" in text
        assert 'layouts: ["/src/routes/layout.tsx"]' in text


class TestCompiledPage:
    def _compile(self, tmp_path, monkeypatch, nexy_project, files):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        monkeypatch.chdir(tmp_path)
        for rel in files:
            _write(tmp_path, rel)
        VFS().clear()
        install_vfs_importer()
        FrontendRouteCompiler().compile(input="src/routes/blog/post.tsx")

    def test_page_template_lists_layout_keys(self, tmp_path, monkeypatch, nexy_project):
        self._compile(
            tmp_path,
            monkeypatch,
            nexy_project,
            ["src/routes/layout.tsx", "src/routes/blog/layout.tsx", "src/routes/blog/post.tsx"],
        )
        html = VFS().read("__nexy__/src/routes/blog/post.html")
        keys = ",".join(
            layout_key(p) for p in ("/src/routes/layout.tsx", "/src/routes/blog/layout.tsx")
        )
        assert f'data-nexy-layouts="{keys}"' in html

    def test_page_without_layouts_has_no_attribute(self, tmp_path, monkeypatch, nexy_project):
        self._compile(tmp_path, monkeypatch, nexy_project, ["src/routes/blog/post.tsx"])
        assert "data-nexy-layouts" not in VFS().read("__nexy__/src/routes/blog/post.html")

    def test_layout_pages_skip_the_ssg_snapshot(self, tmp_path, monkeypatch, nexy_project):
        self._compile(
            tmp_path,
            monkeypatch,
            nexy_project,
            ["src/routes/layout.tsx", "src/routes/blog/post.tsx"],
        )
        source = VFS().read("__nexy__/src/routes/blog/post.py")
        assert "__ssg_file" not in source

    def test_framework_layout_does_not_wrap_on_the_server(
        self, tmp_path, monkeypatch, nexy_project
    ):
        self._compile(
            tmp_path,
            monkeypatch,
            nexy_project,
            ["src/routes/layout.tsx", "src/routes/blog/post.tsx"],
        )
        source = VFS().read("__nexy__/src/routes/blog/post.py")
        assert "import Layout as __Layout" not in source
        assert "__nexy_shell" in source

    def test_root_layout_nexy_still_owns_the_document(self, tmp_path, monkeypatch, nexy_project):
        self._compile(
            tmp_path,
            monkeypatch,
            nexy_project,
            ["src/routes/layout.tsx", "src/routes/blog/post.tsx"],
        )
        (tmp_path / "src/routes/layout.nexy").write_text(
            "<html>{{children}}</html>", encoding="utf-8"
        )
        FrontendRouteCompiler().compile(input="src/routes/blog/post.tsx")
        source = VFS().read("__nexy__/src/routes/blog/post.py")
        assert "src.routes.layout import Layout as __Layout" in source
