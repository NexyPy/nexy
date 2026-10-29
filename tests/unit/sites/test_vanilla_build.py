"""The vanilla site is plain files: every page exists, every link resolves, search finds each."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from sites.shared import docs_source
from sites.vanilla import build

DOCS = Path(__file__).resolve().parents[3] / "docs"


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory) -> Path:
    target = tmp_path_factory.mktemp("vanilla")
    build.build(target)
    return target


def _pages(out: Path) -> list[Path]:
    return sorted((out / "docs").rglob("index.html"))


class TestPages:
    def test_every_doc_has_a_page(self, out):
        sections = docs_source.read_sections(DOCS)
        slugs = {p.slug for s in sections for p in s.pages} | {""}
        found = {p.parent.relative_to(out / "docs").as_posix() for p in _pages(out)} - {"."}
        found.add("")
        assert found == slugs

    def test_the_root_sends_visitors_to_the_docs(self, out):
        assert 'url=docs/"' in (out / "index.html").read_text(encoding="utf-8")

    def test_github_pages_does_not_run_jekyll(self, out):
        assert (out / ".nojekyll").is_file()

    def test_the_assets_are_copied(self, out):
        assert all((out / "assets" / name).is_file() for name in ("style.css", "site.js"))


class TestLinks:
    @staticmethod
    def _internal(html: str) -> list[str]:
        links = re.findall(r'(?:href|src)="([^"]+)"', html)
        return [x for x in links if not re.match(r"([a-z]+:|#|mailto)", x)]

    def test_every_relative_link_resolves_to_a_file(self, out):
        broken = []
        for page in _pages(out):
            for href in self._internal(page.read_text(encoding="utf-8")):
                target = (page.parent / href.split("#")[0].split("?")[0]).resolve()
                if target.is_dir():
                    target /= "index.html"
                if not target.is_file():
                    broken.append(f"{page.relative_to(out)} -> {href}")
        assert broken == []

    def test_no_link_is_absolute_so_a_project_site_works(self, out):
        html = (out / "docs" / "guides" / "actions" / "index.html").read_text(encoding="utf-8")
        assert not re.search(r'(?:href|src)="/(?!/)', html)


class TestPageContent:
    @pytest.fixture(scope="class")
    def html(self, out):
        return (out / "docs" / "guides" / "actions" / "index.html").read_text(encoding="utf-8")

    def test_the_title_is_the_page_title(self, html):
        assert "<title>Actions - Nexy</title>" in html

    def test_the_menu_marks_the_current_page(self, html):
        assert re.search(r'<a [^>]*aria-current="page"[^>]*>Actions</a>', html)

    def test_the_outline_lists_the_headings(self, html):
        assert 'href="#define-an-action"' in html

    def test_the_pager_names_the_neighbours(self, html):
        assert 'class="pager"' in html

    def test_the_menu_is_made_of_collapsible_sections(self, html):
        assert '<details class="group" data-section="Guides" open>' in html

    def test_a_section_says_how_many_pages_it_holds(self, html):
        pattern = r'<span class="group-name">Guides</span>.*?<span class="group-count">8</span>'
        assert re.search(pattern, html)

    def test_the_menu_has_a_search_button(self, html):
        assert 'class="search-open"' in html

    def test_the_first_page_has_no_previous_link(self, out):
        html = (out / "docs" / "index.html").read_text(encoding="utf-8")
        assert 'rel="prev"' not in html

    def test_titles_are_escaped(self):
        assert build.escape('<b>"x"</b>') == "&lt;b&gt;&quot;x&quot;&lt;/b&gt;"


class TestUsability:
    @pytest.fixture(scope="class")
    def html(self, out):
        return (out / "docs" / "guides" / "actions" / "index.html").read_text(encoding="utf-8")

    def test_the_keyboard_can_skip_the_menu(self, html):
        assert 'class="skip" href="#content"' in html and 'id="content"' in html

    def test_the_page_says_which_colour_the_browser_bar_takes(self, html):
        assert 'name="theme-color"' in html

    def test_code_is_coloured_without_javascript(self, html):
        assert 'class="tok-' in html

    def test_a_wrong_address_gets_a_page_that_still_has_its_style(self, tmp_path):
        build.build(tmp_path, base="/nexy")
        page = (tmp_path / "404.html").read_text(encoding="utf-8")
        assert 'href="/nexy/assets/style.css"' in page and 'href="/nexy/docs/"' in page

    def test_the_base_may_be_empty_for_a_site_at_the_root_of_a_domain(self, tmp_path):
        build.build(tmp_path, base="")
        assert 'href="/assets/style.css"' in (tmp_path / "404.html").read_text(encoding="utf-8")

    def test_the_base_is_normalised(self):
        assert [build.base_of(x) for x in ("", "/", "nexy", "/nexy", "/nexy/")] == [
            "/",
            "/",
            "/nexy/",
            "/nexy/",
            "/nexy/",
        ]


class TestSearch:
    @pytest.fixture(scope="class")
    def index(self, out):
        return json.loads((out / "search-index.json").read_text(encoding="utf-8"))

    def test_every_page_is_searchable(self, out, index):
        assert len(index) == len(_pages(out))

    def test_an_entry_says_where_it_is(self, index):
        entry = next(e for e in index if e["title"] == "Actions")
        assert entry["url"] == "docs/guides/actions/"

    def test_an_entry_carries_text_but_no_markup(self, index):
        assert all("<" not in e["text"] for e in index)
