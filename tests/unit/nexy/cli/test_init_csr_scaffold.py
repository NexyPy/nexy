"""Client routing must scaffold a project without a single .nexy file.

``useCSR = True`` hands the views to the framework, so ``nexy init`` cannot
ship the server-rendered ``.nexy`` pages. What replaces them is a framework
route that the client router can mount. For React the root ``layout.tsx`` owns
the HTML document, like Next.js' root layout.
"""

from pathlib import Path

import pytest

from nexy.modules.cli.init.template_setup import _render_local_template


def _scaffold(dest: Path, framework: str, *, use_csr: bool) -> str:
    config = {
        "client_framework": framework,
        "FBRouter": True,
        "project_type": "web",
        "orm": "None",
        "useCSR": use_csr,
    }
    _render_local_template("web-fbr", dest, config, "demo")
    return (dest / "nexyconfig.py").read_text(encoding="utf-8")


def _nexy_files(dest: Path) -> list[str]:
    return sorted(p.relative_to(dest).as_posix() for p in dest.rglob("*.nexy"))


class TestCsrScaffold:
    def test_no_nexy_file_is_generated(self, tmp_path: Path):
        _scaffold(tmp_path, "react", use_csr=True)
        assert _nexy_files(tmp_path) == []

    def test_react_root_layout_owns_the_html_document(self, tmp_path: Path):
        _scaffold(tmp_path, "react", use_csr=True)
        layout = (tmp_path / "src" / "routes" / "layout.tsx").read_text(encoding="utf-8")
        assert "<html" in layout and "<head>" in layout and "<body" in layout
        assert "{children}" in layout
        assert "{%" not in layout and "{{" not in layout.replace("{{ __html", "")

    def test_solid_root_layout_owns_the_document_and_enables_ssr(self, tmp_path: Path):
        _scaffold(tmp_path, "solid", use_csr=True)
        layout = (tmp_path / "src" / "routes" / "layout.tsx").read_text(encoding="utf-8")
        assert "<html" in layout and "props.children" in layout
        assert "className" not in layout and "{%" not in layout
        # Solid must compile for the server too, or Node cannot render the layout.
        assert "solid({ ssr: true })" in (tmp_path / "vite.config.ts").read_text(encoding="utf-8")

    def test_solid_server_mode_keeps_the_default_plugin(self, tmp_path: Path):
        _scaffold(tmp_path, "solid", use_csr=False)
        assert "solid()" in (tmp_path / "vite.config.ts").read_text(encoding="utf-8")

    @pytest.mark.parametrize(
        ("framework", "layout"),
        [("preact", "layout.tsx"), ("vue", "layout.vue"), ("svelte", "layout.svelte")],
    )
    def test_every_framework_gets_a_root_layout_that_owns_the_document(
        self, tmp_path: Path, framework: str, layout: str
    ):
        _scaffold(tmp_path, framework, use_csr=True)
        assert _nexy_files(tmp_path) == []
        source = (tmp_path / "src" / "routes" / layout).read_text(encoding="utf-8")
        assert "<html" in source and "<head>" in source and "<body" in source
        assert "{%" not in source and "{{ " not in source.replace("{{ __html", "")
        assert [p.name for p in (tmp_path / "src" / "routes").glob("layout.*")] == [layout]

    def test_vue_layout_writes_the_theme_script_through_v_html(self, tmp_path: Path):
        # Vue escapes the text of a <script> element, which turns `&&` into `&amp;&amp;`.
        _scaffold(tmp_path, "vue", use_csr=True)
        source = (tmp_path / "src" / "routes" / "layout.vue").read_text(encoding="utf-8")
        assert 'v-html="themeScript"' in source and "inheritAttrs: false" in source

    def test_the_server_mode_scaffold_has_no_framework_layout(self, tmp_path: Path):
        for framework in ("preact", "vue", "svelte"):
            dest = tmp_path / framework
            _scaffold(dest, framework, use_csr=False)
            assert [p.name for p in (dest / "src" / "routes").glob("layout.*")] == ["layout.nexy"]

    def test_route_is_a_fragment_not_a_document(self, tmp_path: Path):
        _scaffold(tmp_path, "react", use_csr=True)
        route = (tmp_path / "src" / "routes" / "index.tsx").read_text(encoding="utf-8")
        assert "<html" not in route and "<body" not in route

    def test_framework_route_is_generated(self, tmp_path: Path):
        _scaffold(tmp_path, "react", use_csr=True)
        assert (tmp_path / "src" / "routes" / "index.tsx").is_file()

    def test_route_has_no_jinja_leftover(self, tmp_path: Path):
        _scaffold(tmp_path, "react", use_csr=True)
        route = (tmp_path / "src" / "routes" / "index.tsx").read_text(encoding="utf-8")
        assert "{%" not in route and "{{" not in route

    def test_config_enables_csr(self, tmp_path: Path):
        config = _scaffold(tmp_path, "react", use_csr=True)
        assert "useCSR = True" in config

    def test_vue_gets_a_vue_route(self, tmp_path: Path):
        _scaffold(tmp_path, "vue", use_csr=True)
        assert (tmp_path / "src" / "routes" / "index.vue").is_file()
        assert not (tmp_path / "src" / "routes" / "index.tsx").exists()

    def test_svelte_gets_a_svelte_route(self, tmp_path: Path):
        _scaffold(tmp_path, "svelte", use_csr=True)
        assert (tmp_path / "src" / "routes" / "index.svelte").is_file()


