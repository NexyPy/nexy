"""The posts of the blog: Markdown files in `content/posts/`, read once and kept in memory.

A post starts with a header between two `---` lines, one `key: value` per line:

    ---
    title: Writing posts in Markdown
    date: 2026-11-12
    tags: writing, markdown
    summary: One sentence that the list and the feed show.
    ---
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import date
from functools import cache
from pathlib import Path

from markdown_it import MarkdownIt

POSTS = Path(__file__).resolve().parents[2] / "content" / "posts"
WORDS_PER_MINUTE = 220
HEADING = re.compile(r"<h2>(.+?)</h2>")


@dataclass(frozen=True)
class Post:
    slug: str
    title: str
    date: date
    tags: tuple[str, ...]
    summary: str
    html: str
    toc: tuple[tuple[str, str], ...]  # (anchor, heading) of each second-level heading
    minutes: int


def _header(text: str) -> tuple[dict[str, str], str]:
    """The `key: value` lines between the two `---`, and the Markdown after them."""
    _, head, body = text.split("---\n", 2)
    fields = dict(line.split(":", 1) for line in head.strip().splitlines())
    return {key.strip(): value.strip() for key, value in fields.items()}, body


def _plain(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html)


def _with_anchors(html: str) -> tuple[str, tuple[tuple[str, str], ...]]:
    """Give each `<h2>` an id, and list them for the table of contents."""
    toc: list[tuple[str, str]] = []

    def named(match: re.Match[str]) -> str:
        text = _plain(match.group(1))
        anchor = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
        toc.append((anchor, text))
        return f'<h2 id="{anchor}">{match.group(1)}</h2>'

    return HEADING.sub(named, html), tuple(toc)


def read(path: Path) -> Post:
    fields, body = _header(path.read_text(encoding="utf-8"))
    html, toc = _with_anchors(MarkdownIt("commonmark").enable("table").render(body))
    return Post(
        slug=path.stem,
        title=fields["title"],
        date=date.fromisoformat(fields["date"]),
        tags=tuple(tag.strip() for tag in fields.get("tags", "").split(",") if tag.strip()),
        summary=fields.get("summary", ""),
        html=html,
        toc=toc,
        minutes=max(1, math.ceil(len(body.split()) / WORDS_PER_MINUTE)),
    )


@cache
def all_posts() -> tuple[Post, ...]:
    """Every post, newest first."""
    posts = (read(path) for path in POSTS.glob("*.md"))
    return tuple(sorted(posts, key=lambda post: post.date, reverse=True))


def find(slug: str) -> Post | None:
    return next((post for post in all_posts() if post.slug == slug), None)


def tagged(tag: str) -> tuple[Post, ...]:
    return tuple(post for post in all_posts() if tag in post.tags)


def tags() -> list[tuple[str, int]]:
    """Each tag and how many posts carry it, the most used first."""
    counts: dict[str, int] = {}
    for post in all_posts():
        for tag in post.tags:
            counts[tag] = counts.get(tag, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def neighbours(slug: str) -> tuple[Post | None, Post | None]:
    """The newer and the older post around this one."""
    posts = all_posts()
    index = next(i for i, post in enumerate(posts) if post.slug == slug)
    newer = posts[index - 1] if index > 0 else None
    older = posts[index + 1] if index + 1 < len(posts) else None
    return newer, older
