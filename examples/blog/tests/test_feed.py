"""The RSS feed: well-formed XML, one item per post, absolute links and escaped text."""

from datetime import date
from xml.etree import ElementTree

from src.blog import posts
from src.blog.posts import Post
from src.routes import rss

TRICKY = Post("q-and-a", "Q&A: <html> in posts", date(2026, 10, 5), "A & B", (), "", (), 1)


def _items(text: str) -> list[ElementTree.Element]:
    return ElementTree.fromstring(text).findall("./channel/item")


def test_the_feed_has_one_item_per_post():
    assert len(_items(rss.feed())) == len(posts.all_posts())


def test_the_newest_post_comes_first():
    assert _items(rss.feed())[0].findtext("title") == posts.all_posts()[0].title


def test_each_link_is_absolute():
    link = _items(rss.feed())[0].findtext("link")
    assert link == f"{rss.site()}/posts/{posts.all_posts()[0].slug}"


def test_text_that_looks_like_markup_stays_text(monkeypatch):
    monkeypatch.setattr(rss, "all_posts", lambda: (TRICKY,))
    assert _items(rss.feed())[0].findtext("title") == "Q&A: <html> in posts"


def test_dates_are_written_the_way_rss_reads_them(monkeypatch):
    monkeypatch.setattr(rss, "all_posts", lambda: (TRICKY,))
    assert _items(rss.feed())[0].findtext("pubDate") == "Mon, 05 Oct 2026 00:00:00 +0000"


def test_the_site_has_no_trailing_slash():
    assert not rss.site().endswith("/")


def test_the_feed_answers_as_rss(client):
    assert client.get("/rss").headers["content-type"].startswith("application/rss+xml")
