"""What a `COM/` item is: one folder, one post or one blog, in one language.

The folder name carries the date and the slug, the frontmatter (`+++`, TOML) carries the metadata,
the body carries the words and the media sits next to them. Nothing here renders, publishes or
measures anything: the rules live in `limits`, `voice` and `cards`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from pathlib import Path

__all__ = ["CATEGORIES", "ComError", "Item", "Kind", "Media"]


class ComError(Exception):
    """A `COM/` folder that cannot be read, or that breaks a rule we publish."""


class Kind(StrEnum):
    """The media a post carries. The folder decides it, never the frontmatter."""

    IMAGE = "image"
    CAROUSEL = "carousel"
    VIDEO = "video"


CATEGORIES = ("posts", "blogs")


@dataclass(frozen=True)
class Media:
    """The files of one post, with one description per file, for screen readers."""

    kind: Kind
    files: tuple[Path, ...]
    alts: tuple[str, ...] = ()

    def size(self) -> int:
        """How many files the post ships: one image, one video, or every card."""
        return len(self.files)


@dataclass(frozen=True)
class Item:
    """One post or one blog, in one language. A language variant is an item of its own."""

    directory: Path
    category: str
    slug: str
    lang: str
    published: date
    body: str
    title: str | None = None
    description: str | None = None
    platforms: tuple[str, ...] = ()
    link: str | None = None
    cta: str = ""
    ask: str = "none"
    proof: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    canonical: str | None = None
    cover: str | None = None
    media: Media | None = None
    stem: str = "post"

    def name(self) -> str:
        """`posts/2026-11-slug.fr`, the name a human reads in a report."""
        return f"{self.category}/{self.slug}.{self.lang}"
