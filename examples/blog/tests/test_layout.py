"""What every page shares: its head, the header and the footer."""


def test_a_page_without_a_title_is_named_after_the_blog(client):
    assert "<title>Plain Text</title>" in client.get("/").text


def test_every_page_points_feed_readers_to_the_feed(client):
    assert '<link rel="alternate" type="application/rss+xml"' in client.get("/").text

