"""The documentation sites read docs/ through one module, so none of them can drift."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from sites.shared import docs_source as source
from sites.shared import i18n

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
    def test_the_first_track_is_getting_started(self, tracks):
        assert tracks[0].label == "Getting Started"

    def test_every_page_is_in_the_menu_once(self, tracks):
        listed = sorted(page.slug for track in tracks for page in source.pages_of(track))
        every = sorted(source.slug_of(relative) for relative in i18n.english_pages(DOCS))
        assert listed == [slug for slug in every if slug]

    def test_a_page_has_the_title_of_its_heading(self, tracks):
        page = source.find(tracks, "guides/actions")
        assert page is not None and page.title == "Actions"

    def test_a_page_knows_the_track_and_group_that_hold_it(self, tracks):
        page = source.find(tracks, "guides/actions")
        assert page is not None
        assert (page.track, page.group) == ("guides", "Forms and data")

    def test_an_unknown_page_is_not_found(self, tracks):
        assert source.find(tracks, "nope/nothing") is None


class TestGroupScope:
    """A group declares the scope it belongs to: `### Routing {fbr}`."""

    @staticmethod
    def _tracks(tmp_path: Path, heading: str) -> list[source.Track]:
        (tmp_path / "guides").mkdir()
        (tmp_path / "guides" / "actions.md").write_text("# Actions", encoding="utf-8")
        (tmp_path / "README.md").write_text(
            "# Docs\n\n## Guides\n\n"
            f"### {heading}\n"
            "| Page | What you will do |\n|---|---|\n"
            "| [Actions](guides/actions.md) | Post a form |\n",
            encoding="utf-8",
        )
        return source.read_tracks(tmp_path)

    def test_a_marker_scopes_the_group_it_names(self, tmp_path):
        group = self._tracks(tmp_path, "Forms {modular}")[0].groups[0]
        assert (group.scope, group.router) == ("modular", "modular")

    def test_a_marker_is_not_part_of_the_title(self, tmp_path):
        assert self._tracks(tmp_path, "Forms {modular}")[0].groups[0].title == "Forms"

    def test_a_group_without_a_marker_is_deduced_from_its_pages(self, tmp_path):
        group = self._tracks(tmp_path, "Forms")[0].groups[0]
        assert (group.scope, group.router) == ("core", None)

    def test_a_marker_wins_over_the_folder_of_the_pages(self, tmp_path):
        group = self._tracks(tmp_path, "Forms {fbr}")[0].groups[0]
        assert group.router == "fbr"

    def test_an_advanced_group_belongs_to_no_router(self, tmp_path):
        group = self._tracks(tmp_path, "Advanced {advanced}")[0].groups[0]
        assert (group.scope, group.router) == ("advanced", None)

    def test_an_unknown_marker_is_left_visible_in_the_title(self, tmp_path):
        group = self._tracks(tmp_path, "Forms {nope}")[0].groups[0]
        assert (group.title, group.scope) == ("Forms {nope}", "core")


class TestPageBadge:
    """DOC-27: a `{new}` token at the end of a row's summary marks the page and nothing else."""

    @staticmethod
    def _page(tmp_path: Path, summary: str) -> source.Page:
        (tmp_path / "guides").mkdir(exist_ok=True)
        (tmp_path / "guides" / "actions.md").write_text("# Actions", encoding="utf-8")
        (tmp_path / "README.md").write_text(
            "# Docs\n\n## Guides\n\n### Forms\n"
            "| Page | What you will do |\n|---|---|\n"
            f"| [Actions](guides/actions.md) | {summary} |\n",
            encoding="utf-8",
        )
        return source.pages_of(source.read_tracks(tmp_path)[0])[0]

    def test_a_token_marks_the_badge_of_the_page(self, tmp_path):
        assert self._page(tmp_path, "Post a form {new}").badge == "new"

    def test_the_token_leaves_the_summary_of_the_page(self, tmp_path):
        assert self._page(tmp_path, "Post a form {new}").summary == "Post a form"

    def test_an_unmarked_page_carries_no_badge(self, tmp_path):
        assert self._page(tmp_path, "Post a form").badge == ""

    def test_an_unknown_token_is_left_visible_in_the_summary(self, tmp_path):
        page = self._page(tmp_path, "Post a form {neww}")
        assert (page.badge, page.summary) == ("", "Post a form {neww}")

    def test_a_token_in_the_middle_of_a_sentence_is_not_a_badge(self, tmp_path):
        page = self._page(tmp_path, "Post {new} a form")
        assert (page.badge, page.summary) == ("", "Post {new} a form")

    def test_the_token_is_not_drawn_in_a_rendered_page(self, tmp_path):
        self._page(tmp_path, "Post a form {new}")  # writes guides/actions.md, the table's target
        path = tmp_path / "guides" / "page.md"
        path.write_text(
            "# T\n\n| Page | Summary |\n|---|---|\n| [a](actions.md) | Post a form {new} |\n",
            encoding="utf-8",
        )
        assert "{new}" not in source.render(path, tmp_path, _link).html

    def test_the_token_leaves_the_search_entry_of_the_home(self, tmp_path):
        row = "| [Actions](guides/actions.md) | Post a form {new} |"
        (tmp_path / "README.md").write_text(
            f"# Docs\n\n## Guides\n\n### Forms\n| Page | Summary |\n|---|---|\n{row}\n",
            encoding="utf-8",
        )
        page = source.home(tmp_path)
        entry = source.search_entry(page, "Docs", source.render(page.path, tmp_path, _link), "docs")
        assert "{new}" not in entry["text"]


