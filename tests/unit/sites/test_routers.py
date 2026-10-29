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


class TestAreas:
    @pytest.mark.parametrize(
        ("slug", "area"),
        [
            ("routing/fbr/pages", "fbr"),
            ("routing/modular/dependency-injection", "modular"),
            ("reference/cli", "cli"),
            ("deployment/performance", "cli"),
            ("reference/config", "core"),
            ("getting-started/how-nexy-works", "core"),
            ("guides/actions", "nexy"),
            ("routing", "nexy"),
            ("", "nexy"),
        ],
    )
    def test_a_page_belongs_to_the_area_of_its_slug(self, slug, area):
        assert source.area_of(slug) == area

    def test_every_page_is_in_the_menu_of_one_area(self):
        sections = source.read_sections(DOCS)
        listed = [
            p.slug for a in source.AREAS for s in source.in_area(sections, a.slug) for p in s.pages
        ]
        assert sorted(listed) == sorted(p.slug for s in sections for p in s.pages)

    def test_an_area_menu_never_holds_an_empty_section(self):
        sections = source.read_sections(DOCS)
        assert all(s.pages for a in source.AREAS for s in source.in_area(sections, a.slug))


class TestVanillaMenu:
    @pytest.fixture(scope="class")
    def out(self, tmp_path_factory):
        out = tmp_path_factory.mktemp("site")
        build.build(out, DOCS)
        return out

    def _html(self, out, slug):
        return (out / "docs" / slug / "index.html").read_text(encoding="utf-8")

    def test_the_menu_of_a_page_holds_only_its_area(self, out):
        html = self._html(out, "routing/modular")
        assert "Dependency injection" in html and "Dynamic routes" not in html

    def test_the_selector_names_every_area(self, out):
        html = self._html(out, "guides/actions")
        assert all(f"<b>{a.label}</b>" in html for a in source.AREAS)

    def test_the_selector_marks_the_area_of_the_page(self, out):
        html = self._html(out, "reference/cli")
        assert re.search(
            r'aria-current="true"><span class="area-icon">.*?<b>Nexy CLI</b>', html, re.S
        )

    def test_only_the_section_of_the_page_is_open(self, out):
        html = self._html(out, "guides/actions")
        assert len(re.findall(r'<details class="group"[^>]* open>', html)) == 1

    def test_the_sections_are_one_accordion(self, out):
        html = self._html(out, "guides/actions")
        assert 'name="nav"' in html

    def test_the_pager_stays_inside_the_area(self, out):
        html = self._html(out, "routing/modular")
        assert "Quick start" not in html.split('class="pager"')[1]


class TestAssets:
    def test_the_menu_can_fold_away(self):
        script = (VANILLA / "assets" / "site.js").read_text(encoding="utf-8")
        assert "nexy-docs-side" in script

    def test_the_panel_scrolls_inside_on_a_wide_screen(self):
        css = (VANILLA / "assets" / "style.css").read_text(encoding="utf-8")
        assert "html, body { height: 100%; overflow: hidden; }" in css
