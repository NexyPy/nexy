"""The home page of the docs: an introduction, then one card per Getting Started page."""

from __future__ import annotations

import re
from pathlib import Path

from sites.shared import docs_source as source
from sites.shared import home

ROOT = Path(__file__).resolve().parents[3]
DOCS = ROOT / "docs"
STYLE = ROOT / "sites" / "vanilla" / "assets" / "style.css"


def _link(slug: str) -> str:
    return f"/docs/{slug}"


def _rendered() -> source.Rendered:
    return home.render(DOCS, _link)


class TestCards:
    def test_the_home_shows_the_nine_pages_of_getting_started(self):
        assert _rendered().html.count('class="home-card"') == 9

    def test_a_card_leads_to_a_page_of_getting_started(self):
        slugs = {_link(page.slug) for page in source.pages_of(source.read_tracks(DOCS)[0])}
        hrefs = re.findall(r'class="home-card" href="([^"]+)"', _rendered().html)
        assert set(hrefs) <= slugs

    def test_every_page_of_getting_started_has_its_card(self):
        track = source.read_tracks(DOCS)[0]
        slugs = {_link(page.slug) for page in source.pages_of(track)}
        hrefs = set(re.findall(r'class="home-card" href="([^"]+)"', _rendered().html))
        assert hrefs == slugs

    def test_a_card_stacks_a_picture_a_title_and_a_line(self):
        card = re.search(r'<a class="home-card".*?</a>', _rendered().html, re.S)[0]
        assert card.index("home-card-art") < card.index("home-card-title")
        assert card.index("home-card-title") < card.index("home-card-text")

    def test_a_card_carries_its_summary(self):
        card = re.search(
            r'<a class="home-card" href="/docs/getting-started/installation"[^>]*>(.*?)</a>',
            _rendered().html,
            re.S,
        )[1]
        assert '<span class="home-card-title">Installation</span>' in card
        assert "Install uv and the Nexy CLI" in card

    def test_a_card_draws_a_picture(self):
        card = re.search(r'<a class="home-card".*?</a>', _rendered().html, re.S)[0]
        assert "<svg" in card.split("home-card-art", 1)[1]


class TestIntroduction:
    def test_the_page_opens_with_the_words_of_the_readme(self):
        assert "<h1" in _rendered().html and "A Python framework for fullstack" in _rendered().html

    def test_the_first_path_comes_first(self):
        html = _rendered().html
        assert html.index("A Python framework") < html.index('class="home-card"')

    def test_the_outline_lists_the_groups_of_getting_started(self):
        track = source.read_tracks(DOCS)[0]
        groups = [group.title for group in track.groups]
        assert [heading.text for heading in _rendered().headings] == groups

    def test_a_group_opens_its_block_of_cards(self):
        html = _rendered().html
        assert re.search(
            r'<h2 id="first-steps" data-group="first-steps">First steps</h2>'
            r'<div class="home-cards">',
            html,
        )


class TestOnlyGettingStarted:
    def test_a_later_track_stays_out_of_the_cards(self, tmp_path):
        (tmp_path / "getting-started").mkdir()
        (tmp_path / "getting-started" / "install.md").write_text("# Install", encoding="utf-8")
        (tmp_path / "routing").mkdir()
        (tmp_path / "routing" / "fbr.md").write_text("# FBR", encoding="utf-8")
        (tmp_path / "README.md").write_text(
            "# Docs\n\nWelcome.\n\n## Getting Started\n\n### First steps\n"
            "| Page | What you will do |\n|---|---|\n"
            "| [Install](getting-started/install.md) | Install it |\n\n"
            "## Routing\n\n### FBR\n| Page | What you will do |\n|---|---|\n"
            "| [FBR](routing/fbr.md) | Route it |\n",
            encoding="utf-8",
        )
        html = home.render(tmp_path, _link).html
        assert "Welcome." in html
        assert 'href="/docs/getting-started/install"' in html
        assert 'href="/docs/routing/fbr"' not in html


class TestStyle:
    def test_the_cards_stand_in_two_columns(self):
        css = STYLE.read_text(encoding="utf-8")
        assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in css

    def test_one_column_when_the_screen_is_narrow(self):
        css = STYLE.read_text(encoding="utf-8")
        assert re.search(
            r"@media \(max-width: 720px\) \{\s*\.home-cards \{ grid-template-columns: 1fr; \}", css
        )

    def test_a_card_has_a_dot_pattern_background(self):
        css = STYLE.read_text(encoding="utf-8")
        block = css.split(".home-card::before", 1)[1].split("}", 1)[0]
        assert "radial-gradient" in block and "background-size: 16px 16px" in block

    def test_the_old_table_cards_are_gone(self):
        css = STYLE.read_text(encoding="utf-8")
        assert ".doc.home .table-wrap" not in css


class TestLanguage:
    def test_the_home_of_a_language_reads_its_translated_introduction(self):
        intro = source.home(DOCS, "fr").path.read_text(encoding="utf-8").split("\n", 1)[0][2:]
        assert intro in home.render(DOCS, _link, "fr").html

    def test_the_cards_of_a_language_name_its_translated_pages(self):
        first = source.read_tracks(DOCS, "fr")[0].groups[0].pages[0]
        assert first.label in home.render(DOCS, _link, "fr").html
