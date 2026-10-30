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
            ("routing/custom", "custom"),
            ("routing", None),
            ("guides/actions", None),
            ("routing/fbrx", None),
            ("", None),
        ],
    )
    def test_it_comes_from_the_folder_of_the_page(self, slug, router):
        assert source.router_of(slug) == router

    def test_the_routers_are_named_for_the_selector(self):
        assert source.ROUTERS == (
            ("fbr", "File-based"),
            ("modular", "Modular"),
            ("custom", "Custom"),
        )

    def test_every_page_of_a_router_folder_knows_its_router(self):
        pages = [p for t in source.read_tracks(DOCS) for p in source.pages_of(t)]
        wrong = [p.slug for p in pages if p.router != source.router_of(p.slug)]
        assert wrong == []

    def test_the_menu_holds_pages_of_both_routers(self):
        routers = {p.router for t in source.read_tracks(DOCS) for p in source.pages_of(t)}
        assert {"fbr", "modular", "custom", None} <= routers


class TestTracks:
    @pytest.mark.parametrize(
        ("slug", "track"),
        [
            ("getting-started/installation", "Start here"),
            ("routing/fbr/pages", "Build"),
            ("rendering/ssr", "Choose your stack"),
            ("routing/modular/dependency-injection", "Advanced"),
            ("guides/testing", "Guides"),
            ("reference/cli", "Reference"),
            ("", "Start here"),
        ],
    )
    def test_a_page_belongs_to_the_track_that_holds_it(self, slug, track):
        assert source.track_of(source.read_tracks(DOCS), slug).label == track

    def test_every_page_is_in_the_menu_of_exactly_one_track(self):
        tracks = source.read_tracks(DOCS)
        listed = [p.slug for t in tracks for p in source.pages_of(t)]
        every = [source.slug_of(p.relative_to(DOCS).as_posix()) for p in DOCS.rglob("*.md")]
        assert sorted(listed) == sorted(slug for slug in every if slug)

    def test_a_track_menu_never_holds_an_empty_group(self):
        tracks = source.read_tracks(DOCS)
        assert all(group.pages for track in tracks for group in track.groups)


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

    def test_the_selector_names_every_track(self, out):
        html = self._html(out, "guides/actions")
        assert all(f"<b>{track.label}</b>" in html for track in source.read_tracks(DOCS))

    def test_every_choice_of_the_selector_has_an_icon(self, out):
        html = self._html(out, "guides/actions")
        assert html.count('class="area-icon"') == len(source.read_tracks(DOCS)) + 1

    def test_the_selector_marks_the_track_of_the_page(self, out):
        html = self._html(out, "reference/cli")
        assert re.search(
            r'aria-current="true"><span class="area-icon">.*?<b>Reference</b>', html, re.S
        )

    def test_only_the_section_of_the_page_is_open(self, out):
        html = self._html(out, "guides/actions")
        assert len(re.findall(r'<details class="group"[^>]* open>', html)) == 1

    def test_the_sections_do_not_close_each_other(self, out):
        """No exclusive accordion: opening a folder never hides the folder of the current page."""
        html = self._html(out, "guides/actions")
        assert 'name="nav"' not in html

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

    def test_the_menu_filter_is_wired(self):
        script = (VANILLA / "assets" / "site.js").read_text(encoding="utf-8")
        assert ".side-filter input" in script

    def test_the_folder_holding_the_page_is_marked(self):
        css = (VANILLA / "assets" / "style.css").read_text(encoding="utf-8")
        assert ':has(a[aria-current="page"])' in css
