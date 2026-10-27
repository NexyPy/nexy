"""The pieces every route compiler shares: paths, layout wrapping and package files."""

from __future__ import annotations

from nexy.helpers.fs.vfs import VFS
from nexy.helpers.fs.vfs_packages import write_package_inits
from nexy.modules.compiler.document_shell import (
    CSR_SHELL_HEADER,
    CSR_SHELL_RENDER,
    LAYOUT_RENDER,
    layout_parts,
)
from nexy.modules.compiler.route_paths import route_paths


class TestRoutePaths:
    def test_a_page_is_served_at_its_path(self):
        assert route_paths("src/routes/blog/post.tsx", "post").pathname == "/blog/post"

    def test_a_dynamic_segment_becomes_a_parameter(self):
        assert route_paths("src/routes/blog/[slug].tsx", "[slug]").pathname == "/blog/{slug}"

    def test_the_index_is_the_root(self):
        assert route_paths("src/routes/index.tsx", "index").pathname == "/"

    def test_the_generated_files_share_one_stem(self):
        paths = route_paths("src/routes/about.tsx", "about")
        assert paths.py_path.endswith("about.py") and paths.html_path.endswith("about.html")
        assert paths.meta_path.endswith("about.meta.json")

    def test_the_component_is_named_after_the_file(self):
        assert route_paths("src/routes/about.tsx", "about").component == "About"

    def test_a_file_with_no_name_is_the_index(self):
        assert route_paths("src/routes/.tsx", "").component == "Index"

    def test_the_package_is_the_folder_of_the_module(self):
        paths = route_paths("src/routes/blog/post.tsx", "post")
        assert paths.package == paths.namespaced.rsplit("/", 1)[0]


class TestLayoutParts:
    def test_a_layout_wraps_the_view(self):
        header, wrapper = layout_parts("src.routes.layout", fallback_shell=True)
        assert "from src.routes.layout import Layout as __Layout" in header
        assert wrapper == LAYOUT_RENDER

    def test_a_missing_layout_module_degrades_to_a_visible_marker(self):
        header, _ = layout_parts("src.routes.layout", fallback_shell=False)
        assert "except ImportError" in header and "Layout not available" in header

    def test_without_a_layout_a_route_gets_the_document_shell(self):
        assert layout_parts(None, fallback_shell=True) == (CSR_SHELL_HEADER, CSR_SHELL_RENDER)

    def test_without_a_layout_a_component_stays_a_fragment(self):
        assert layout_parts(None, fallback_shell=False) == ("", "rendered")


class TestPackageInits:
    def test_every_folder_of_the_path_gets_an_init(self):
        vfs = VFS()
        vfs.clear()
        write_package_inits(vfs, "pkg_a/pkg_b/pkg_c")
        assert all(
            vfs.exists(f"{p}/__init__.py") for p in ("pkg_a", "pkg_a/pkg_b", "pkg_a/pkg_b/pkg_c")
        )
        vfs.clear()

    def test_an_existing_init_is_kept(self):
        vfs = VFS()
        vfs.clear()
        vfs.write("pkg_k/__init__.py", "X = 1")
        write_package_inits(vfs, "pkg_k/sub")
        assert vfs.read("pkg_k/__init__.py") == "X = 1"
        vfs.clear()

    def test_backslashes_are_accepted(self):
        vfs = VFS()
        vfs.clear()
        write_package_inits(vfs, "pkg_w\\inner")
        assert vfs.exists("pkg_w/inner/__init__.py")
        vfs.clear()
