import re

import pytest

from src.docs.nav import PAGES
from src.docs.search import ENTRIES


def test_the_home_page_links_every_section(client):
    assert 'href="/docs/guides/schedule"' in client.get("/").text


@pytest.mark.parametrize("page", PAGES, ids=lambda page: page.url)
def test_every_page_of_the_menu_shows_its_markdown(client, page):
    # The first heading of the file, in the page: the Markdown answers, not another route.
    heading = page.file.read_text(encoding="utf-8").splitlines()[0].removeprefix("# ")
    assert f">{heading}</h1>" in client.get(page.url).text


def test_a_markdown_page_names_its_tab_after_its_heading(client):
    assert "<title>Quick start | Cairn docs</title>" in client.get("/docs/quick-start").text


def test_a_markdown_page_describes_itself_with_its_first_paragraph(client):
    page = client.get("/docs/commands/prune").text
    assert '<meta name="description" content="Deletes the snapshots' in page


def test_the_menu_marks_the_current_page(client):
    page = client.get("/docs/configuration").text
    assert re.search(r'href="/docs/configuration"[^>]*aria-current="page"', page)


def test_the_outline_lists_the_headings_of_the_page(client):
    assert 'href="#check-the-installation"' in client.get("/docs/installation").text


def test_a_page_links_to_the_next_one(client):
    page = client.get("/docs/installation").text
    assert re.search(r'href="/docs/quick-start"[^>]*>\s*<span[^>]*>Next', page)


def test_every_search_result_lands_on_a_heading_of_its_page(client):
    for entry in ENTRIES:
        path, _, anchor = entry.url.partition("#")
        assert not anchor or f'id="{anchor}"' in client.get(path).text, entry.url


def test_the_search_page_lists_the_results(client):
    assert 'href="/docs/commands/prune"' in client.get("/search?q=prune").text


def test_the_search_page_says_when_nothing_matches(client):
    assert "No page has every word" in client.get("/search?q=zebra").text


def test_the_search_page_escapes_the_query(client):
    assert "&lt;b&gt;" in client.get("/search?q=<b>x</b>").text


def test_an_unknown_page_answers_404(client):
    assert client.get("/docs/nothing-here").status_code == 404


def test_the_sitemap_lists_the_docs_pages(client):
    assert "<loc>https://docs.cairn.example/docs/faq</loc>" in client.get("/sitemap.xml").text
