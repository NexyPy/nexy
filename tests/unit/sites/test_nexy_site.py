"""The docs site made with Nexy: it serves the pages of docs/ and nothing outside them."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from sites.shared import docs_source
from tests.e2e.project import request

SITE = Path(__file__).resolve().parents[3] / "sites" / "nexy"
DOCS = SITE.parents[1] / "docs"
ACTIONS = "/docs/guides/actions"
MODULAR = "/docs/routing/modular/dependency-injection"
NOTHING: dict[str, str] = {}


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
    ]
    found = request(SITE, *[(path, NOTHING) for path in paths])
    return dict(zip(paths, found, strict=True))


def _menu(body: str) -> str:
    """The side menu of the page: between its nav tags, before the article."""
    return body.split('<nav class="side"', 1)[1].split("</nav>", 1)[0]


def test_the_root_sends_visitors_to_the_docs(answers):
    status, headers, _ = answers["/"]
    assert status in (301, 302, 307, 308) and headers["location"].endswith("/docs")


def test_the_docs_home_is_served(answers):
    assert answers["/docs"][0] == 200


def test_a_page_has_its_title(answers):
    assert "<title>Actions - Nexy</title>" in answers[ACTIONS][2]


def test_the_menu_marks_the_current_page(answers):
    assert re.search(r'<a [^>]*aria-current="page"[^>]*>Actions</a>', answers[ACTIONS][2])


def test_a_heading_has_its_anchor_and_a_link_in_the_outline(answers):
    body = answers[ACTIONS][2]
    assert 'id="define-an-action"' in body and 'href="#define-an-action"' in body


def test_links_between_pages_point_to_the_site(answers):
    assert 'href="/docs/guides/middleware-and-security"' in answers[ACTIONS][2]


def test_the_menu_of_a_page_holds_only_its_area(answers):
    """A page of the Nexy area sees its own pages, never those of a router."""
    menu = _menu(answers[ACTIONS][2])
    assert "Actions" in menu and "Dependency injection" not in menu


def test_the_selector_names_every_area(answers):
    menu = _menu(answers[ACTIONS][2])
    assert all(f"<b>{area.label}</b>" in menu for area in docs_source.AREAS)


def test_the_selector_marks_the_area_of_the_page(answers):
    body = answers[MODULAR][2]
    assert re.search(
        r'aria-current="true"\s*>\s*<span class="area-icon">.*?<b>Modular Router</b>',
        body,
        re.S,
    )


def test_only_the_section_of_the_page_is_open(answers):
    assert len(re.findall(r'<details class="group"[^>]* open>', answers[ACTIONS][2])) == 1


def test_the_sections_do_not_close_each_other(answers):
    """Opening a folder never hides the folder holding the current page."""
    assert 'name="nav"' not in answers[ACTIONS][2]


def test_the_menu_can_be_filtered(answers):
    assert 'class="side-filter"' in answers[ACTIONS][2]


def test_the_menu_is_drawn_by_the_server(answers):
    """No script builds the menu: it is already in the response."""
    head = answers[ACTIONS][2].split("</head>")[0]
    assert 'data-section="' in answers[ACTIONS][2] and "dataset.router" not in head


def test_the_pager_stays_inside_the_area(answers):
    tail = answers[MODULAR][2].split('class="pager"', 1)[1].split("</nav>", 1)[0]
    assert "Quick start" not in tail


def test_a_page_that_does_not_exist_is_not_found(answers):
    assert answers["/docs/nope/nothing"][0] == 404


def test_the_button_offers_the_page_as_markdown(answers):
    assert 'data-markdown="/markdown?slug=guides/actions"' in answers[ACTIONS][2]


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
    sections = docs_source.read_sections(DOCS)
    wanted = {"/docs"} | {f"/docs/{p.slug}" for s in sections for p in s.pages}
    found = request(SITE, *[(path, NOTHING) for path in sorted(wanted)])
    assert len(found) == len(wanted) and {status for status, _, _ in found} == {200}
