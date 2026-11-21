"""The posts of the blog: one Markdown file each in `content/posts/`, its name is its address.

A post opens with a header between two `---` lines, one `key: value` per line:

    ---
    title: One file, one post
    date: 2026-08-24
    summary: One sentence for the list of posts and for the feed.
    tags: markdown, writing
    ---

Each `## Section` of the text gets an anchor and a line in the table of contents of the post.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from html import unescape
from pathlib import Path

from markdown_it import MarkdownIt

POSTS = Path(__file__).resolve().parents[2] / "content" / "posts"
WORDS_PER_MINUTE = 220
REQUIRED = ("title", "date", "summary")

# Raw HTML in a post is shown as text: a post is Markdown, never a way to run a script.
_MARKDOWN = MarkdownIt("commonmark", {"html": False}).enable(["table", "strikethrough"])
_SECTION = re.compile(r"<h2>(.+?)</h2>")
_TAG = re.compile(r"<[^>]+>")


class PostError(ValueError):
    """A post the blog cannot read; the message names its file."""


@dataclass(frozen=True)
class Heading:
    anchor: str
    text: str


@dataclass(frozen=True)
class Post:
    slug: str
    title: str
    date: date
    summary: str
    tags: tuple[str, ...]
    html: str
    headings: tuple[Heading, ...]
    minutes: int

    @property
    def day(self) -> str:
        """The date as people write it: August 24, 2026."""
        return f"{self.date:%B} {self.date.day}, {self.date.year}"


def _header(text: str, name: str) -> tuple[dict[str, str], str]:
    """The `key: value` lines between the two `---`, and the Markdown after them."""
    if not text.startswith("---\n") or "\n---\n" not in text:
        raise PostError(f"{name}: a post starts with a header between two --- lines")
    head, body = text[4:].split("\n---\n", 1)
    fields = {key.strip(): value.strip() for key, _, value in map(_split, head.splitlines())}
    missing = [key for key in REQUIRED if not fields.get(key)]
    if missing:
        raise PostError(f"{name}: the header has no {', '.join(missing)}")
    return fields, body


def _split(line: str) -> tuple[str, str, str]:
    return line.partition(":")


def _date(text: str, name: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise PostError(f"{name}: {text} is not a date written as 2026-08-24") from None


def _anchored(html: str) -> tuple[str, tuple[Heading, ...]]:
    """Each `<h2>` with an id, and the list of them for the table of contents."""
    headings: list[Heading] = []
    seen: Counter[str] = Counter()

    def anchor(match: re.Match[str]) -> str:
        text = unescape(_TAG.sub("", match.group(1)))
        name = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
        seen[name] += 1
        heading = Heading(name if seen[name] == 1 else f"{name}-{seen[name]}", text)
        headings.append(heading)
        return f'<h2 id="{heading.anchor}">{match.group(1)}</h2>'

    return _SECTION.sub(anchor, html), tuple(headings)


def parse(text: str, slug: str) -> Post:
    """The post written in *text*, served at `/posts/<slug>`."""
    name = f"{slug}.md"
    fields, body = _header(text, name)
    html, headings = _anchored(_MARKDOWN.render(body))
    tags = (tag.strip().lower() for tag in fields.get("tags", "").split(","))
    return Post(
        slug=slug,
        title=fields["title"],
        date=_date(fields["date"], name),
        summary=fields["summary"],
        tags=tuple(tag for tag in tags if tag),
        html=html,
        headings=headings,
        minutes=max(1, math.ceil(len(body.split()) / WORDS_PER_MINUTE)),
    )


@lru_cache(maxsize=1)
def _read(files: tuple[tuple[Path, int, int], ...]) -> tuple[Post, ...]:
    found = (parse(path.read_text(encoding="utf-8"), path.stem) for path, *_ in files)
    return tuple(sorted(found, key=lambda post: post.date, reverse=True))


def all_posts() -> tuple[Post, ...]:
    """Every post, newest first. A file is read again once it changed: an edit shows on reload.

    A change is a new modification time or a new size: on a coarse clock (Windows), a file written
    right after it was read can keep its time."""
    stats = [(path, path.stat()) for path in sorted(POSTS.glob("*.md"))]
    return _read(tuple((path, stat.st_mtime_ns, stat.st_size) for path, stat in stats))


def find(slug: str) -> Post | None:
    return next((post for post in all_posts() if post.slug == slug), None)


def tagged(tag: str) -> tuple[Post, ...]:
    return tuple(post for post in all_posts() if tag in post.tags)


def tags() -> list[tuple[str, int]]:
    """Each tag and how many posts carry it, the most used first, then by name."""
    counts = Counter(tag for post in all_posts() for tag in post.tags)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def neighbours(post: Post) -> tuple[Post | None, Post | None]:
    """The post just newer than this one and the one just older; None at either end."""
    posts = all_posts()
    index = posts.index(post)
    newer = posts[index - 1] if index > 0 else None
    older = posts[index + 1] if index + 1 < len(posts) else None
    return newer, older
