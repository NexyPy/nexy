"""The plain-CSS starter opens its mobile menu as a sheet from the left edge."""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.modules.cli.init.template_setup import _render_local_template


def _scaffold(dest: Path, framework: str = "none", use_csr: bool = False) -> Path:
    config = {
        "client_framework": framework,
        "FBRouter": True,
        "project_type": "web",
        "orm": "None",
        "useCSR": use_csr,
        "style": "vanilla",
    }
    _render_local_template("web-fbr", dest, config, "demo")
    return dest


def _header(tmp_path: Path, name: str = "header.nexy") -> str:
    return (tmp_path / "src" / "components" / name).read_text(encoding="utf-8")


def _css(tmp_path: Path) -> str:
    return (tmp_path / "src" / "globale.css").read_text(encoding="utf-8")


class TestTheServerHeader:
    def test_the_bar_offers_a_menu_button(self, tmp_path):
        _scaffold(tmp_path)
        assert "data-menu-button" in _header(tmp_path)

    def test_the_button_says_whether_the_menu_is_open(self, tmp_path):
        _scaffold(tmp_path)
        assert 'aria-expanded="false"' in _header(tmp_path)

    def test_the_button_points_at_the_panel(self, tmp_path):
        _scaffold(tmp_path)
        header = _header(tmp_path)
        assert 'aria-controls="nx-menu"' in header and 'id="nx-menu"' in header

    def test_the_panel_is_a_modal_dialog(self, tmp_path):
        _scaffold(tmp_path)
        header = _header(tmp_path)
        assert 'role="dialog"' in header and 'aria-modal="true"' in header

    def test_the_panel_sits_outside_the_blurred_bar(self, tmp_path):
        _scaffold(tmp_path)
        header = _header(tmp_path)
        # The bar blurs its backdrop, which anchors a fixed child to the bar, not the screen.
        assert header.index("</header>") < header.index("data-menu-panel")

    def test_the_panel_starts_hidden(self, tmp_path):
        _scaffold(tmp_path)
        assert "data-menu-panel hidden" in _header(tmp_path)

    def test_escape_closes_the_menu(self, tmp_path):
        _scaffold(tmp_path)
        assert 'event.key === "Escape"' in _header(tmp_path)

    def test_the_page_behind_stops_scrolling(self, tmp_path):
        _scaffold(tmp_path)
        assert 'document.body.style.overflow = open ? "hidden" : ""' in _header(tmp_path)

    def test_the_focus_moves_into_the_panel(self, tmp_path):
        _scaffold(tmp_path)
        assert "dialog.focus()" in _header(tmp_path)

    def test_no_jinja_is_left_in_the_header(self, tmp_path):
        _scaffold(tmp_path)
        assert "{%" not in _header(tmp_path)


CLIENT_FILES = {
    "react": ("src/components/header.tsx", "src/components/sheet.tsx"),
    "preact": ("src/components/header.tsx", "src/components/sheet.tsx"),
    "solid": ("src/components/header.tsx", "src/components/sheet.tsx"),
    "vue": ("src/routes/layout.vue", "src/components/sheet.vue"),
    "svelte": ("src/routes/layout.svelte", "src/components/sheet.svelte"),
}


def _client(tmp_path: Path, framework: str) -> tuple[str, str]:
    _scaffold(tmp_path, framework, True)
    header, sheet = CLIENT_FILES[framework]
    return (tmp_path / header).read_text("utf-8"), (tmp_path / sheet).read_text("utf-8")


@pytest.mark.parametrize("framework", list(CLIENT_FILES))
class TestTheClientRoutedHeader:
    def test_the_bar_offers_a_menu_button(self, tmp_path, framework):
        header, _sheet = _client(tmp_path, framework)
        assert 'aria-controls="nx-menu"' in header

    def test_the_menu_is_the_sheet_component(self, tmp_path, framework):
        header, _sheet = _client(tmp_path, framework)
        assert '<Sheet id="nx-menu"' in header

    def test_the_sheet_sits_outside_the_blurred_bar(self, tmp_path, framework):
        header, _sheet = _client(tmp_path, framework)
        assert header.index("</header>") < header.index("<Sheet")

    def test_the_sheet_is_a_modal_dialog(self, tmp_path, framework):
        _header, sheet = _client(tmp_path, framework)
        assert 'role="dialog"' in sheet and 'aria-modal="true"' in sheet

    def test_the_sheet_is_drawn_by_the_starter_stylesheet(self, tmp_path, framework):
        _header, sheet = _client(tmp_path, framework)
        assert 'class' in sheet and '"nx-sheet"' in sheet

    def test_the_sheet_carries_no_utility_class(self, tmp_path, framework):
        _header, sheet = _client(tmp_path, framework)
        assert "inset-0" not in sheet

    def test_no_jinja_is_left(self, tmp_path, framework):
        header, sheet = _client(tmp_path, framework)
        assert "{{" not in header.replace("{{ title }}", "") and "{%" not in sheet + header


class TestTheStylesheet:
    def test_it_carries_the_slide_from_the_left_edge(self, tmp_path):
        _scaffold(tmp_path)
        css = _css(tmp_path)
        assert "@keyframes nx-sheet-in" in css and ".nx-sheet {" in css

    def test_it_fades_the_scrim(self, tmp_path):
        _scaffold(tmp_path)
        assert "@keyframes nx-scrim-in" in _css(tmp_path)

    def test_a_closing_sheet_slides_back(self, tmp_path):
        _scaffold(tmp_path)
        css = _css(tmp_path)
        assert "@keyframes nx-sheet-out" in css and '.nx-sheet[data-state="closed"]' in css

    def test_the_logo_of_the_sheet_turns_light_in_dark_mode(self, tmp_path):
        _scaffold(tmp_path)
        assert ":root.dark .nx-sheet-head img" in _css(tmp_path)

    def test_every_link_of_the_sheet_fits_a_thumb(self, tmp_path):
        _scaffold(tmp_path)
        css = _css(tmp_path)
        link = css[css.index(".nx-sheet-link {") :]
        assert "min-height: 2.75rem" in link[: link.index("}")]

    def test_the_phone_trades_the_links_for_the_button(self, tmp_path):
        _scaffold(tmp_path)
        css = _css(tmp_path)
        narrow = css[css.index("@media (max-width: 47.99rem)") :]
        assert ".nx-nav-links" in narrow and "display: none" in narrow

    def test_a_reduced_motion_preference_turns_the_slide_off(self, tmp_path):
        _scaffold(tmp_path)
        css = _css(tmp_path)
        reduced = css[css.index("prefers-reduced-motion") :]
        assert ".nx-sheet," in reduced
