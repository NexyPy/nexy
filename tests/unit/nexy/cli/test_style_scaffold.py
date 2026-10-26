"""`nx new` styles the starter with Tailwind CSS, UnoCSS or a plain stylesheet."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from nexy.modules.cli.init.template_setup import _render_local_template
from nexy.modules.frontend.vite_entry import write_main_file


def _scaffold(dest: Path, style: str, framework: str = "react") -> Path:
    config = {
        "client_framework": framework,
        "FBRouter": True,
        "project_type": "web",
        "orm": "None",
        "useCSR": framework != "none",
        "style": style,
    }
    _render_local_template("web-fbr", dest, config, "demo")
    return dest


def _read(dest: Path, name: str) -> str:
    return (dest / name).read_text(encoding="utf-8")


class TestTailwind:
    def test_it_installs_and_loads_tailwind(self, tmp_path):
        _scaffold(tmp_path, "tailwind")
        assert "tailwindcss" in _read(tmp_path, "package.json")
        assert "tailwindcss()" in _read(tmp_path, "vite.config.ts")
        assert '@import "tailwindcss"' in _read(tmp_path, "src/globale.css")

    def test_it_has_no_unocss_config(self, tmp_path):
        _scaffold(tmp_path, "tailwind")
        assert not (tmp_path / "uno.config.ts").exists()


class TestUnoCss:
    def test_it_installs_and_loads_unocss_instead_of_tailwind(self, tmp_path):
        _scaffold(tmp_path, "unocss")
        assert '"unocss"' in _read(tmp_path, "package.json")
        assert "tailwind" not in _read(tmp_path, "package.json")
        assert "UnoCSS()" in _read(tmp_path, "vite.config.ts")
        assert "tailwind" not in _read(tmp_path, "vite.config.ts")

    def test_it_has_a_config_that_maps_the_design_tokens(self, tmp_path):
        _scaffold(tmp_path, "unocss")
        assert "var(--accent)" in _read(tmp_path, "uno.config.ts")

    def test_the_stylesheet_keeps_the_components_without_the_tailwind_directives(self, tmp_path):
        _scaffold(tmp_path, "unocss")
        css = _read(tmp_path, "src/globale.css")
        assert ".btn-primary" in css and ".nx-bento" in css
        assert "@import" not in css and "@theme" not in css and "@custom-variant" not in css

    def test_the_client_entry_loads_the_generated_utilities(self, tmp_path):
        _scaffold(tmp_path, "unocss")
        src = tmp_path / "__nexy__" / "src"
        src.mkdir(parents=True)
        write_main_file(src, set())
        main = (src / "main.ts").read_text(encoding="utf-8")
        # Before the stylesheet, so the project's own base rules come after the reset.
        assert main.index('import "virtual:uno.css"') < main.index('import "/src/globale.css"')


@pytest.mark.parametrize("style", ["vanilla", "other"])
class TestPlainCss:
    def test_no_css_tool_is_installed(self, tmp_path, style):
        _scaffold(tmp_path, style)
        manifest = _read(tmp_path, "package.json") + _read(tmp_path, "vite.config.ts")
        assert "tailwind" not in manifest and "unocss" not in manifest.lower()

    def test_there_is_no_unocss_config(self, tmp_path, style):
        _scaffold(tmp_path, style)
        assert not (tmp_path / "uno.config.ts").exists()

    def test_the_stylesheet_is_plain_css(self, tmp_path, style):
        _scaffold(tmp_path, style)
        css = _read(tmp_path, "src/globale.css")
        assert "@apply" not in css and "@import" not in css and "@theme" not in css

    def test_the_stylesheet_styles_every_class_the_starter_uses(self, tmp_path, style):
        _scaffold(tmp_path, style)
        css = _read(tmp_path, "src/globale.css")
        used = set()
        for page in (tmp_path / "src").rglob("*"):
            if page.is_file() and page.suffix in (".nexy", ".tsx"):
                for value in re.findall(r'(?:class|className)="([^"]+)"', page.read_text("utf-8")):
                    used |= {name for name in value.split() if name.startswith(("nx-", "btn-"))}
        assert used and [name for name in sorted(used) if f".{name}" not in css] == []

    def test_the_theme_variables_are_still_defined(self, tmp_path, style):
        _scaffold(tmp_path, style, framework="vue")
        assert "--accent: #42B883" in _read(tmp_path, "src/globale.css")
