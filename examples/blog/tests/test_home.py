"""The home page: the latest post first, then every other one."""

from html import escape

from src.blog.posts import all_posts


def test_the_home_page_lists_every_post(client):
    html = client.get("/").text
    assert all(escape(post.title) in html for post in all_posts())


def test_the_newest_post_leads_the_home_page(client):
    html = client.get("/").text
    newest, next_one = all_posts()[:2]
    assert html.index(escape(newest.title)) < html.index(escape(next_one.title))


def test_the_home_page_describes_the_blog(client):
    assert '<meta name="description"' in client.get("/").text