class TestDefaultScaffold:
    def test_nexy_pages_are_generated(self, tmp_path: Path):
        _scaffold(tmp_path, "react", use_csr=False)
        assert (tmp_path / "src" / "routes" / "index.nexy").is_file()
        assert (tmp_path / "src" / "routes" / "layout.nexy").is_file()

    def test_no_framework_route_is_generated(self, tmp_path: Path):
        _scaffold(tmp_path, "react", use_csr=False)
        assert not (tmp_path / "src" / "routes" / "index.tsx").exists()

    def test_config_does_not_enable_csr(self, tmp_path: Path):
        config = _scaffold(tmp_path, "react", use_csr=False)
        assert "useCSR" not in config

    def test_the_starter_ships_no_demo_component(self, tmp_path: Path):
        _scaffold(tmp_path, "none", use_csr=False)
        assert not (tmp_path / "src" / "components" / "counter").exists()

    def test_layout_owns_the_html_document(self, tmp_path: Path):
        _scaffold(tmp_path, "vue", use_csr=False)
        layout = (tmp_path / "src" / "routes" / "layout.nexy").read_text(encoding="utf-8")
        assert layout.lstrip().split("---")[2].lstrip().startswith("<!DOCTYPE html>")

    def test_layout_keeps_request_time_placeholders(self, tmp_path: Path):
        """layout.nexy is rendered per request, not at scaffold time."""
        _scaffold(tmp_path, "react", use_csr=False)
        layout = (tmp_path / "src" / "routes" / "layout.nexy").read_text(encoding="utf-8")
        assert '<html lang="en"' in layout
        assert "{{children | safe}}" in layout


class TestEveryModeHasTheRightLayout:
    def test_server_mode_has_layout_nexy_with_the_document(self, tmp_path: Path):
        for framework in ("none", "react", "preact", "solid", "vue", "svelte"):
            dest = tmp_path / framework
            _scaffold(dest, framework, use_csr=False)
            text = (dest / "src" / "routes" / "layout.nexy").read_text(encoding="utf-8")
            assert "<!DOCTYPE html>" in text and "{%" not in text
            assert not (dest / "src" / "routes" / "layout.tsx").exists()

    def test_client_mode_never_has_layout_nexy(self, tmp_path: Path):
        for framework in ("react", "preact", "solid", "vue", "svelte"):
            dest = tmp_path / framework
            _scaffold(dest, framework, use_csr=True)
            assert _nexy_files(dest) == []
