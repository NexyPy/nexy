"""Which paths the dev server reacts to, and what kind of path each one is."""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.modules.cli.devtools.watch.paths import (
    is_directory_of_pages,
    is_generated_init,
    is_ignored_path,
    is_route_page,
    is_routes_directory,
    is_stray_markdown,
    needs_restart,
    normalize_path,
)


class TestNormalize:
    def test_string(self):
        assert normalize_path("some/path/file.nexy") == "some/path/file.nexy"

    def test_bytes(self):
        assert normalize_path(b"some/path/file.nexy") == "some/path/file.nexy"

    def test_backslashes(self):
        assert normalize_path("src\\routes\\index.nexy") == "src/routes/index.nexy"

    def test_strips_dot_slash(self):
        assert normalize_path("./src/routes/index.nexy") == "src/routes/index.nexy"

    def test_strips_cwd_prefix(self):
        cwd = Path.cwd().as_posix()
        assert normalize_path(f"{cwd}/src/routes/index.nexy") == "src/routes/index.nexy"

    def test_absolute_path_on_different_drive(self):
        other_drive = "E:" if Path.cwd().drive == "D:" else "D:"
        path = f"{other_drive}/other/project/src/routes/index.nexy"
        assert normalize_path(path) == path


class TestIgnored:
    @pytest.mark.parametrize(
        "path",
        [
            ".git/config",
            "venv/bin/python",
            "__pycache__/c.py",
            "node_modules/p/i.js",
            "__nexy__/g.py",
        ],
    )
    def test_generated_and_environment_paths_are_ignored(self, path):
        assert is_ignored_path(path)

    @pytest.mark.parametrize("path", ["src/routes/index.nexy", "src/lib/utils.py"])
    def test_source_paths_are_not(self, path):
        assert not is_ignored_path(path)


class TestGeneratedInit:
    def test_an_empty_init_is_not_a_change(self, tmp_path):
        init = tmp_path / "__init__.py"
        init.write_text("")
        assert is_generated_init(str(init))

    def test_an_init_with_code_is_a_change(self, tmp_path):
        init = tmp_path / "__init__.py"
        init.write_text("VALUE = 1\n")
        assert not is_generated_init(str(init))

    def test_other_files_are_a_change(self, tmp_path):
        other = tmp_path / "users.py"
        other.write_text("")
        assert not is_generated_init(str(other))


class TestStrayMarkdown:
    def test_a_readme_at_the_root_is_not_a_page(self):
        assert is_stray_markdown("README.md") is True

    def test_a_markdown_route_is_a_page(self):
        assert is_stray_markdown("src/routes/blog/post.md") is False

    def test_a_python_file_is_never_stray(self):
        assert is_stray_markdown("src/routes/users.py") is False


class TestPages:
    def test_a_nexy_file_in_the_routes_is_a_page(self):
        assert is_route_page("src/routes/about.nexy")

    def test_python_is_not_a_page(self):
        assert not is_route_page("src/routes/users.py")

    def test_a_file_outside_the_routes_is_not_a_page(self):
        assert not is_route_page("src/components/card.nexy")

    def test_a_folder_of_the_routes_is_a_directory_of_pages(self):
        assert is_directory_of_pages("src/routes/blog")

    def test_a_file_is_not_a_directory(self):
        assert not is_directory_of_pages("src/routes/blog/post.nexy")

    def test_the_routes_directory_itself_counts(self):
        assert is_routes_directory("src/routes")

    def test_a_folder_elsewhere_is_not_one(self):
        assert not is_directory_of_pages("src/components/ui")


class TestRestart:
    @pytest.mark.parametrize("path", ["a.py", "a.nexy", "a.md", "a.mdx"])
    def test_server_side_files_need_a_restart(self, path):
        assert needs_restart(path)

    def test_a_client_file_does_not(self):
        assert not needs_restart("src/components/card.tsx")
