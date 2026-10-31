"""The docs speak of three routers: the menu shows the routing groups of the one you chose."""

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
            ("fbr", "FBR", "File-based routing"),
            ("modular", "Modular", "Controllers and modules"),
            ("custom", "Custom Router", "Create your own router"),
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
            ("getting-started/installation", "Getting Started"),
            ("routing/fbr/pages", "Routing"),
            ("rendering/ssr", "Rendering"),
            ("routing/modular/dependency-injection", "Routing"),
            ("guides/testing", "Guides"),
            ("reference/cli", "Reference"),
            ("views/react", "React"),
            ("", "Getting Started"),
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


class TestGroupRouter:
    def test_a_group_of_one_router_folder_belongs_to_that_router(self):
        groups = [g for t in source.read_tracks(DOCS) for g in t.groups]
        assert {"fbr", "modular", "custom"} <= {g.router for g in groups}

    def test_every_page_of_a_router_group_is_of_that_router(self):
        groups = [g for t in source.read_tracks(DOCS) for g in t.groups if g.router]
        assert all(p.router == g.router for g in groups for p in g.pages)

    def test_a_group_of_shared_pages_belongs_to_no_router(self):
        group = source.group_of(source.read_tracks(DOCS), "guides/actions")
        assert group.router is None

    def test_the_pager_never_crosses_into_another_router(self):
        tracks = source.read_tracks(DOCS)
        for track in tracks:
            for page in source.pages_of(track):
                near = [p for p in source.neighbours(track, page.slug) if p]
                assert {p.router for p in near} <= {None, page.router}, page.slug


class TestVanillaMenu:
    @pytest.fixture(scope="class")
    def out(self, tmp_path_factory):
        out = tmp_path_factory.mktemp("site")
        build.build(out, DOCS)
        return out

    def _html(self, out, slug):
        return (out / "docs" / slug / "index.html").read_text(encoding="utf-8")

    def test_the_menu_of_a_page_holds_every_section(self, out):
        html = self._html(out, "routing/modular")
        expected = [group.title for track in source.read_tracks(DOCS) for group in track.groups]
        actual = re.findall(r'<details class="group" data-section="([^"]+)"', html)
        assert actual == expected

    def test_the_routing_groups_carry_their_router(self, out):
        html = self._html(out, "guides/actions")
        assert all(f'data-router="{key}"' in html for key, _name, _blurb in source.ROUTERS)

    def test_the_selector_names_every_router(self, out):
        html = self._html(out, "guides/actions")
        assert all(f"<b>{name}</b>" in html for _key, name, _blurb in source.ROUTERS)

    def test_every_choice_of_the_selector_has_an_icon(self, out):
        html = self._html(out, "guides/actions")
        assert html.count('class="area-icon"') == 2 * len(source.ROUTERS)

    def test_the_selector_marks_the_router_of_the_page(self, out):
        html = self._html(out, "routing/modular")
        assert 'data-pick="modular" aria-current="true"' in html

    def test_a_router_page_tells_its_router_before_the_first_paint(self, out):
        html = self._html(out, "routing/modular")
        assert '<meta name="nexy-router" content="modular">' in html

    def test_a_shared_page_names_no_router(self, out):
        assert '<meta name="nexy-router"' not in self._html(out, "guides/actions")

    def test_only_the_section_of_the_page_is_open(self, out):
        html = self._html(out, "guides/actions")
        assert len(re.findall(r'<details class="group"[^>]* open>', html)) == 1

    def test_the_sections_do_not_close_each_other(self, out):
        """No exclusive accordion: opening a folder never hides the folder of the current page."""
        html = self._html(out, "guides/actions")
        assert 'name="nav"' not in html

    def test_the_pager_stays_inside_the_router(self, out):
        html = self._html(out, "routing/modular")
        assert "/fbr/" not in html.split('class="pager"')[1]


class TestAssets:
    def test_the_menu_can_fold_away(self):
        script = (VANILLA / "assets" / "site.js").read_text(encoding="utf-8")
        assert "nexy-docs-side" in script

    def test_the_panel_scrolls_inside_on_a_wide_screen(self):
        css = (VANILLA / "assets" / "style.css").read_text(encoding="utf-8")
        assert "html, body { height: 100%; overflow: hidden; }" in css

    def test_the_router_choice_is_kept(self):
        script = (VANILLA / "assets" / "site.js").read_text(encoding="utf-8")
        assert "nexy-docs-router" in script

    def test_the_routers_not_chosen_are_not_drawn(self):
        css = (VANILLA / "assets" / "style.css").read_text(encoding="utf-8")
        assert all(
            f'html[data-router="{key}"] .side [data-router]:not([data-router="{key}"])' in css
            for key, _name, _blurb in source.ROUTERS
        )

    def test_the_menu_filter_is_wired(self):
        script = (VANILLA / "assets" / "site.js").read_text(encoding="utf-8")
        assert ".side-filter input" in script

    def test_the_folder_holding_the_page_is_marked(self):
        css = (VANILLA / "assets" / "style.css").read_text(encoding="utf-8")
        assert ':has(a[aria-current="page"])' in css
