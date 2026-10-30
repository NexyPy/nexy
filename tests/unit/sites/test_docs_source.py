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
def tracks():
    return source.read_tracks(DOCS)


class TestSlug:
    def test_a_page_loses_its_extension(self):
        assert source.slug_of("guides/actions.md") == "guides/actions"

    def test_a_folder_index_is_the_folder(self):
        assert source.slug_of("routing/fbr/README.md") == "routing/fbr"

    def test_the_root_index_is_empty(self):
        assert source.slug_of("README.md") == ""


class TestTracks:
    def test_the_first_track_is_start_here(self, tracks):
        assert tracks[0].label == "Start here"

    def test_every_track_explains_what_it_is_for(self, tracks):
        assert all(track.blurb for track in tracks)

    def test_every_group_explains_what_it_is_for(self, tracks):
        assert all(group.blurb for track in tracks for group in track.groups)

    def test_every_page_is_in_the_menu_once(self, tracks):
        listed = sorted(page.slug for track in tracks for page in source.pages_of(track))
        every = sorted(source.slug_of(p.relative_to(DOCS).as_posix()) for p in DOCS.rglob("*.md"))
        assert listed == [slug for slug in every if slug]

    def test_a_page_has_the_title_of_its_heading(self, tracks):
        page = source.find(tracks, "guides/actions")
        assert page is not None and page.title == "Actions"

    def test_a_page_knows_the_track_and_group_that_hold_it(self, tracks):
        page = source.find(tracks, "guides/actions")
        assert page is not None and (page.track, page.group) == ("build", "Forms and actions")

    def test_an_unknown_page_is_not_found(self, tracks):
        assert source.find(tracks, "nope/nothing") is None


class TestNeighbours:
    def test_the_first_page_has_no_previous(self, tracks):
        first = source.pages_of(tracks[0])[0].slug
        assert source.neighbours(tracks[0], first)[0] is None

    def test_the_next_page_follows_the_menu(self, tracks):
        first, second = source.pages_of(tracks[0])[:2]
        assert source.neighbours(tracks[0], first.slug)[1] == second

    def test_the_last_page_has_no_next(self, tracks):
        last = source.pages_of(tracks[-1])[-1].slug
        assert source.neighbours(tracks[-1], last)[1] is None

    def test_the_neighbours_are_read_inside_one_track(self, tracks):
        track = source.track_of(tracks, "guides/actions")
        before, after = source.neighbours(track, "guides/actions")
        assert {before.track, after.track} == {track.slug}


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


class TestFigures:
    """An image of the docs is an illustration: drawn as a figure, its alt text as the caption."""

    @staticmethod
    def _page(tmp_path: Path) -> Path:
        (tmp_path / "assets").mkdir()
        (tmp_path / "assets" / "scopes.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
            "<style>svg { color: #0a0a0a; }</style>"
            "<text>drawn-words</text></svg>",
            encoding="utf-8",
        )
        path = tmp_path / "page.md"
        path.write_text(
            "# T\n\n![The scopes of an error page](assets/scopes.svg)\n", encoding="utf-8"
        )
        return path

    def test_an_image_becomes_a_figure(self, tmp_path):
        html = source.render(self._page(tmp_path), tmp_path, _link).html
        assert '<figure class="figure">' in html and html.endswith("</figure>\n")
        assert "<figcaption>The scopes of an error page</figcaption>" in html

    def test_the_svg_is_drawn_so_it_takes_the_colours_of_the_page(self, tmp_path):
        html = source.render(self._page(tmp_path), tmp_path, _link).html
        assert "<svg" in html and "<text>drawn-words</text>" in html

    def test_the_palette_meant_for_github_is_dropped(self, tmp_path):
        html = source.render(self._page(tmp_path), tmp_path, _link).html
        assert "<style>" not in html

    def test_the_text_of_a_figure_is_left_out_of_the_search(self, tmp_path):
        rendered = source.render(self._page(tmp_path), tmp_path, _link)
        assert "drawn-words" not in source.plain(rendered.html)

    def test_an_image_that_does_not_exist_stays_an_image(self, tmp_path):
        path = tmp_path / "page.md"
        path.write_text("# T\n\n![gone](assets/gone.svg)\n", encoding="utf-8")
        assert '<img src="assets/gone.svg"' in source.render(path, tmp_path, _link).html


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


class TestCallouts:
    @staticmethod
    def _html(tmp_path: Path, text: str) -> str:
        path = tmp_path / "p.md"
        path.write_text(text, encoding="utf-8")
        return source.render(path, tmp_path, _link).html

    def test_a_github_alert_becomes_a_callout(self, tmp_path):
        html = self._html(tmp_path, "> [!NOTE]\n> Useful information.\n")
        assert 'class="callout callout-note"' in html
        assert "<p>Useful information.</p>" in html

    def test_the_callout_names_its_kind(self, tmp_path):
        assert '<p class="callout-title">Warning</p>' in self._html(
            tmp_path, "> [!WARNING]\n> Careful.\n"
        )

    def test_each_kind_has_its_own_class(self, tmp_path):
        html = self._html(tmp_path, "> [!TIP]\n> A shortcut.\n")
        assert 'class="callout callout-tip"' in html

    def test_a_plain_quote_stays_a_quote(self, tmp_path):
        html = self._html(tmp_path, "> A quote, not an alert.\n")
        assert "<blockquote>" in html and "callout" not in html

    def test_the_text_of_a_callout_survives(self, tmp_path):
        html = self._html(tmp_path, "> [!CAUTION]\n> Do not **do** this.\n")
        assert "Do not do this." in source.plain(html)


