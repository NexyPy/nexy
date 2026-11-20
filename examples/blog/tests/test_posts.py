"""The posts of content/posts/, as the pages and the feed read them."""

from datetime import date

from src.blog.posts import all_posts, find, neighbours, read, tagged, tags
from src.routes.rss import feed


def test_posts_come_newest_first():
    dates = [post.date for post in all_posts()]
    assert dates == sorted(dates, reverse=True)


def test_a_post_is_found_by_its_slug():
    assert find("hello-world").title == "Hello from a blog made with Nexy"


def test_an_unknown_slug_finds_nothing():
    assert find("nope") is None


def test_the_header_gives_the_date():
    assert find("hello-world").date == date(2026, 11, 2)


def test_the_header_gives_the_tags():
    assert find("hello-world").tags == ("nexy", "meta")


def test_each_second_level_heading_gets_an_anchor():
    assert '<h2 id="where-to-start">Where to start</h2>' in find("hello-world").html


def test_the_table_of_contents_lists_the_headings():
    assert find("hello-world").toc[0] == ("what-is-in-the-project", "What is in the project")


def test_a_short_post_reads_in_one_minute():
    assert find("hello-world").minutes == 1


def test_a_long_post_reads_in_more_minutes(tmp_path):
    path = tmp_path / "long.md"
    path.write_text("---\ntitle: Long\ndate: 2026-01-01\n---\n" + "word " * 700)
    assert read(path).minutes == 4


def test_the_newest_post_has_no_newer_one():
    assert neighbours(all_posts()[0].slug)[0] is None


def test_the_oldest_post_has_no_older_one():
    assert neighbours(all_posts()[-1].slug)[1] is None


def test_a_tag_lists_its_posts():
    assert [post.slug for post in tagged("rss")] == ["an-rss-feed"]


def test_the_most_used_tag_comes_first():
    assert tags()[0] == ("nexy", 3)


def test_the_feed_has_an_item_per_post():
    assert feed().count("<item>") == len(all_posts())


def test_the_feed_escapes_the_text():
    assert "&" not in feed().replace("&amp;", "").replace("&lt;", "").replace("&gt;", "")
