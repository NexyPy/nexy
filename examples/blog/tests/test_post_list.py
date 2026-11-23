"""A list of posts: one row per post, each linking to it."""

from nexy.testing import render

from src.blog.posts import all_posts


def test_each_post_gets_a_row():
    html = render("src/components/PostList.nexy", posts=all_posts())
    assert html.count('class="blog-row"') == len(all_posts())


def test_a_row_links_to_its_post():
    post = all_posts()[0]
    assert f'href="/posts/{post.slug}"' in render("src/components/PostList.nexy", posts=(post,))


def test_a_title_that_looks_like_markup_stays_text():
    post = all_posts()[0]
    tricky = type(post)(**{**post.__dict__, "title": "<b>Bold</b>"})
    assert "&lt;b&gt;Bold" in render("src/components/PostList.nexy", posts=(tricky,))
