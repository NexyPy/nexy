"""The docs speak of two routers, like Next.js speaks of two: the menu shows the one you chose."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from sites.shared import docs_source as source
from sites.vanilla import build

DOCS = Path(__file__).resolve().parents[3] / "docs"
ROOT = DOCS.parent
VANILLA = ROOT / "sites" / "vanilla"


class TestRouterOfAPage:
    @pytest.mark.parametrize(
        ("slug", "router"),
        [
            ("routing/fbr", "fbr"),
            ("routing/fbr/pages/dynamic-routes", "fbr"),
            ("routing/modular", "modular"),
            ("routing/modular/guards-and-metadata", "modular"),
            ("routing", None),
            ("guides/actions", None),
            ("routing/fbrx", None),
            ("", None),
        ],
    )
    def test_it_comes_from_the_folder_of_the_page(self, slug, router):
        assert source.router_of(slug) == router

    def test_the_two_routers_are_named_for_the_selector(self):
        assert source.ROUTERS == (("fbr", "File-based"), ("modular", "Modular"))

    def test_every_page_of_a_router_folder_knows_its_router(self):
        pages = [p for s in source.read_sections(DOCS) for p in s.pages]
        wrong = [p.slug for p in pages if p.router != source.router_of(p.slug)]
        assert wrong == []

    def test_the_menu_holds_pages_of_both_routers(self):
        routers = {p.router for s in source.read_sections(DOCS) for p in s.pages}
        assert {"fbr", "modular", None} <= routers


class TestVanillaMenu:
    @pytest.fixture(scope="class")
    def out(self, tmp_path_factory):
        target = tmp_path_factory.mktemp("routers")
        build.build(target)
        return target

    @staticmethod
    def _read(out: Path, slug: str) -> str:
        return (out / "docs" / slug / "index.html").read_text(encoding="utf-8")

    def test_a_page_of_one_router_is_marked_in_the_menu(self, out):
        html = self._read(out, "guides/actions")
        assert re.search(r'<li data-router="fbr"><a href="[^"]+">Pages</a></li>', html)

    def test_a_page_of_the_other_router_is_marked_too(self, out):
        html = self._read(out, "guides/actions")
        assert re.search(r'<li data-router="modular"><a href="[^"]+">Guards and metadata</a>', html)

    def test_a_page_of_neither_router_is_never_hidden(self, out):
        html = self._read(out, "guides/actions")
        assert re.search(r'<li><a href="[^"]+" aria-current="page">Actions</a></li>', html)

    def test_a_modular_page_declares_its_router(self, out):
        html = self._read(out, "routing/modular/dependency-injection")
        assert '<meta name="nexy-router" content="modular">' in html

    def test_a_file_based_page_declares_its_router(self, out):
        assert '<meta name="nexy-router" content="fbr">' in self._read(out, "routing/fbr/pages")

    def test_a_page_of_neither_router_declares_none(self, out):
        assert '<meta name="nexy-router"' not in self._read(out, "guides/actions")

    def test_the_menu_offers_both_routers(self, out):
        html = self._read(out, "guides/actions")
        buttons = re.findall(r'<button type="button" data-router="(\w+)" data-home="([^"]+)"', html)
        assert [name for name, _ in buttons] == ["fbr", "modular"]

    def test_each_choice_leads_to_the_overview_of_its_router(self, out):
        page = out / "docs" / "guides" / "actions"
        html = (page / "index.html").read_text(encoding="utf-8")
        homes = re.findall(r'data-home="([^"]+)"', html)
        assert homes and all((page / home / "index.html").resolve().is_file() for home in homes)

    def test_the_router_is_set_before_the_first_paint(self, out):
        head = self._read(out, "guides/actions").split("</head>")[0]
        assert "dataset.router" in head and "nexy-docs-router" in head


class TestAssets:
    def test_the_stylesheet_hides_the_pages_of_the_other_router(self):
        css = (VANILLA / "assets" / "style.css").read_text(encoding="utf-8")
        assert 'html[data-router="fbr"] .side li[data-router="modular"]' in css

    def test_the_stylesheet_never_hides_the_choice_itself(self):
        css = (VANILLA / "assets" / "style.css").read_text(encoding="utf-8")
        assert '.side [data-router="modular"]' not in css

    def test_the_script_remembers_the_choice_and_follows_a_router_page(self):
        script = (VANILLA / "assets" / "site.js").read_text(encoding="utf-8")
        assert "router-switch" in script and "nexy-docs-router" in script
