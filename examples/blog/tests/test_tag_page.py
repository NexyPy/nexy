"""The page of one tag: the posts that carry it, or a 404 for a tag no post has."""

from html import escape

from src.blog.posts import all_posts

NEWEST = all_posts()[0]


def test_a_tag_lists_its_posts(client):
    assert escape(NEWEST.title) in client.get(f"/tags/{NEWEST.tags[0]}").text


def test_a_tag_is_read_in_lower_case(client):
    assert client.get(f"/tags/{NEWEST.tags[0].upper()}").status_code == 200


def test_a_tag_no_post_carries_is_not_found(client):
    assert client.get("/tags/nothing-here").status_code == 404
