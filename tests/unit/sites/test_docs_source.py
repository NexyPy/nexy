"""The documentation sites read docs/ through one module, so none of them can drift."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from sites.shared import docs_source as source

DOCS = Path(__file__).resolve().parents[3] / "docs"


def _link(slug: str) -> str:
    return f"/docs/{slug}" if slug else "/docs"


@pytest.fixture(scope="module")
def sections():
    return source.read_sections(DOCS)


class TestSlug:
    def test_a_page_loses_its_extension(self):
        assert source.slug_of("guides/actions.md") == "guides/actions"

    def test_a_folder_index_is_the_folder(self):
        assert source.slug_of("routing/fbr/README.md") == "routing/fbr"

    def test_the_root_index_is_empty(self):
        assert source.slug_of("README.md") == ""


class TestSections:
    def test_the_first_section_is_getting_started(self, sections):
        assert sections[0].title == "Getting started"

    def test_every_page_is_in_the_menu_once(self, sections):
        listed = sorted(page.slug for section in sections for page in section.pages)
        every = sorted(source.slug_of(p.relative_to(DOCS).as_posix()) for p in DOCS.rglob("*.md"))
        assert listed == [slug for slug in every if slug]

    def test_a_page_has_the_title_of_its_heading(self, sections):
        page = source.find(sections, "guides/actions")
        assert page is not None and page.title == "Actions"

    def test_an_unknown_page_is_not_found(self, sections):
        assert source.find(sections, "nope/nothing") is None


class TestNeighbours:
    def test_the_first_page_has_no_previous(self, sections):
        first = sections[0].pages[0].slug
        assert source.neighbours(sections, first)[0] is None

    def test_the_next_page_follows_the_menu(self, sections):
        first, second = sections[0].pages[0], sections[0].pages[1]
        assert source.neighbours(sections, first.slug)[1] == second

    def test_the_last_page_has_no_next(self, sections):
        last = sections[-1].pages[-1].slug
        assert source.neighbours(sections, last)[1] is None


class TestRender:
    @staticmethod
    def _html(tmp_path: Path, text: str, name: str = "guides/page.md") -> str:
        (tmp_path / "guides").mkdir(exist_ok=True)
        (tmp_path / "guides" / "actions.md").write_text("# A", encoding="utf-8")
        path = tmp_path / name
        path.write_text(text, encoding="utf-8")
        return source.render(path, tmp_path, _link).html

    def test_a_link_to_another_page_becomes_its_url(self, tmp_path):
        assert 'href="/docs/guides/actions#x"' in self._html(tmp_path, "[a](actions.md#x)")

    def test_a_link_up_a_folder_is_resolved(self, tmp_path):
        (tmp_path / "top.md").write_text("# T", encoding="utf-8")
        assert 'href="/docs/top"' in self._html(tmp_path, "[t](../top.md)")

    def test_a_link_outside_docs_goes_to_the_repository(self, tmp_path):
        html = self._html(tmp_path, "[c](../../CHANGELOG.md)")
        assert 'href="https://github.com/NexyPy/nexy/blob/main/CHANGELOG.md"' in html

    def test_a_file_that_is_not_markdown_outside_docs_goes_to_the_repository(self, tmp_path):
        html = self._html(tmp_path, "[l](../../llms.txt)")
        assert 'href="https://github.com/NexyPy/nexy/blob/main/llms.txt"' in html

    def test_an_external_link_is_left_alone(self, tmp_path):
        assert 'href="https://example.com/x"' in self._html(tmp_path, "[e](https://example.com/x)")

    def test_a_heading_gets_a_github_style_id(self, tmp_path):
        assert '<h2 id="what-to-assert">' in self._html(tmp_path, "## What to assert\n")

    def test_two_equal_headings_get_distinct_ids(self, tmp_path):
        html = self._html(tmp_path, "## Same\n\n## Same\n")
        assert 'id="same"' in html and 'id="same-1"' in html

    def test_a_file_name_becomes_a_caption(self, tmp_path):
        html = self._html(tmp_path, '```python filename="src/a.py"\nx = 1\n```\n')
        assert "<figcaption>src/a.py</figcaption>" in html

    def test_a_block_without_a_name_has_no_caption(self, tmp_path):
        assert "figcaption" not in self._html(tmp_path, "```python\nx = 1\n```\n")

    def test_the_language_of_a_block_is_kept(self, tmp_path):
        html = self._html(tmp_path, '```python filename="a.py"\nx = 1\n```\n')
        assert 'lang="python"' in html

    def test_the_headings_are_listed_for_the_outline(self, tmp_path):
        (tmp_path / "guides").mkdir()
        path = tmp_path / "guides" / "p.md"
        path.write_text("# T\n\n## One\n\n### Two\n", encoding="utf-8")
        found = source.render(path, tmp_path, _link).headings
        assert [(h.level, h.id) for h in found] == [(2, "one"), (3, "two")]


class TestHighlight:
    @staticmethod
    def _html(tmp_path: Path, fence: str, code: str) -> str:
        path = tmp_path / "p.md"
        path.write_text(f"```{fence}\n{code}\n```\n", encoding="utf-8")
        return source.render(path, tmp_path, _link).html

    def test_a_python_keyword_gets_a_token_class(self, tmp_path):
        html = self._html(tmp_path, "python", "def run(): pass")
        assert '<span class="tok-k">def</span>' in html

    def test_the_text_of_the_code_is_unchanged(self, tmp_path):
        html = self._html(tmp_path, "python", "x = 1 < 2 and 'a'")
        text = re.sub(r"<[^>]+>", "", html)
        assert "x = 1 &lt; 2 and &#x27;a&#x27;" in text or "x = 1 &lt; 2 and 'a'" in text

    def test_a_nexy_file_is_coloured_as_a_template(self, tmp_path):
        html = self._html(tmp_path, "nexy", "<h1>{{ title }}</h1>")
        assert 'class="tok-' in html

    def test_an_unknown_language_stays_plain(self, tmp_path):
        assert "tok-" not in self._html(tmp_path, "klingon", "qapla")

    def test_a_block_without_a_language_stays_plain(self, tmp_path):
        assert "tok-" not in self._html(tmp_path, "", "def run(): pass")

    def test_a_named_block_is_coloured_too(self, tmp_path):
        html = self._html(tmp_path, 'python filename="a.py"', "def run(): pass")
        assert "<figcaption>a.py</figcaption>" in html and "tok-k" in html


class TestAnchors:
    def test_a_heading_has_a_link_to_itself(self, tmp_path):
        path = tmp_path / "p.md"
        path.write_text("# T\n\n## One\n", encoding="utf-8")
        html = source.render(path, tmp_path, _link).html
        assert '<a class="anchor" href="#one"' in html

    def test_the_anchor_adds_no_text_to_the_outline_or_to_search(self, tmp_path):
        path = tmp_path / "p.md"
        path.write_text("# T\n\n## One\n", encoding="utf-8")
        rendered = source.render(path, tmp_path, _link)
        assert rendered.headings[0].text == "One" and source.plain(rendered.html) == "T One"


class TestSearchEntry:
    @staticmethod
    def _entry(tmp_path: Path) -> dict[str, str]:
        path = tmp_path / "p.md"
        path.write_text("# Title\n\nSome **bold** words.\n\n## Part\n", encoding="utf-8")
        page = source.Page("p", "Title", "Title", path)
        rendered = source.render(path, tmp_path, _link)
        return source.search_entry(page, "Guides", rendered, "docs/p")

    def test_it_names_the_page_and_where_it_is(self, tmp_path):
        entry = self._entry(tmp_path)
        assert (entry["title"], entry["section"], entry["url"]) == ("Title", "Guides", "docs/p")

    def test_it_carries_the_text_without_markup(self, tmp_path):
        assert self._entry(tmp_path)["text"] == "Title Some bold words. Part"

    def test_it_lists_the_headings(self, tmp_path):
        assert self._entry(tmp_path)["headings"] == "Part"

    def test_the_text_is_cut_to_a_size_a_browser_can_search_quickly(self, tmp_path):
        path = tmp_path / "long.md"
        path.write_text("# T\n\n" + "word " * 5000, encoding="utf-8")
        page = source.Page("long", "T", "T", path)
        entry = source.search_entry(page, "S", source.render(path, tmp_path, _link), "docs/long")
        assert len(entry["text"]) == source.TEXT_LENGTH


class TestRealDocs:
    def test_every_page_renders(self, sections):
        pages = [page for section in sections for page in section.pages]
        assert all(source.render(page.path, DOCS, _link).html for page in pages)

    def test_every_link_to_a_heading_finds_it(self, sections):
        pages = {p.slug: p for s in sections for p in s.pages}
        ids = {
            slug: {h.id for h in source.render(page.path, DOCS, _link).headings}
            for slug, page in pages.items()
        }
        missing = []
        for slug, page in pages.items():
            html = source.render(page.path, DOCS, _link).html
            for target, _, anchor in re.findall(r'href="/docs(/?[^"#]*)(#)([^"]+)"', html):
                if target.strip("/") in ids and anchor not in ids[target.strip("/")]:
                    missing.append(f"{slug} -> {target}#{anchor}")
        assert missing == []
