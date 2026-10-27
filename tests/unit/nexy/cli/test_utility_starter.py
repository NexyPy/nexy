"""The starter in Tailwind or UnoCSS uses utility classes and the idioms of its framework."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from nexy.modules.cli.init.template_setup import _render_local_template

UTILITY_STYLES = ["tailwind", "unocss"]
SHARED = [
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
    "theme-toggle",
]
# (framework, client-routed, extension, components besides the shared ones, logo label)
TARGETS = {
    "react": ("react", True, "tsx", ["theme-script"], "React"),
    "preact": ("preact", True, "tsx", ["theme-script"], "Preact"),
    "solid": ("solid", True, "tsx", ["theme-script"], "Solid"),
    "vue": ("vue", True, "vue", ["live-row", "step-check"], "Vue"),
    "svelte": ("svelte", True, "svelte", ["live-row", "step-check"], "Svelte"),
    "none": ("none", False, "nexy", ["live-row"], "JavaScript"),
    "react-server": ("react", False, "nexy", ["live-row"], "React"),
}
CLIENT_TARGETS = [name for name, target in TARGETS.items() if target[2] != "nexy"]
EMOJI = re.compile("[\U0001f300-\U0001faff☀-➿]")
HAND_DOM = ("querySelector", "addEventListener", "innerHTML =")


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


def _file_name(name: str, extension: str) -> str:
    """The file of a component: a .nexy component is named like its tag, in PascalCase."""
    if extension == "nexy":
        return "".join(part.capitalize() for part in name.split("-")) + ".nexy"
    return f"{name}.{extension}"


def _component(root: Path, name: str, extension: str) -> Path:
    return root / "src" / "components" / _file_name(name, extension)


def _sources(root: Path, extension: str) -> list[Path]:
    return sorted((root / "src").rglob(f"*.{extension}"))


def _text(root: Path, extension: str) -> str:
    return " ".join(path.read_text(encoding="utf-8") for path in _sources(root, extension))


@pytest.fixture(params=sorted(TARGETS))
def target(request):
    return TARGETS[request.param]


@pytest.mark.parametrize("style", UTILITY_STYLES)
class TestEveryFramework:
    def _project(self, tmp_path, target, style):
        framework, use_csr, extension, extra, label = target
        _scaffold(tmp_path, framework, style, use_csr)
        return tmp_path, extension, extra, label

    def test_every_component_of_the_design_is_scaffolded(self, tmp_path, target, style):
        root, extension, extra, _ = self._project(tmp_path, target, style)
        found = sorted(p.name for p in (root / "src" / "components").glob(f"*.{extension}"))
        assert found == sorted(_file_name(name, extension) for name in [*SHARED, *extra])

    def test_the_three_pages_exist(self, tmp_path, target, style):
        root, extension, _, _ = self._project(tmp_path, target, style)
        routes = root / "src" / "routes"
        assert all(
            (routes / f"{name}.{extension}").is_file() for name in ("layout", "index", "about")
        )

    def test_no_class_of_the_old_stylesheet_is_left(self, tmp_path, target, style):
        root, extension, _, _ = self._project(tmp_path, target, style)
        text = _text(root, extension).replace("nx-spin", "").replace("nx-header", "")
        assert "nx-" not in text

    def test_a_nexy_page_has_no_scaffold_time_markers_left(self, tmp_path, target, style):
        root, extension, _, _ = self._project(tmp_path, target, style)
        assert "{% raw %}" not in _text(root, extension) and "{% endraw %}" not in _text(
            root, extension
        )

    def test_no_source_uses_an_emoji(self, tmp_path, target, style):
        root, extension, _, _ = self._project(tmp_path, target, style)
        assert EMOJI.search(_text(root, extension)) is None

    def test_the_logo_is_the_one_of_the_framework(self, tmp_path, target, style):
        root, extension, _, label = self._project(tmp_path, target, style)
        logo = _component(root, "framework-logo", extension).read_text(encoding="utf-8")
        assert f'aria-label="{label}"' in logo

    def test_the_home_page_confirms_the_app_is_running(self, tmp_path, target, style):
        root, extension, _, _ = self._project(tmp_path, target, style)
        home = (root / "src" / "routes" / f"index.{extension}").read_text(encoding="utf-8")
        assert "Your app is running." in home and "Built with Nexy" not in home

    def test_the_first_step_names_a_file_of_the_project(self, tmp_path, target, style):
        root, extension, _, _ = self._project(tmp_path, target, style)
        steps = _component(root, "steps", extension).read_text(encoding="utf-8")
        assert f"src/routes/index.{extension}" in steps

    def test_the_design_tokens_name_ink_paper_and_signal(self, tmp_path, target, style):
        root, _, _, _ = self._project(tmp_path, target, style)
        css = (root / "src" / "globale.css").read_text(encoding="utf-8")
        assert all(token in css for token in ("--ink:", "--paper:", "--signal:"))


@pytest.mark.parametrize("style", UTILITY_STYLES)
@pytest.mark.parametrize("name", CLIENT_TARGETS)
class TestIdiomaticClientCode:
    def test_no_template_syntax_is_left_in_the_sources(self, tmp_path, name, style):
        framework, use_csr, extension, _, _ = TARGETS[name]
        _scaffold(tmp_path, framework, style, use_csr)
        assert "{%" not in _text(tmp_path, extension)

    def _components(self, tmp_path, name, style) -> str:
        framework, use_csr, extension, _, _ = TARGETS[name]
        _scaffold(tmp_path, framework, style, use_csr)
        return (
            _text(tmp_path / "src" / "components", extension)
            if False
            else " ".join(
                p.read_text(encoding="utf-8")
                for p in (tmp_path / "src" / "components").glob(f"*.{extension}")
            )
        )

    def test_it_never_reaches_for_the_dom_by_hand(self, tmp_path, name, style):
        text = self._components(tmp_path, name, style)
        assert not any(mark in text for mark in HAND_DOM)

    def test_the_theme_switch_keeps_state_the_way_its_framework_does(self, tmp_path, name, style):
        framework, use_csr, extension, _, _ = TARGETS[name]
        _scaffold(tmp_path, framework, style, use_csr)
        toggle = _component(tmp_path, "theme-toggle", extension).read_text(encoding="utf-8")
        marker = {
            "react": "useState",
            "preact": "preact/hooks",
            "solid": "createSignal",
            "vue": "ref(false)",
            "svelte": "$state(false)",
        }[name]
        assert marker in toggle and 'role="switch"' in toggle


class TestFrameworkSpecificRules:
    def test_preact_writes_class_and_imports_its_hooks(self, tmp_path):
        _scaffold(tmp_path, "preact", "unocss")
        header = (tmp_path / "src/components/header.tsx").read_text(encoding="utf-8")
        assert 'from "preact/hooks"' in header and "className=" not in header.replace(
            "<Container", ""
        )

    def test_solid_never_destructures_its_props(self, tmp_path):
        _scaffold(tmp_path, "solid", "unocss")
        button = (tmp_path / "src/components/button.tsx").read_text(encoding="utf-8")
        assert "export default function Button(props:" in button

    def test_solid_loops_with_for(self, tmp_path):
        _scaffold(tmp_path, "solid", "unocss")
        footer = (tmp_path / "src/components/footer.tsx").read_text(encoding="utf-8")
        assert "<For each={LINKS}>" in footer and ".map(" not in footer

    def test_vue_components_use_script_setup(self, tmp_path):
        _scaffold(tmp_path, "vue", "unocss")
        button = (tmp_path / "src/components/button.vue").read_text(encoding="utf-8")
        assert '<script setup lang="ts">' in button

    def test_svelte_components_use_runes(self, tmp_path):
        _scaffold(tmp_path, "svelte", "unocss")
        steps = (tmp_path / "src/components/steps.svelte").read_text(encoding="utf-8")
        assert "$state(" in steps and "$derived(" in steps

    def test_the_server_pages_use_the_slot_tag_with_a_capital(self, tmp_path):
        _scaffold(tmp_path, "none", "unocss", use_csr=False)
        container = (tmp_path / "src/components/Container.nexy").read_text(encoding="utf-8")
        assert "<Slot />" in container and "<slot" not in container

    def test_a_server_page_keeps_its_scripts_in_the_component_that_owns_them(self, tmp_path):
        _scaffold(tmp_path, "none", "unocss", use_csr=False)
        toggle = (tmp_path / "src/components/ThemeToggle.nexy").read_text(encoding="utf-8")
        assert "<script>" in toggle and 'localStorage.setItem("nexy-theme"' in toggle


class TestStyleSpecificTokens:
    def test_tailwind_maps_the_tokens_in_its_theme(self, tmp_path):
        _scaffold(tmp_path, "react", "tailwind")
        css = (tmp_path / "src" / "globale.css").read_text(encoding="utf-8")
        assert "--color-ink: var(--ink)" in css and "--font-display" in css

    def test_unocss_maps_the_tokens_in_its_config(self, tmp_path):
        _scaffold(tmp_path, "react", "unocss")
        config = (tmp_path / "uno.config.ts").read_text(encoding="utf-8")
        assert "ink: 'var(--ink)'" in config and "display:" in config

    def test_unocss_reads_the_nexy_pages_of_a_server_project(self, tmp_path):
        _scaffold(tmp_path, "none", "unocss", use_csr=False)
        config = (tmp_path / "uno.config.ts").read_text(encoding="utf-8")
        assert "src/**/*.nexy" in config

    def test_a_client_routed_project_does_not_scan_nexy_files(self, tmp_path):
        _scaffold(tmp_path, "react", "unocss")
        assert "*.nexy" not in (tmp_path / "uno.config.ts").read_text(encoding="utf-8")

    @pytest.mark.parametrize(
        ("framework", "accent"),
        [
            ("react", "#61DAFB"),
            ("preact", "#8E6CF0"),
            ("solid", "#4F88C6"),
            ("vue", "#42B883"),
            ("svelte", "#FF3E00"),
            ("none", "#F7DF1E"),
        ],
    )
    def test_the_accent_is_the_colour_of_the_framework(self, tmp_path, framework, accent):
        _scaffold(tmp_path, framework, "tailwind", use_csr=framework != "none")
        css = (tmp_path / "src" / "globale.css").read_text(encoding="utf-8")
        assert f"--accent: {accent};" in css


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


class TestPlainCssKeepsItsStarter:
    @pytest.mark.parametrize("framework", ["react", "preact", "solid", "vue", "svelte"])
    def test_a_client_framework_in_plain_css_has_no_utility_component(self, tmp_path, framework):
        _scaffold(tmp_path, framework, "vanilla")
        assert not list((tmp_path / "src" / "components").glob("button.*"))

    def test_a_server_project_in_plain_css_has_no_utility_component(self, tmp_path):
        _scaffold(tmp_path, "none", "vanilla", use_csr=False)
        assert not (tmp_path / "src" / "components" / "Button.nexy").exists()

    def test_the_modular_router_keeps_its_starter(self, tmp_path):
        config = {
            "client_framework": "none",
            "FBRouter": False,
            "project_type": "web",
            "orm": "None",
            "useCSR": False,
            "style": "tailwind",
        }
        _render_local_template("web-modular", tmp_path, config, "demo")
        assert not (tmp_path / "src" / "components" / "Button.nexy").exists()
