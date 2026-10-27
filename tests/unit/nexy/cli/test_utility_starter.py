"""The React starter in Tailwind or UnoCSS is written with utility classes and React idioms."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from nexy.modules.cli.init.template_setup import _render_local_template

UTILITY_STYLES = ["tailwind", "unocss"]
COMPONENTS = [
    "button",
    "container",
    "copy-chip",
    "eyebrow",
    "footer",
    "frame",
    "framework-logo",
    "header",
    "icon",
    "line-pattern",
    "live-panel",
    "section-head",
    "steps",
    "theme-script",
    "theme-toggle",
]
EMOJI = re.compile("[\U0001f300-\U0001faff☀-➿]")


def _scaffold(dest: Path, framework: str, style: str, use_csr: bool = True) -> Path:
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


def _source_files(root: Path) -> list[Path]:
    return [*root.joinpath("src").rglob("*.tsx")]


@pytest.mark.parametrize("style", UTILITY_STYLES)
class TestUtilityStarter:
    def test_every_component_of_the_design_is_scaffolded(self, tmp_path, style):
        _scaffold(tmp_path, "react", style)
        found = sorted(p.stem for p in (tmp_path / "src" / "components").glob("*.tsx"))
        assert found == sorted(COMPONENTS)

    def test_no_class_of_the_old_stylesheet_is_left(self, tmp_path, style):
        _scaffold(tmp_path, "react", style)
        text = " ".join(p.read_text(encoding="utf-8") for p in _source_files(tmp_path))
        assert "nx-" not in text.replace("nx-spin", "").replace("nx-header", "")

    def test_no_template_syntax_is_left_in_the_sources(self, tmp_path, style):
        _scaffold(tmp_path, "react", style)
        text = " ".join(p.read_text(encoding="utf-8") for p in _source_files(tmp_path))
        assert "{%" not in text

    def test_no_source_uses_an_emoji(self, tmp_path, style):
        _scaffold(tmp_path, "react", style)
        text = " ".join(p.read_text(encoding="utf-8") for p in _source_files(tmp_path))
        assert EMOJI.search(text) is None

    def test_react_code_never_reaches_for_the_dom_by_hand(self, tmp_path, style):
        _scaffold(tmp_path, "react", style)
        components = (tmp_path / "src" / "components").glob("*.tsx")
        text = " ".join(p.read_text(encoding="utf-8") for p in components)
        assert "querySelector" not in text and "addEventListener" not in text

    def test_the_theme_switch_is_a_hook_with_state(self, tmp_path, style):
        _scaffold(tmp_path, "react", style)
        toggle = (tmp_path / "src" / "components" / "theme-toggle.tsx").read_text(encoding="utf-8")
        assert "useState" in toggle and "useEffect" in toggle

    def test_the_layout_composes_the_shared_components(self, tmp_path, style):
        _scaffold(tmp_path, "react", style)
        layout = (tmp_path / "src" / "routes" / "layout.tsx").read_text(encoding="utf-8")
        assert "<Header />" in layout and "<Footer />" in layout and "<ThemeScript />" in layout

    def test_the_home_page_confirms_the_app_is_running(self, tmp_path, style):
        _scaffold(tmp_path, "react", style)
        home = (tmp_path / "src" / "routes" / "index.tsx").read_text(encoding="utf-8")
        assert "Your app is running." in home

    def test_the_home_page_has_no_badge_or_marketing_claims(self, tmp_path, style):
        _scaffold(tmp_path, "react", style)
        home = (tmp_path / "src" / "routes" / "index.tsx").read_text(encoding="utf-8")
        assert "Built with Nexy" not in home

    def test_the_design_tokens_name_ink_paper_and_signal(self, tmp_path, style):
        _scaffold(tmp_path, "react", style)
        css = (tmp_path / "src" / "globale.css").read_text(encoding="utf-8")
        assert all(token in css for token in ("--ink:", "--paper:", "--signal:"))


@pytest.mark.parametrize("style", UTILITY_STYLES)
class TestUtilityStylesheet:
    def _css(self, dest: Path, style: str) -> str:
        _scaffold(dest, "react", style)
        return (dest / "src" / "globale.css").read_text(encoding="utf-8")

    def test_changing_page_feels_like_changing_a_tab(self, tmp_path, style):
        css = self._css(tmp_path, style)
        assert "@view-transition" in css and "::view-transition-new(root)" in css

    def test_motion_is_switched_off_for_people_who_ask(self, tmp_path, style):
        assert "prefers-reduced-motion: reduce" in self._css(tmp_path, style)

    def test_the_dark_theme_is_a_class_on_the_page(self, tmp_path, style):
        assert ".dark {" in self._css(tmp_path, style)

    def test_the_page_is_never_pure_black(self, tmp_path, style):
        assert "#000000" not in self._css(tmp_path, style).lower()

    def test_the_only_hues_are_the_framework_and_the_signal(self, tmp_path, style):
        lines = self._css(tmp_path, style).splitlines()
        plain = " ".join(
            line for line in lines if "--accent:" not in line and "--signal:" not in line
        )
        codes = re.findall(r"#([0-9a-fA-F]{6})", plain)
        spread = [
            max(int(c[i : i + 2], 16) for i in (0, 2, 4))
            - min(int(c[i : i + 2], 16) for i in (0, 2, 4))
            for c in codes
        ]
        assert max(spread) <= 12


class TestStyleSpecificTokens:
    def test_tailwind_maps_the_tokens_in_its_theme(self, tmp_path):
        _scaffold(tmp_path, "react", "tailwind")
        css = (tmp_path / "src" / "globale.css").read_text(encoding="utf-8")
        assert "--color-ink: var(--ink)" in css and "--font-display" in css

    def test_unocss_maps_the_tokens_in_its_config(self, tmp_path):
        _scaffold(tmp_path, "react", "unocss")
        config = (tmp_path / "uno.config.ts").read_text(encoding="utf-8")
        assert "ink: 'var(--ink)'" in config and "display:" in config


class TestOtherStartersAreUntouched:
    @pytest.mark.parametrize("framework", ["preact", "solid", "vue", "svelte"])
    def test_another_framework_keeps_its_starter(self, tmp_path, framework):
        _scaffold(tmp_path, framework, "tailwind")
        assert not (tmp_path / "src" / "components" / "button.tsx").exists()

    def test_plain_css_keeps_its_starter(self, tmp_path):
        _scaffold(tmp_path, "react", "vanilla")
        assert not (tmp_path / "src" / "components" / "button.tsx").exists()

    def test_server_mode_keeps_its_starter(self, tmp_path):
        _scaffold(tmp_path, "react", "tailwind", use_csr=False)
        assert not (tmp_path / "src" / "components" / "button.tsx").exists()
