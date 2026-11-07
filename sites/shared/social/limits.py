"""What each network accepts, and what a post must ship to be sendable at all.

Three limits decide everything: the length of a caption, the number of files, and the rules of a
LinkedIn document. The document ones are LinkedIn's own (same size on every page, 300 pages, 100 MB
at most); the ratios are the ones that survive a phone screen. Nothing here looks at pixels: that is
`cards.py`, which can open the files.
"""

from __future__ import annotations

from dataclasses import dataclass

from sites.shared.social import Item, Kind

__all__ = ["CAROUSEL", "LIMITS", "PLATFORMS", "Carousel", "Limit", "check"]

PLATFORMS = ("linkedin", "bluesky", "mastodon")


@dataclass(frozen=True)
class Limit:
    """What one network accepts for one post."""

    caption: int
    files: int


LIMITS = {
    "linkedin": Limit(caption=3000, files=20),
    "bluesky": Limit(caption=300, files=4),
    "mastodon": Limit(caption=500, files=4),
}


@dataclass(frozen=True)
class Carousel:
    """The LinkedIn document rules, as published by LinkedIn."""

    min_cards: int = 2
    max_cards: int = 300
    max_bytes: int = 100 * 1024 * 1024
    min_width: int = 400
    ratios: tuple[tuple[int, int], ...] = ((1, 1), (4, 5))


CAROUSEL = Carousel()


def check(item: Item) -> list[str]:
    """Every limit this item breaks, as sentences a human can act on."""
    problems = _captions(item)
    problems.extend(_media(item))
    return problems


def _captions(item: Item) -> list[str]:
    problems: list[str] = []
    for platform in item.platforms:
        limit = LIMITS.get(platform)
        if limit is None:
            problems.append(f"{item.name()}: {platform!r} is not one of {', '.join(PLATFORMS)}")
            continue
        if len(item.body) > limit.caption:
            problems.append(
                f"{item.name()}: {len(item.body)} characters for {platform}, "
                f"which accepts {limit.caption}"
            )
        if item.media is not None and item.media.size() > limit.files:
            problems.append(
                f"{item.name()}: {item.media.size()} files for {platform}, "
                f"which accepts {limit.files}"
            )
    return problems


def _media(item: Item) -> list[str]:
    media = item.media
    if media is None:
        return []
    problems = _unreadable(item)
    if not media.alts:
        problems.append(f"{item.name()}: no `alt`, so nobody who cannot see it gets anything")
    elif len(media.alts) != media.size():
        problems.append(
            f"{item.name()}: {len(media.alts)} `alt` for {media.size()} file(s), one per file"
        )
    if media.kind is Kind.CAROUSEL:
        problems.extend(_carousel(item))
    if media.kind is Kind.VIDEO and not (item.directory / "transcript.md").is_file():
        problems.append(f"{item.name()}: a video ships a transcript.md, for people who watch muted")
    return problems


def _carousel(item: Item) -> list[str]:
    media = item.media
    if media is None:
        return []
    problems: list[str] = []
    if not CAROUSEL.min_cards <= media.size() <= CAROUSEL.max_cards:
        problems.append(
            f"{item.name()}: {media.size()} cards, a document wants "
            f"{CAROUSEL.min_cards} to {CAROUSEL.max_cards}"
        )
    total = sum(path.stat().st_size for path in media.files)
    if total > CAROUSEL.max_bytes:
        problems.append(f"{item.name()}: {total // 1024} KiB of cards, the limit is 100 MiB")
    return problems


def _unreadable(item: Item) -> list[str]:
    media = item.media
    if media is None:
        return []
    return [
        f"{item.name()}: {path.name} is empty, replace the placeholder with the real file"
        for path in media.files
        if path.stat().st_size == 0
    ]
