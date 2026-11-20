"""An address the blog does not serve: its own page, with the latest posts to go on with."""

from html import escape

from src.blog.posts import all_posts


def test_an_unknown_address_answers_404(client):
    assert client.get("/nowhere").status_code == 404


def test_the_page_is_the_blog_own(client):
    assert "This page is not here" in client.get("/nowhere").text


def test_the_page_offers_the_latest_post(client):
    assert escape(all_posts()[0].title) in client.get("/nowhere").text


def test_search_engines_leave_it_out(client):
    assert '<meta name="robots" content="noindex">' in client.get("/nowhere").text
