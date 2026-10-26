"""The home page of a new project: one design for every framework and style, nothing unstyled."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from nexy.modules.cli.init.template_setup import _render_local_template
from nexy.vite import _BOOT_GATE, _development_tags

FRAMEWORKS = [("none", False), ("react", False), ("react", True), ("vue", True), ("svelte", True)]
ROUTE_EXT = {"none": "nexy", "react": "tsx", "vue": "vue", "svelte": "svelte"}


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


def _home(dest: Path, framework: str, use_csr: bool) -> str:
    ext = ROUTE_EXT[framework] if use_csr or framework == "none" else "nexy"
    return (dest / "src" / "routes" / f"index.{ext}").read_text(encoding="utf-8")


@pytest.mark.parametrize(("framework", "use_csr"), FRAMEWORKS)
class TestHome:
    def test_the_hero_says_what_nexy_is(self, tmp_path, framework, use_csr):
        _scaffold(tmp_path, framework, use_csr)
        assert "The Python framework for the whole web app." in _home(tmp_path, framework, use_csr)

    def test_the_steps_are_three_tabs(self, tmp_path, framework, use_csr):
        _scaffold(tmp_path, framework, use_csr)
        assert _home(tmp_path, framework, use_csr).count('type="radio"') == 3

    def test_the_command_can_be_copied(self, tmp_path, framework, use_csr):
        _scaffold(tmp_path, framework, use_csr)
        assert 'data-copy="nx new my-app"' in _home(tmp_path, framework, use_csr)

    def test_both_illustrations_ship_with_the_project(self, tmp_path, framework, use_csr):
        _scaffold(tmp_path, framework, use_csr)
        home = _home(tmp_path, framework, use_csr)
        public = tmp_path / "public"
        for name in ("hero-light.svg", "hero-dark.svg"):
            assert name in home and (public / name).is_file()

    def test_exactly_one_file_is_selected_at_first(self, tmp_path, framework, use_csr):
        _scaffold(tmp_path, framework, use_csr)
        home = _home(tmp_path, framework, use_csr)
        assert home.count("defaultChecked") + home.count(" checked") == 1

    def test_labels_point_at_their_inputs_in_the_syntax_of_the_framework(
        self, tmp_path, framework, use_csr
    ):
        _scaffold(tmp_path, framework, use_csr)
        home = _home(tmp_path, framework, use_csr)
        attribute = "htmlFor" if framework == "react" and use_csr else "for"
        assert f'{attribute}="nx-t-ship"' in home

    def test_no_utility_class_is_needed_to_look_right(self, tmp_path, framework, use_csr):
        _scaffold(tmp_path, framework, use_csr)
        home = _home(tmp_path, framework, use_csr)
        assert "text-foreground-second" not in home and "max-w-5xl" not in home
        assert "style=" not in home

    def test_the_counter_is_a_segmented_control(self, tmp_path, framework, use_csr):
        _scaffold(tmp_path, framework, use_csr)
        counter = next((tmp_path / "src" / "components" / "counter").glob("counter.*"))
        assert "nx-counter" in counter.read_text(encoding="utf-8")

    def test_the_page_is_not_dark_before_the_theme_is_known(self, tmp_path, framework, use_csr):
        _scaffold(tmp_path, framework, use_csr)
        layout = next((tmp_path / "src" / "routes").glob("layout.*"))
        assert 'class="dark"' not in layout.read_text(encoding="utf-8")

    def test_the_layout_loads_the_fonts_the_design_uses(self, tmp_path, framework, use_csr):
        _scaffold(tmp_path, framework, use_csr)
        layout = next((tmp_path / "src" / "routes").glob("layout.*"))
        assert "Bricolage+Grotesque" in layout.read_text(encoding="utf-8")


@pytest.mark.parametrize("style", ["tailwind", "unocss", "vanilla", "other"])
class TestStylesheet:
    def test_every_style_gets_the_same_starter_classes(self, tmp_path, style):
        _scaffold(tmp_path, "react", True, style)
        css = (tmp_path / "src" / "globale.css").read_text(encoding="utf-8")
        names = (".nx-hero", ".nx-tabs", ".nx-bento", ".nx-switch", ".btn-primary")
        assert all(name in css for name in names)

    def test_changing_page_feels_like_changing_a_tab(self, tmp_path, style):
        _scaffold(tmp_path, "react", True, style)
        css = (tmp_path / "src" / "globale.css").read_text(encoding="utf-8")
        assert "@view-transition" in css and "::view-transition-new(root)" in css

    def test_the_page_is_not_black_in_the_dark(self, tmp_path, style):
        _scaffold(tmp_path, "react", True, style)
        css = (tmp_path / "src" / "globale.css").read_text(encoding="utf-8")
        assert "#062b24" in css and "#000000" not in css.lower()

    def test_the_dark_theme_is_a_class_on_the_page(self, tmp_path, style):
        _scaffold(tmp_path, "react", True, style)
        css = (tmp_path / "src" / "globale.css").read_text(encoding="utf-8")
        assert ".dark {" in css and ":root.dark .nx-switch-thumb" in css

    def test_motion_is_switched_off_for_people_who_ask(self, tmp_path, style):
        _scaffold(tmp_path, "react", True, style)
        css = (tmp_path / "src" / "globale.css").read_text(encoding="utf-8")
        assert "prefers-reduced-motion: no-preference" in css


class TestSwitch:
    @pytest.mark.parametrize(("framework", "use_csr"), FRAMEWORKS)
    def test_it_is_an_accessible_switch(self, tmp_path, framework, use_csr):
        _scaffold(tmp_path, framework, use_csr)
        components = tmp_path / "src" / "components"
        holder = next(iter(components.glob("theme-toggle.*")), components / "header.nexy")
        text = holder.read_text(encoding="utf-8")
        assert 'role="switch"' in text and "aria-checked" in text and "aria-label" in text


class TestNoFlashOfUnstyledPage:
    def test_development_hides_the_page_until_the_client_has_loaded_its_styles(self):
        assert "visibility:hidden" in _BOOT_GATE and "nexy-boot" in _BOOT_GATE

    def test_the_gate_always_has_a_way_out(self):
        assert "setTimeout" in _BOOT_GATE

    def test_the_gate_comes_before_the_scripts(self, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        tags = _development_tags()
        assert tags.index("nexy-boot") < tags.index("/@vite/client")


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_the_script_of_the_head_is_valid_javascript():
    from nexy.modules.cli.constants import TEMPLATES_DIR

    script = TEMPLATES_DIR / "_partials" / "theme_script.js"
    done = subprocess.run(["node", "--check", str(script)], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr


def test_a_failed_copy_is_not_reported_as_done():
    from nexy.modules.cli.constants import TEMPLATES_DIR

    script = (TEMPLATES_DIR / "_partials" / "theme_script.js").read_text(encoding="utf-8")
    assert "copyWithSelection" in script and "}, function () {});" in script
