"""The docs site made with Nexy: it serves the pages of docs/ and nothing outside them."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from sites.shared import docs_source
from tests.e2e.project import request

SITE = Path(__file__).resolve().parents[3] / "sites" / "nexy"
ACTIONS = "/docs/guides/actions"
NOTHING: dict[str, str] = {}


@pytest.fixture(scope="module")
def answers():
    paths = [
        "/",
        "/docs",
        ACTIONS,
        "/docs/nope/nothing",
        "/docs/routing/modular/dependency-injection",
        "/assets/style.css",
        "/assets/%2e%2e%2f%2e%2e%2fnexy%2fnexyconfig.py",
        "/search-index",
    ]
    found = request(SITE, *[(path, NOTHING) for path in paths])
    return dict(zip(paths, found, strict=True))


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


def test_the_menu_marks_the_pages_of_each_router(answers):
    body = answers[ACTIONS][2]
    assert '<li data-router="fbr">' in body and '<li data-router="modular">' in body


def test_the_menu_offers_both_routers(answers):
    body = answers[ACTIONS][2]
    found = re.findall(r'<button type="button" data-router="(\w+)" data-home="([^"]+)"', body)
    assert found == [("fbr", "/docs/routing/fbr"), ("modular", "/docs/routing/modular")]


def test_a_modular_page_declares_its_router(answers):
    body = answers["/docs/routing/modular/dependency-injection"][2]
    assert re.search(r'<meta name="nexy-router" content="modular" ?/?>', body)


def test_a_page_of_neither_router_declares_none(answers):
    assert '<meta name="nexy-router"' not in answers[ACTIONS][2]


def test_the_router_is_set_before_the_first_paint(answers):
    head = answers[ACTIONS][2].split("</head>")[0]
    assert "dataset.router" in head and "nexy-docs-router" in head


def test_a_page_that_does_not_exist_is_not_found(answers):
    assert answers["/docs/nope/nothing"][0] == 404


def test_the_stylesheet_is_the_one_of_the_vanilla_site(answers):
    status, headers, body = answers["/assets/style.css"]
    assert status == 200 and headers["content-type"].startswith("text/css") and "--accent" in body


def test_a_file_outside_the_assets_cannot_be_read(answers):
    status, _, body = answers["/assets/%2e%2e%2f%2e%2e%2fnexy%2fnexyconfig.py"]
    assert status == 404 and "NexyConfigModel" not in body


def test_search_lists_every_page(answers):
    entries = json.loads(answers["/search-index"][2])
    assert len(entries) == len(list((SITE.parents[1] / "docs").rglob("*.md")))


def test_every_page_of_the_menu_is_served():
    body = request(SITE, ("/docs", NOTHING))[0][2]
    links = sorted(set(re.findall(r'<a href="(/docs/[^"#]+)"', body)))
    statuses = [status for status, _, _ in request(SITE, *[(path, NOTHING) for path in links])]
    in_the_menu = sum(
        len(section.pages) for section in docs_source.read_sections(SITE.parents[1] / "docs")
    )
    assert set(statuses) == {200} and len(links) == in_the_menu
