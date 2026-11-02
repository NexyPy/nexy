"""The docs site made with Nexy: it serves the pages of docs/ and nothing outside them."""

from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

import pytest

from sites.shared import docs_source
from tests.e2e.project import request

SITE = Path(__file__).resolve().parents[3] / "sites" / "nexy"
DOCS = SITE.parents[1] / "docs"
ACTIONS = "/docs/guides/actions"
MODULAR = "/docs/routing/modular/dependency-injection"
CONTINUE = '<a href="#" class="continue" hidden>Continue</a>'
NOTHING: dict[str, str] = {}
REDIRECTS = sorted(docs_source.REDIRECTS.items())


@pytest.fixture(scope="module")
def answers():
    paths = [
        "/",
        "/docs",
        ACTIONS,
        "/docs/nope/nothing",
        MODULAR,
        "/assets/style.css",
        "/assets/%2e%2e%2f%2e%2e%2fnexy%2fnexyconfig.py",
        "/search-index",
        "/markdown",
        "/markdown?slug=guides/actions",
        "/markdown?slug=nope/nothing",
        *(f"/docs/{old}" for old, _new in REDIRECTS),
    ]
    found = request(SITE, *[(path, NOTHING) for path in paths])
    return dict(zip(paths, found, strict=True))


def _menu(body: str) -> str:
    """The side menu of the page: between its nav tags, before the article."""
    return body.split('<nav class="side"', 1)[1].split("</nav>", 1)[0]


class TestNewBadge:
    """DOC-27: the Nexy site paints the same pill as the vanilla one, and hides the token."""

    def test_a_marked_page_paints_the_pill_after_the_link(self, answers):
        marked = next(
            (
                page
                for track in docs_source.read_tracks(DOCS)
                for page in docs_source.pages_of(track)
                if page.badge
            ),
            None,
        )
        assert marked is not None, "docs/README.md marks no page: the pill would go untested"
        pattern = (
            rf'<a href="/docs/{re.escape(marked.slug)}"[^>]*>'
            rf'{re.escape(marked.label)}</a><span class="badge-new">New</span>'
        )
        assert re.search(pattern, _menu(answers[ACTIONS][2])), marked.slug

    def test_the_token_is_in_no_html_the_site_serves(self, answers):
        pages = {
            path: body
            for path, (_status, _headers, body) in answers.items()
            if "<!doctype html>" in body.lower()
        }
        assert pages and all("{new}" not in body for body in pages.values())

    def test_the_menu_of_every_page_hides_the_token(self, answers):
        for path, (_status, _headers, body) in answers.items():
            if '<nav class="side"' in body:
                assert "{new}" not in _menu(body), path

    def test_the_home_page_hides_the_token_of_its_own_table(self, answers):
        assert "{new}" not in answers["/docs"][2]


def test_the_root_sends_visitors_to_the_docs(answers):
    status, headers, _ = answers["/"]
    assert status in (301, 302, 307, 308) and headers["location"].endswith("/docs")


def test_the_docs_home_is_served(answers):
    assert answers["/docs"][0] == 200


def test_a_page_has_its_title(answers):
    assert "<title>Actions - Nexy</title>" in answers[ACTIONS][2]


def test_the_menu_marks_the_current_page(answers):
    assert re.search(r'<a [^>]*aria-current="page"[^>]*>Actions</a>', answers[ACTIONS][2])


def test_the_menu_shows_no_description(answers):
    """A11 mirror: the Nexy site lists labels in the menu, never their summaries."""
    assert 'class="page-summary"' not in _menu(answers[ACTIONS][2])
    assert "<small" not in _menu(answers[ACTIONS][2])


def _progress_scripts(text: str) -> list[str]:
    """The inline scripts that carry the reading state, dedented: what both sites must share."""
    return [
        textwrap.dedent(block)
        for block in re.findall(r"<script>(.*?)</script>", text, re.S)
        if "seen" in block
    ]


def test_the_read_pages_are_dimmed_by_the_same_script_as_the_vanilla_site():
    """DOC-26: one divergence between the two sites on the reading state is a bug."""
    vanilla = (SITE.parent / "vanilla" / "template.html").read_text(encoding="utf-8")
    nexy = (SITE / "src" / "routes" / "layout.nexy").read_text(encoding="utf-8")
    assert _progress_scripts(vanilla) == _progress_scripts(nexy)


def test_the_button_offers_the_reader_a_hidden_link(answers):
    assert CONTINUE in answers[ACTIONS][2]


def test_the_menu_of_this_site_holds_no_read_state(answers):
    assert "seen" not in _menu(answers[ACTIONS][2])


def test_the_list_of_read_pages_is_taken_before_the_menu_paints(answers):
    body = answers[ACTIONS][2]
    assert 'localStorage.getItem("nexy-docs-seen")' in body.split("</head>", 1)[0]


def test_the_links_are_dimmed_while_the_menu_is_still_parsed(answers):
    """The marking sits between the menu and the panel: no plain link is ever painted."""
    body = answers[ACTIONS][2]
    marking = body.index('classList.add("seen")')
    assert body.index("</nav>") < marking < body.index('<div class="panel"')


def test_a_heading_has_its_anchor_and_a_link_in_the_outline(answers):
    body = answers[ACTIONS][2]
    assert 'id="the-action-cycle"' in body and 'href="#the-action-cycle"' in body


def test_links_between_pages_point_to_the_site(answers):
    assert 'href="/docs/guides/middleware-and-security"' in answers[ACTIONS][2]


