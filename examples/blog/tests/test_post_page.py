"""The page of one post: its text, its sections, its tab title, and the posts around it."""

from html import escape

from src.blog.posts import all_posts

NEWEST, OLDEST = all_posts()[0], all_posts()[-1]


def test_a_post_shows_its_text(client):
    assert NEWEST.html in client.get(f"/posts/{NEWEST.slug}").text


def test_a_post_links_each_of_its_sections(client):
    html = client.get(f"/posts/{NEWEST.slug}").text
    assert all(f'href="#{heading.anchor}"' in html for heading in NEWEST.headings)


def test_a_post_names_the_tab_after_itself(client):
    html = client.get(f"/posts/{NEWEST.slug}").text
    assert f"<title>{escape(NEWEST.title)} | Plain Text</title>" in html


def test_the_oldest_post_links_to_the_one_after_it(client):
    html = client.get(f"/posts/{OLDEST.slug}").text
    assert f'href="/posts/{all_posts()[-2].slug}"' in html


def test_an_unknown_post_is_not_found(client):
    assert client.get("/posts/nowhere").status_code == 404
