"""A link without a tag cannot be judged, so every link a post sends carries one."""

from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

from sites.shared.social import utm


def test_a_bare_url_gets_the_four_tags() -> None:
    query = parse_qs(
        urlsplit(utm.tagged("https://example.test/docs", "linkedin", "2026-11-hmr")).query
    )
    assert query["utm_source"] == ["linkedin"]


def test_the_campaign_is_the_slug_and_the_content_is_the_language() -> None:
    query = parse_qs(
        urlsplit(utm.tagged("https://example.test/", "bluesky", "2026-11-hmr", "fr")).query
    )
    assert (query["utm_campaign"], query["utm_content"]) == (["2026-11-hmr"], ["fr"])


def test_an_existing_query_is_kept() -> None:
    query = parse_qs(urlsplit(utm.tagged("https://example.test/?page=2", "mastodon", "slug")).query)
    assert query["page"] == ["2"]


def test_an_old_tag_is_replaced_not_repeated() -> None:
    tagged = utm.tagged("https://example.test/?utm_source=old", "linkedin", "slug")
    assert parse_qs(urlsplit(tagged).query)["utm_source"] == ["linkedin"]


def test_a_fragment_survives() -> None:
    assert utm.tagged("https://example.test/docs#build", "linkedin", "slug").endswith("#build")
