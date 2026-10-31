"""The head tags, the sitemap and robots: what a crawler reads, written once for both sites."""

from __future__ import annotations

import json
import re

import pytest

from sites.shared import seo

URL = "https://example.test/docs/guides/actions/"
TRAIL = (("Documentation", "https://example.test/docs/"), ("Actions", URL))


def _head(**given: str) -> str:
    facts = {
        "title": "Actions",
        "description": "A function becomes an endpoint.",
        "url": URL,
        "site_url": "https://example.test",
        "trail": TRAIL,
        **given,
    }
    return seo.Head(**facts).html()  # type: ignore[arg-type]


def _graph(html: str) -> list[dict[str, object]]:
    found = re.search(r'<script type="application/ld\+json">(.*?)</script>', html)
    assert found is not None
    return json.loads(found[1])["@graph"]


class TestDescription:
    def test_the_opening_paragraph_is_the_summary(self):
        assert seo.description("<p>The first one.</p><p>Then more.</p>") == "The first one."

    def test_the_summary_carries_no_markup(self):
        html = "<p>Call <code>@Action</code> on a <a href='x'>function</a>.</p>"
        assert seo.description(html) == "Call @Action on a function."

    def test_the_summary_keeps_its_words_apart(self):
        assert seo.description("<p>In a <code>.nexy</code> page.</p>") == "In a .nexy page."

    def test_the_summary_closes_its_parentheses(self):
        html = "<p>Client mode (<code>useCSR = True</code>).</p>"
        assert seo.description(html) == "Client mode (useCSR = True)."

    def test_a_long_summary_stops_before_two_hundred_characters(self):
        text = seo.description(f"<p>{'word ' * 80}</p>")
        assert len(text) <= 200 and text.endswith("\u2026")

    def test_a_page_without_a_paragraph_has_no_summary(self):
        assert seo.description("<ul><li>Only a list</li></ul>") == ""


class TestAddress:
    def test_the_home_of_the_docs_ends_with_its_folder(self):
        assert seo.home("https://example.test/nexy") == "https://example.test/nexy/docs/"

    def test_a_page_lives_in_its_own_folder(self):
        assert seo.canonical("https://example.test", "guides/actions") == URL

    def test_the_docs_home_is_the_docs_folder(self):
        assert seo.canonical("https://example.test/nexy/", "") == "https://example.test/nexy/docs/"


class TestHead:
    def test_the_page_gives_its_canonical_address(self):
        assert f'<link rel="canonical" href="{URL}">' in _head()

    def test_the_page_can_be_crawled_and_previewed_large(self):
        assert 'content="index, follow, max-image-preview:large"' in _head()

    def test_the_page_reads_as_a_card(self):
        html = _head()
        assert '<meta property="og:title" content="Actions">' in html
        assert '<meta name="twitter:card" content="summary_large_image">' in html

    def test_the_card_shows_the_picture_of_the_site(self):
        assert '<meta property="og:image" content="https://example.test/assets/og.png">' in _head()

    def test_the_home_is_a_website_and_a_page_is_an_article(self):
        assert 'property="og:type" content="website"' in _head(page_type="WebPage")
        assert 'property="og:type" content="article"' in _head()

    def test_a_page_without_a_summary_writes_no_description_tag(self):
        html = _head(description="")
        assert 'name="description"' not in html and "og:description" not in html

    def test_every_value_is_escaped(self):
        assert "&quot;quoted&quot; &amp; &lt;b&gt;" in _head(title='A "quoted" & <b>bold</b>')

    def test_the_linked_data_survives_a_title_with_a_quote(self):
        assert _graph(_head(title='A "quoted" title'))[0]["headline"] == 'A "quoted" title'

    def test_the_linked_data_names_the_page_and_its_menu(self):
        graph = _graph(_head())
        assert [item["@type"] for item in graph] == ["TechArticle", "BreadcrumbList"]
        crumbs = graph[1]["itemListElement"]
        assert [crumb["name"] for crumb in crumbs] == ["Documentation", "Actions"]


class TestFiles:
    def test_the_sitemap_lists_each_address_once(self):
        xml = seo.sitemap([seo.home("https://example.test"), URL])
        assert xml.count("<url>") == 2 and URL in xml

    def test_the_sitemap_is_well_formed(self):
        assert seo.sitemap([]).startswith('<?xml version="1.0" encoding="UTF-8"?>\n<urlset')

    def test_robots_names_the_sitemap(self):
        assert "Sitemap: https://example.test/nexy/sitemap.xml" in seo.robots(
            "https://example.test/nexy/"
        )

    def test_robots_keeps_the_markdown_copies_out_of_the_index(self):
        assert "Disallow: /*.md$" in seo.robots("https://example.test")


@pytest.mark.parametrize("slug", ["", "guides/actions"])
def test_every_address_of_the_docs_ends_with_a_slash(slug):
    assert seo.canonical("https://example.test", slug).endswith("/")