def test_the_menu_of_a_page_holds_every_section(answers):
    menu = _menu(answers[ACTIONS][2])
    tracks = docs_source.read_tracks(DOCS)
    assert all(f'<p class="side-section">{track.label}</p>' in menu for track in tracks)


def test_the_menu_declares_the_scope_of_every_group(answers):
    menu = _menu(answers[ACTIONS][2])
    expected = [g.scope for t in docs_source.read_tracks(DOCS) for g in t.groups]
    assert re.findall(r'class="group" data-section="[^"]+" data-scope="([^"]+)"', menu) == expected


def test_the_groups_of_a_router_name_their_router(answers):
    menu = _menu(answers[ACTIONS][2])
    assert all(f'data-router="{key}"' in menu for key, _, _ in docs_source.ROUTERS)


def test_the_selector_names_every_router(answers):
    menu = _menu(answers[ACTIONS][2])
    assert all(f"<b>{name}</b>" in menu for _, name, _ in docs_source.ROUTERS)


def test_the_selector_marks_the_router_of_the_page(answers):
    assert re.search(r'data-pick="modular"\s+aria-current="true"', answers[MODULAR][2])


def test_a_router_page_names_its_router(answers):
    assert re.search(r'<meta name="nexy-router" content="modular"', answers[MODULAR][2])


def test_a_shared_page_names_no_router(answers):
    assert '<meta name="nexy-router"' not in answers[ACTIONS][2]


def test_only_the_section_of_the_page_is_open(answers):
    assert len(re.findall(r'<details class="group"[^>]* open>', answers[ACTIONS][2])) == 1


def test_the_sections_do_not_close_each_other(answers):
    """Opening a folder never hides the folder holding the current page."""
    assert 'name="nav"' not in answers[ACTIONS][2]


def test_the_menu_can_be_filtered(answers):
    assert 'class="side-filter"' in answers[ACTIONS][2]


def test_the_menu_head_stays_while_the_groups_scroll(answers):
    body = answers[ACTIONS][2]
    assert '<div class="side-scroll">' in body and 'class="group-note"' not in body


def test_the_menu_is_drawn_by_the_server(answers):
    """No script builds the menu: it is already in the response."""
    assert 'data-section="' in answers[ACTIONS][2]


def test_the_pager_stays_inside_the_router(answers):
    tail = answers[MODULAR][2].split('class="pager"', 1)[1].split("</nav>", 1)[0]
    assert "/fbr/" not in tail


def test_a_page_that_does_not_exist_is_not_found(answers):
    assert answers["/docs/nope/nothing"][0] == 404


@pytest.mark.parametrize("old", [old for old, _ in REDIRECTS])
def test_an_old_address_answers_with_a_permanent_redirect(answers, old):
    assert answers[f"/docs/{old}"][0] == 301


@pytest.mark.parametrize(("old", "new"), REDIRECTS)
def test_an_old_address_points_at_the_page_that_replaced_it(answers, old, new):
    assert answers[f"/docs/{old}"][1]["location"] == f"/docs/{new}"


def test_the_button_offers_the_page_as_markdown(answers):
    assert 'data-markdown="/markdown?slug=guides/actions"' in answers[ACTIONS][2]


def test_a_page_declares_its_canonical_address(answers):
    assert (
        '<link rel="canonical" href="https://nexy.ai/docs/guides/actions/">' in answers[ACTIONS][2]
    )


def test_a_page_reads_as_a_card(answers):
    body = answers[ACTIONS][2]
    assert '<meta property="og:title" content="Actions">' in body
    assert '<meta name="twitter:card" content="summary_large_image">' in body


def test_a_page_says_what_it_is_about(answers):
    assert re.search(r'<meta name="description" content="[^"]{20,}">', answers[ACTIONS][2])


def test_a_page_carries_its_linked_data(answers):
    found = re.search(r'application/ld\+json">(.*?)</script>', answers[ACTIONS][2])
    assert found and json.loads(found[1])["@graph"][0]["@type"] == "TechArticle"


def test_the_markdown_of_a_page_is_its_source_file(answers):
    status, headers, body = answers["/markdown?slug=guides/actions"]
    assert status == 200 and headers["content-type"].startswith("text/markdown")
    assert body == (DOCS / "guides" / "actions.md").read_text(encoding="utf-8")


def test_the_markdown_of_the_home_is_served(answers):
    status, _, body = answers["/markdown"]
    assert status == 200 and body.startswith("# Nexy documentation")


def test_a_markdown_page_that_does_not_exist_is_not_found(answers):
    assert answers["/markdown?slug=nope/nothing"][0] == 404


def test_the_stylesheet_is_the_one_of_the_vanilla_site(answers):
    status, headers, body = answers["/assets/style.css"]
    assert status == 200 and headers["content-type"].startswith("text/css") and "--accent" in body


def test_a_file_outside_the_assets_cannot_be_read(answers):
    status, _, body = answers["/assets/%2e%2e%2f%2e%2e%2fnexy%2fnexyconfig.py"]
    assert status == 404 and "NexyConfigModel" not in body


def test_search_lists_every_page(answers):
    entries = json.loads(answers["/search-index"][2])
    assert len(entries) == len(list(DOCS.rglob("*.md")))


def test_every_page_of_the_menu_is_served():
    tracks = docs_source.read_tracks(DOCS)
    wanted = {"/docs"} | {f"/docs/{p.slug}" for t in tracks for p in docs_source.pages_of(t)}
    found = request(SITE, *[(path, NOTHING) for path in sorted(wanted)])
    assert len(found) == len(wanted) and {status for status, _, _ in found} == {200}
