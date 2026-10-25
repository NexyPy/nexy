"""The theme button and the current-link mark belong to the project, not to the framework runtime."""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.modules.cli.init.template_setup import _render_local_template
from nexy.modules.frontend.vite_entry import write_main_file

CSR = [("react", "tsx"), ("preact", "tsx"), ("solid", "tsx"), ("vue", "vue"), ("svelte", "svelte")]


def _scaffold(dest: Path, framework: str, use_csr: bool) -> Path:
    config = {
        "client_framework": framework,
        "FBRouter": True,
        "project_type": "web",
        "orm": "None",
        "useCSR": use_csr,
    }
    _render_local_template("web-fbr", dest, config, "demo")
    return dest


@pytest.mark.parametrize(("framework", "ext"), CSR)
class TestClientRouted:
    def test_the_theme_toggle_is_a_component_of_the_project(self, tmp_path, framework, ext):
        _scaffold(tmp_path, framework, True)
        component = tmp_path / "src" / "components" / f"theme-toggle.{ext}"
        assert 'localStorage.setItem("nexy-theme"' in component.read_text(encoding="utf-8")

    def test_the_layout_uses_it(self, tmp_path, framework, ext):
        _scaffold(tmp_path, framework, True)
        layout = next((tmp_path / "src" / "routes").glob("layout.*"))
        text = layout.read_text(encoding="utf-8")
        assert f"theme-toggle.{ext}" in text and "<ThemeToggle" in text

    def test_no_jinja_is_left_in_the_component(self, tmp_path, framework, ext):
        _scaffold(tmp_path, framework, True)
        component = tmp_path / "src" / "components" / f"theme-toggle.{ext}"
        assert "{%" not in component.read_text(encoding="utf-8")


@pytest.mark.parametrize("framework", ["none", "react", "vue"])
class TestServerRendered:
    def test_no_framework_component_is_shipped_for_the_toggle(self, tmp_path, framework):
        _scaffold(tmp_path, framework, False)
        assert list((tmp_path / "src" / "components").glob("theme-toggle.*")) == []

    def test_the_header_component_carries_its_own_script(self, tmp_path, framework):
        _scaffold(tmp_path, framework, False)
        header = (tmp_path / "src" / "components" / "header.nexy").read_text(encoding="utf-8")
        assert "data-theme-toggle" in header and "aria-current" in header


def test_the_generated_entry_has_no_ui_runtime(tmp_path):
    src = tmp_path / "__nexy__" / "src"
    src.mkdir(parents=True)
    write_main_file(src, set())
    main = (src / "main.ts").read_text(encoding="utf-8")
    assert "startUi" not in main and "ui.ts" not in main