class TestRealDocsBadges:
    """The real menu: a typo in a token would be drawn as a word of the promise."""

    def test_no_summary_carries_a_brace(self, tracks):
        """Only `{new}` is a token, and `read_tracks` strips it: a `{neww}` would stay visible."""
        stray = [p.slug for t in tracks for p in source.pages_of(t) if "{" in p.summary]
        assert stray == []

    def test_a_marked_page_carries_the_token_in_no_word_it_shows(self, tracks):
        for track in tracks:
            for page in source.pages_of(track):
                if page.badge:
                    assert "{new}" not in f"{page.summary} {page.label} {page.title}"


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
        near = [page for page in source.neighbours(track, "guides/actions") if page]
        assert near and {page.track for page in near} == {track.slug}


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

    def test_a_group_marker_is_not_drawn_on_the_page(self, tmp_path):
        html = self._html(tmp_path, "### Routing {fbr}\n")
        assert '<h3 id="routing">Routing' in html and "{fbr}" not in html

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


class TestRouterVariants:
    """DOC-20: the words and the code of a page follow the router the reader chose."""

    @staticmethod
    def _html(tmp_path: Path, text: str) -> str:
        path = tmp_path / "page.md"
        path.write_text(text, encoding="utf-8")
        return source.render(path, tmp_path, _link).html

    def test_a_block_is_drawn_under_its_router(self, tmp_path):
        html = self._html(tmp_path, "<!-- router:fbr -->\nThe FBR way.\n<!-- /router -->\n")
        block = re.search(r'<div class="router-variant" data-router="fbr">(.*?)</div>', html, re.S)
        assert block and "<p>The FBR way.</p>" in block[1]

    def test_a_block_may_serve_several_routers(self, tmp_path):
        html = self._html(tmp_path, "<!-- router:fbr,custom -->\nShared.\n<!-- /router -->\n")
        assert 'data-router="fbr custom"' in html

    def test_the_markers_leave_no_comment_on_the_page(self, tmp_path):
        html = self._html(tmp_path, "<!-- router:modular -->\nM\n<!-- /router -->\n")
        assert "router:" not in html

    def test_a_marker_of_an_unknown_router_draws_no_variant(self, tmp_path):
        html = self._html(tmp_path, "<!-- router:nope -->\nShared.\n<!-- /router -->\n")
        assert 'class="router-variant"' not in html

    def test_a_marker_inside_a_code_block_stays_code(self, tmp_path):
        html = self._html(tmp_path, "```md\n<!-- router:fbr -->\n```\n")
        assert 'class="router-variant"' not in html and "router:fbr" in html

    def test_a_heading_inside_a_variant_is_in_the_outline(self, tmp_path):
        path = tmp_path / "page.md"
        path.write_text("<!-- router:custom -->\n## Install\n<!-- /router -->\n", encoding="utf-8")
        assert [h.text for h in source.render(path, tmp_path, _link).headings] == ["Install"]


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

    def test_the_logic_of_a_nexy_file_is_coloured_as_python(self, tmp_path):
        html = self._html(tmp_path, "nexy", "---\ndef run():\n    pass\n---")
        assert '<span class="tok-k">def</span>' in html

    def test_the_template_after_the_bars_is_coloured_as_html(self, tmp_path):
        html = self._html(tmp_path, "nexy", "---\nx = 1\n---\n<h1>{{ x }}</h1>")
        assert '<span class="tok-nt">h1</span>' in html

    def test_the_bars_of_a_nexy_frontmatter_are_kept(self, tmp_path):
        html = self._html(tmp_path, "nexy", "---\nx = 1\n---\n<p>hi</p>")
        assert html.count('<span class="tok-bar">---</span>') == 2

    def test_an_unknown_language_stays_plain(self, tmp_path):
        assert "tok-" not in self._html(tmp_path, "klingon", "qapla")

    def test_a_block_without_a_language_stays_plain(self, tmp_path):
        assert "tok-" not in self._html(tmp_path, "", "def run(): pass")

    def test_a_named_block_is_coloured_too(self, tmp_path):
        html = self._html(tmp_path, 'python filename="a.py"', "def run(): pass")
        assert "<figcaption>a.py</figcaption>" in html and "tok-k" in html

    def test_an_added_line_is_marked_and_the_marker_is_gone(self, tmp_path):
        html = self._html(tmp_path, "python", "x = 1  # [!code ++]")
        assert 'class="line line-add"' in html and "!code" not in html

    def test_a_removed_line_is_marked(self, tmp_path):
        html = self._html(tmp_path, "python", "x = 1  # [!code --]")
        assert 'class="line line-del"' in html

    def test_a_highlighted_line_is_marked(self, tmp_path):
        html = self._html(tmp_path, "python", "x = 1  # [!code highlight]")
        assert 'class="line line-hl"' in html

    def test_every_line_is_one_row(self, tmp_path):
        html = self._html(tmp_path, "python", "x = 1\ny = 2")
        assert html.count('class="line"') == 2


