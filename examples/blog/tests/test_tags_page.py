"""The page of every tag."""

from src.blog.posts import tags


def test_the_tags_page_lists_every_tag(client):
    html = client.get("/tags").text
    assert all(f'href="/tags/{tag}"' in html for tag, _ in tags())


def test_a_tag_says_how_many_posts_carry_it(client):
    tag, count = tags()[0]
    assert f'aria-label="{tag}, {count} posts"' in client.get("/tags").text
