"""The plain-CSS starter opens its mobile menu as a sheet from the left edge."""

from __future__ import annotations

from pathlib import Path

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


class TestTheClientRoutedHeader:
    def test_it_has_no_button_that_could_not_work(self, tmp_path):
        _scaffold(tmp_path, "react", True)
        assert "data-menu-button" not in _header(tmp_path, "header.tsx")

    def test_it_has_no_sheet_script(self, tmp_path):
        _scaffold(tmp_path, "react", True)
        assert "addEventListener" not in _header(tmp_path, "header.tsx")


class TestTheStylesheet:
    def test_it_carries_the_slide_from_the_left_edge(self, tmp_path):
        _scaffold(tmp_path)
        css = _css(tmp_path)
        assert "@keyframes nx-sheet-in" in css and ".nx-sheet {" in css

    def test_it_fades_the_scrim(self, tmp_path):
        _scaffold(tmp_path)
        assert "@keyframes nx-scrim-in" in _css(tmp_path)

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
