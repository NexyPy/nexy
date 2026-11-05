"""The mobile menu is a sheet that comes from the left edge, in every framework of the starter."""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.modules.cli.init.template_setup import _render_local_template

CSR = [("react", "tsx"), ("preact", "tsx"), ("solid", "tsx"), ("vue", "vue"), ("svelte", "svelte")]


def _scaffold(dest: Path, framework: str, use_csr: bool, style: str = "tailwind") -> Path:
    config = {
        "client_framework": framework,
        "FBRouter": True,
        "project_type": "web",
        "orm": "None",
        "useCSR": use_csr,
        "style": style,
    }
    _render_local_template("web-fbr", dest, config, "demo")
    return dest


def _sheet(tmp_path: Path, ext: str) -> str:
    return (tmp_path / "src" / "components" / f"sheet.{ext}").read_text(encoding="utf-8")


def _header(tmp_path: Path, ext: str) -> str:
    return (tmp_path / "src" / "components" / f"header.{ext}").read_text(encoding="utf-8")


@pytest.mark.parametrize(("framework", "ext"), CSR)
class TestClientSheet:
    def test_the_sheet_is_a_component_of_the_project(self, tmp_path, framework, ext):
        _scaffold(tmp_path, framework, True)
        assert (tmp_path / "src" / "components" / f"sheet.{ext}").is_file()

    def test_the_sheet_is_a_modal_dialog(self, tmp_path, framework, ext):
        _scaffold(tmp_path, framework, True)
        assert 'role="dialog"' in _sheet(tmp_path, ext) and "aria-modal" in _sheet(tmp_path, ext)

    def test_the_sheet_comes_from_the_left_edge(self, tmp_path, framework, ext):
        _scaffold(tmp_path, framework, True)
        assert "left-0" in _sheet(tmp_path, ext)

    def test_escape_closes_the_sheet(self, tmp_path, framework, ext):
        _scaffold(tmp_path, framework, True)
        assert "Escape" in _sheet(tmp_path, ext)

    def test_the_sheet_holds_the_page_still_while_it_is_open(self, tmp_path, framework, ext):
        _scaffold(tmp_path, framework, True)
        assert "overflow" in _sheet(tmp_path, ext)

    def test_the_header_opens_it(self, tmp_path, framework, ext):
        _scaffold(tmp_path, framework, True)
        assert f"/sheet.{ext}" in _header(tmp_path, ext)

    def test_no_jinja_is_left_in_the_sheet(self, tmp_path, framework, ext):
        _scaffold(tmp_path, framework, True)
        assert "{%" not in _sheet(tmp_path, ext)

    def test_the_panel_carries_the_class_that_slides_it(self, tmp_path, framework, ext):
        _scaffold(tmp_path, framework, True)
        cls = "className" if framework == "react" else "class"
        panel = _sheet(tmp_path, ext)
        assert f'{cls}="sheet ' in panel and f'{cls}="sheet-scrim ' in panel


class TestServerRenderedSheet:
    def test_the_header_uses_the_same_sheet(self, tmp_path):
        _scaffold(tmp_path, "none", False)
        header = (tmp_path / "src" / "components" / "Header.nexy").read_text(encoding="utf-8")
        assert "data-sheet" in header

    def test_the_server_sheet_is_a_modal_dialog(self, tmp_path):
        _scaffold(tmp_path, "none", False)
        header = (tmp_path / "src" / "components" / "Header.nexy").read_text(encoding="utf-8")
        assert 'aria-modal="true"' in header

    def test_the_server_sheet_closes_on_escape(self, tmp_path):
        _scaffold(tmp_path, "none", False)
        header = (tmp_path / "src" / "components" / "Header.nexy").read_text(encoding="utf-8")
        assert "Escape" in header

    def test_the_server_sheet_comes_from_the_left_edge(self, tmp_path):
        _scaffold(tmp_path, "none", False)
        header = (tmp_path / "src" / "components" / "Header.nexy").read_text(encoding="utf-8")
        assert "left-0" in header


@pytest.mark.parametrize("style", ["tailwind", "unocss"])
class TestTheAnimationIsDefined:
    def test_the_stylesheet_holds_the_keyframes_the_sheet_names(self, tmp_path, style):
        _scaffold(tmp_path, "react", True, style)
        css = (tmp_path / "src" / "globale.css").read_text(encoding="utf-8")
        assert "@keyframes sheet-in" in css and ".sheet {" in css and ".sheet-scrim {" in css

    def test_a_reduced_motion_preference_turns_the_slide_off(self, tmp_path, style):
        _scaffold(tmp_path, "react", True, style)
        css = (tmp_path / "src" / "globale.css").read_text(encoding="utf-8")
        reduced = css[css.index("prefers-reduced-motion") :]
        assert ".sheet," in reduced and ".sheet-scrim {" in reduced
