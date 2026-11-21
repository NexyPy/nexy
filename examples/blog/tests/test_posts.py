"""The posts: a header, Markdown, an anchor per section, and the order the blog shows them in."""

import os
from datetime import date

import pytest

from src.blog import posts
from src.blog.posts import PostError, parse

POST = """---
title: One file, one post
date: 2026-08-24
summary: How a post is written.
tags: Markdown, writing
---

Intro.

## The header

Text.

## Q&A

More text.
"""


def _write(folder, name, day, tags="nexy"):
    text = f"---\ntitle: {name}\ndate: {day}\nsummary: About {name}.\ntags: {tags}\n---\n\nText.\n"
    (folder / f"{name}.md").write_text(text, encoding="utf-8")


@pytest.fixture
def folder(tmp_path, monkeypatch):
    """Three posts in a folder of their own, written out of order."""
    monkeypatch.setattr(posts, "POSTS", tmp_path)
    _write(tmp_path, "middle", "2026-09-01", "nexy, python")
    _write(tmp_path, "newest", "2026-10-01", "python")
    _write(tmp_path, "oldest", "2026-08-01", "nexy")
    return tmp_path


def test_the_header_gives_the_title():
    assert parse(POST, "one-file").title == "One file, one post"


def test_the_header_gives_the_date():
    assert parse(POST, "one-file").date == date(2026, 8, 24)


def test_the_header_gives_the_summary():
    assert parse(POST, "one-file").summary == "How a post is written."


def test_tags_are_read_in_lower_case():
    assert parse(POST, "one-file").tags == ("markdown", "writing")


def test_the_date_reads_as_people_write_it():
    assert parse(POST, "one-file").day == "August 24, 2026"


def test_each_section_gets_an_anchor():
    assert '<h2 id="the-header">The header</h2>' in parse(POST, "one-file").html


def test_the_table_of_contents_follows_the_sections():
    assert [h.text for h in parse(POST, "one-file").headings] == ["The header", "Q&A"]


def test_two_sections_with_the_same_words_get_two_anchors():
    text = POST.replace("## Q&A", "## The header")
    assert [h.anchor for h in parse(text, "x").headings] == ["the-header", "the-header-2"]


def test_a_short_post_reads_in_one_minute():
    assert parse(POST, "one-file").minutes == 1


def test_a_long_post_reads_in_more_minutes():
    assert parse(POST + "word " * 700, "long").minutes == 4


def test_raw_html_is_shown_as_text():
    assert "<script>" not in parse(POST + "\n<script>alert(1)</script>\n", "x").html


def test_a_post_without_header_names_its_file():
    with pytest.raises(PostError, match="draft.md"):
        parse("Just text.", "draft")


def test_a_header_without_title_says_so():
    with pytest.raises(PostError, match="no title"):
        parse(POST.replace("title: One file, one post\n", ""), "draft")


def test_a_date_that_is_not_one_says_so():
    with pytest.raises(PostError, match="2026-13-01"):
        parse(POST.replace("2026-08-24", "2026-13-01"), "draft")


def test_an_edited_post_is_read_again(folder):
    posts.all_posts()
    _write(folder, "middle", "2026-09-01", "edited")
    assert posts.find("middle").tags == ("edited",)


def test_an_edit_that_keeps_the_modification_time_is_read_again(folder):
    # A coarse clock (Windows) can give the edited file the time it had when it was last read.
    posts.all_posts()
    before = (folder / "middle.md").stat().st_mtime_ns
    _write(folder, "middle", "2026-09-01", "edited")
    os.utime(folder / "middle.md", ns=(before, before))
    assert posts.find("middle").tags == ("edited",)


def test_every_post_of_the_blog_reads():
    assert len(posts.all_posts()) >= 5


@pytest.mark.usefixtures("folder")
class TestTheFolder:
    """Three posts of a folder of their own, read the way the pages read them."""

    def test_posts_come_newest_first(self):
        assert [post.slug for post in posts.all_posts()] == ["newest", "middle", "oldest"]

    def test_a_post_is_found_by_the_name_of_its_file(self):
        assert posts.find("middle").title == "middle"

    def test_an_unknown_name_finds_no_post(self):
        assert posts.find("nowhere") is None

    def test_a_tag_lists_its_posts_newest_first(self):
        assert [post.slug for post in posts.tagged("nexy")] == ["middle", "oldest"]

    def test_tags_are_counted_the_most_used_first(self):
        assert posts.tags() == [("nexy", 2), ("python", 2)]

    def test_the_newest_post_has_no_newer_one(self):
        assert posts.neighbours(posts.find("newest"))[0] is None

    def test_the_oldest_post_has_no_older_one(self):
        assert posts.neighbours(posts.find("oldest"))[1] is None

    def test_a_post_sits_between_its_neighbours(self):
        newer, older = posts.neighbours(posts.find("middle"))
        assert (newer.slug, older.slug) == ("newest", "oldest")
