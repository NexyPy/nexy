"""Client routing must scaffold a project without a single .nexy file.

``useCSR = True`` hands the views to the framework, so ``nexy init`` cannot
ship the server-rendered ``.nexy`` pages. What replaces them is a framework
route that the client router can mount.
"""

from pathlib import Path

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

    def test_framework_route_is_generated(self, tmp_path: Path):
        _scaffold(tmp_path, "react", use_csr=True)
        assert (tmp_path / "src" / "routes" / "index.tsx").is_file()

    def test_route_imports_the_client_component(self, tmp_path: Path):
        _scaffold(tmp_path, "react", use_csr=True)
        route = (tmp_path / "src" / "routes" / "index.tsx").read_text(encoding="utf-8")
        assert 'from "@/components/card.tsx"' in route

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

    def test_vanilla_components_are_kept(self, tmp_path: Path):
        _scaffold(tmp_path, "none", use_csr=False)
        assert (tmp_path / "src" / "components" / "card.nexy").is_file()

    def test_layout_keeps_request_time_placeholders(self, tmp_path: Path):
        """layout.nexy is rendered per request, not at scaffold time."""
        _scaffold(tmp_path, "react", use_csr=False)
        layout = (tmp_path / "src" / "routes" / "layout.nexy").read_text(encoding="utf-8")
        assert 'lang="{{ locale }}"' in layout
        assert "{{children | safe}}" in layout