class TestDiagrams:
    @staticmethod
    def _html(tmp_path: Path, text: str) -> str:
        path = tmp_path / "p.md"
        path.write_text(text, encoding="utf-8")
        return source.render(path, tmp_path, _link).html

    def test_a_diagram_becomes_a_figure(self, tmp_path):
        html = self._html(tmp_path, "```diagram\nBrowser -> Server\n```\n")
        assert '<figure class="diagram">' in html and '<pre lang="diagram">' in html

    def test_a_named_diagram_has_a_caption(self, tmp_path):
        html = self._html(tmp_path, '```diagram filename="One request"\nBrowser -> Server\n```\n')
        assert "<figcaption>One request</figcaption>" in html

    def test_a_diagram_is_not_coloured_as_code(self, tmp_path):
        assert "<span" not in self._html(tmp_path, "```diagram\nBrowser -> Server\n```\n")

    def test_a_diagram_keeps_its_text(self, tmp_path):
        html = self._html(tmp_path, "```diagram\nBrowser -> Server\n```\n")
        assert "Browser -&gt; Server" in html

    def test_a_linear_flow_is_drawn_as_blocks(self, tmp_path):
        fence = "```diagram\nuvx nexy new notes ──► edit layout ──► nx build\n```\n"
        html = self._html(tmp_path, fence)
        assert html.count('class="flow-step"') == 3

    def test_a_flow_line_names_its_variant(self, tmp_path):
        html = self._html(tmp_path, "```diagram\nSSR   request ──► HTML\n```\n")
        assert '<span class="flow-label">SSR</span>' in html

    def test_a_mapping_is_drawn_as_pairs(self, tmp_path):
        html = self._html(
            tmp_path,
            "```diagram\nsrc/routes/about.nexy   →  /about\nsrc/routes/index.nexy   →  /\n```\n",
        )
        assert '<div class="map">' in html and "<code>/about</code>" in html

    def test_a_branch_drawing_stays_ascii(self, tmp_path):
        html = self._html(tmp_path, "```diagram\nBrowser\n   │\n   ├── HTML\n```\n")
        assert '<pre lang="diagram"><code>' in html and 'class="flow"' not in html

    def test_a_mapping_note_needs_no_column_gap(self, tmp_path):
        html = self._html(
            tmp_path,
            "```diagram\napp-like page → .tsx .vue (framework files)\nendpoint → .py (GET)\n```\n",
        )
        assert '<span class="map-note">(framework files)</span>' in html


class TestStructures:
    @staticmethod
    def _html(tmp_path: Path, text: str) -> str:
        path = tmp_path / "p.md"
        path.write_text(text, encoding="utf-8")
        return source.render(path, tmp_path, _link).html

    def test_a_folder_listing_becomes_an_explorer(self, tmp_path):
        html = self._html(tmp_path, "```text\nsrc/\n├─ routes/\n│  └─ index.nexy\n```\n")
        assert '<figure class="diagram tree">' in html

    def test_a_folder_is_drawn_apart_from_a_file(self, tmp_path):
        html = self._html(tmp_path, "```text\nsrc/\n├─ routes/\n│  └─ index.nexy\n```\n")
        assert '<span class="tree-name tree-dir">routes/</span>' in html

    def test_a_nested_file_follows_the_guide_of_its_parent(self, tmp_path):
        html = self._html(tmp_path, "```text\nsrc/\n├─ routes/\n│  └─ index.nexy\n```\n")
        assert '<span class="tree-guide tree-guide-line"></span>' in html

    def test_the_last_child_closes_the_line_of_its_folder(self, tmp_path):
        html = self._html(tmp_path, "```text\nsrc/\n└─ a.py\n```\n")
        assert '<span class="tree-guide tree-guide-last"></span>' in html

    def test_a_route_note_is_marked_apart(self, tmp_path):
        html = self._html(tmp_path, "```text\nsrc/\n└─ index.nexy   → /\n```\n")
        assert '<span class="tree-route">→ /</span>' in html

    def test_a_note_keeps_the_names_it_marks_as_code(self, tmp_path):
        html = self._html(tmp_path, "```text\nsrc/\n└─ a.css   created by `nexy new`\n```\n")
        assert "<code>nexy new</code>" in html

    def test_a_plain_listing_stays_a_block(self, tmp_path):
        html = self._html(tmp_path, "```text\nnexy » error index.py:18\n```\n")
        assert '<pre lang="text">' in html and 'class="tree"' not in html


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
    def test_every_page_renders(self, tracks):
        pages = [page for track in tracks for page in source.pages_of(track)]
        assert all(source.render(page.path, DOCS, _link).html for page in pages)

    def test_every_link_to_a_heading_finds_it(self, tracks):
        pages = {p.slug: p for t in tracks for p in source.pages_of(t)}
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
