"""Route discovery honours useCSR: .nexy files stop being routes."""

from pathlib import Path

from nexy.core.config import Config
from nexy.modules.routers.fbrouter.discovery import RouteDiscovery

_REACT = """
from nexy.frontend import react
"""


def _write(tmp_path: Path, rel: str, content: str = "") -> Path:
    path = tmp_path / "src" / "routes" / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _discover() -> list[str]:
    return sorted(p.name for p in RouteDiscovery().scan())


class TestDiscoveryDefault:
    def test_nexy_page_is_discovered(self, nexy_project, tmp_path):
        nexy_project()
        _write(tmp_path, "index.nexy", "<h1>hi</h1>")
        assert _discover() == ["index.nexy"]

    def test_layout_nexy_is_not_a_route(self, nexy_project, tmp_path):
        nexy_project()
        _write(tmp_path, "layout.nexy", "<html></html>")
        assert _discover() == []


class TestDiscoveryCsr:
    def test_nexy_page_is_skipped(self, nexy_project, tmp_path):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        _write(tmp_path, "index.nexy", "<h1>hi</h1>")
        assert _discover() == []

    def test_framework_page_is_discovered(self, nexy_project, tmp_path):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        _write(tmp_path, "index.tsx", "export default function P() {}")
        assert _discover() == ["index.tsx"]

    def test_mixed_tree_keeps_only_framework_pages(self, nexy_project, tmp_path):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        _write(tmp_path, "index.nexy", "<h1>hi</h1>")
        _write(tmp_path, "about.tsx", "export default function P() {}")
        assert _discover() == ["about.tsx"]

    def test_markdown_pages_stay_available(self, nexy_project, tmp_path):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        _write(tmp_path, "docs.md", "# Docs")
        assert _discover() == ["docs.md"]


class TestDiscoveryCsrWarning:
    def test_ignored_nexy_page_is_reported(self, nexy_project, tmp_path, capsys):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        _write(tmp_path, "index.nexy", "<h1>hi</h1>")
        Config()
        RouteDiscovery().scan()
        assert "useCSR=True" in capsys.readouterr().out
