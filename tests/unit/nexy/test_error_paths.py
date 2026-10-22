import pytest
from jinja2 import TemplateNotFound

from nexy.compiler import Compiler
from nexy.errors import NexyCompileError
from nexy.hooks import usePathname, useViews
from nexy.modules.builder.discovery import Discovery
from nexy.template import Template


class TestCompilerErrorPaths:
    def test_missing_input_file_raises_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError, match="missing.nexy"):
            Compiler().compile(input="missing.nexy")

    def test_existing_non_component_file_raises_compile_error(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / "notes.txt").write_text("not a component", encoding="utf-8")

        with pytest.raises(NexyCompileError, match="is not a nexy component"):
            Compiler().compile(input="notes.txt")


class TestDiscoveryErrorPaths:
    def test_scan_missing_directory_raises_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError, match="nope"):
            Discovery().scan("nope")


class TestTemplateErrorPaths:
    def test_render_unknown_template_raises_template_not_found(self, nexy_project) -> None:
        nexy_project("")

        with pytest.raises(TemplateNotFound):
            Template().render("does-not-exist.html")


class TestRemoteFetchErrorPaths:
    def test_non_http_scheme_is_rejected(self, nexy_project) -> None:
        from nexy.modules.cli.commands.add import fetch_remote_component

        nexy_project("")

        assert fetch_remote_component("file:///etc/passwd") is None

    def test_ftp_scheme_is_rejected(self, nexy_project) -> None:
        from nexy.modules.cli.commands.add import fetch_remote_component

        nexy_project("")

        assert fetch_remote_component("ftp://example.com/x.tsx") is None


class TestHooksErrorPaths:
    def test_use_views_unsupported_extension_raises_value_error(self, nexy_project) -> None:
        nexy_project("")

        with pytest.raises(ValueError, match="Unsupported view type"):
            useViews("page.txt")

    def test_use_pathname_outside_request_raises_runtime_error(self, nexy_project) -> None:
        nexy_project("")

        with pytest.raises(RuntimeError, match="within the context of an HTTP request"):
            usePathname()


class TestNexyCompileErrorFormatting:
    def test_str_without_location(self) -> None:
        error = NexyCompileError(source_path="src/routes/a.nexy", message="boom")

        assert str(error) == "src/routes/a.nexy - boom"

    def test_str_with_line_and_column(self) -> None:
        error = NexyCompileError(source_path="a.nexy", message="boom", line=4, column=2)

        assert str(error) == "a.nexy:4:2 - boom"

    def test_str_with_line_defaults_column_to_zero(self) -> None:
        error = NexyCompileError(source_path="a.nexy", message="boom", line=4)

        assert str(error) == "a.nexy:4:0 - boom"