class TestTables:
    def test_a_table_scrolls_inside_its_own_card(self, tmp_path):
        path = tmp_path / "p.md"
        path.write_text("| A | B |\n| --- | --- |\n| 1 | 2 |\n", encoding="utf-8")
        html = source.render(path, tmp_path, _link).html
        assert '<div class="table-wrap"><table>' in html


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
        assert '<p class="callout-title" data-i18n="callout_warning">Warning</p>' in self._html(
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

    def test_no_group_title_carries_a_marker(self, tracks):
        """A typo in a marker would be drawn in the menu instead of scoping the group."""
        assert [g.title for t in tracks for g in t.groups if "{" in g.title] == []

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


class TestLanguageTree:
    """A language reads its menu and pages from `docs/<code>/`, English where one is missing."""

    MENU = (
        "## {track}\n\n### {group}\n| Page | Summary |\n|---|---|\n"
        "| [{a}](guides/a.md) | {s} |\n| [B](guides/b.md) | b |\n"
    )

    @classmethod
    def _docs(cls, tmp_path: Path) -> Path:
        (tmp_path / "guides").mkdir()
        (tmp_path / "README.md").write_text(
            "# Docs\n\n" + cls.MENU.format(track="Guides", group="Forms", a="A", s="a"),
            encoding="utf-8",
        )
        (tmp_path / "guides" / "a.md").write_text(
            "# A\n\n![Art](../assets/x.svg)\n", encoding="utf-8"
        )
        (tmp_path / "guides" / "b.md").write_text("# B\n", encoding="utf-8")
        (tmp_path / "assets").mkdir()
        (tmp_path / "assets" / "x.svg").write_text("<svg>art</svg>", encoding="utf-8")
        french = tmp_path / "fr" / "guides"
        french.mkdir(parents=True)
        (tmp_path / "fr" / "README.md").write_text(
            "# Docs\n\n" + cls.MENU.format(track="Guides", group="Formulaires", a="Un A", s="un"),
            encoding="utf-8",
        )
        (french / "a.md").write_text("# Un A\n\n![Dessin](../assets/x.svg)\n", encoding="utf-8")
        return tmp_path

    def test_the_menu_comes_from_the_language_tree(self, tmp_path):
        group = source.read_tracks(self._docs(tmp_path), "fr")[0].groups[0]
        assert group.title == "Formulaires"

    def test_a_translated_page_is_read_from_the_language_tree(self, tmp_path):
        docs = self._docs(tmp_path)
        page = source.find(source.read_tracks(docs, "fr"), "guides/a")
        assert page is not None and page.path == docs / "fr" / "guides" / "a.md"

    def test_a_missing_translation_falls_back_to_english(self, tmp_path):
        docs = self._docs(tmp_path)
        page = source.find(source.read_tracks(docs, "fr"), "guides/b")
        assert page is not None and page.fallback and page.path == docs / "guides" / "b.md"

    def test_a_translated_page_lives_under_its_language(self, tmp_path):
        page = source.find(source.read_tracks(self._docs(tmp_path), "fr"), "guides/a")
        assert page is not None and page.address == "fr/guides/a"

    def test_an_english_page_lives_at_its_slug(self, tmp_path):
        page = source.find(source.read_tracks(self._docs(tmp_path)), "guides/a")
        assert page is not None and page.address == "guides/a"

    def test_the_home_of_a_language_lives_at_its_code(self, tmp_path):
        assert source.home(self._docs(tmp_path), "fr").address == "fr"

    def test_a_translated_page_draws_the_figures_of_the_english_tree(self, tmp_path):
        docs = self._docs(tmp_path)
        rendered = source.render(docs / "fr" / "guides" / "a.md", docs, _link)
        assert "<svg>art</svg>" in rendered.html

    def test_a_translated_link_leaving_docs_reaches_the_repository(self, tmp_path):
        docs = self._docs(tmp_path)
        (docs / "fr" / "guides" / "c.md").write_text(
            "[Log](../../CHANGELOG.md)\n", encoding="utf-8"
        )
        rendered = source.render(docs / "fr" / "guides" / "c.md", docs, _link)
        assert f'href="{source.REPOSITORY}CHANGELOG.md"' in rendered.html
