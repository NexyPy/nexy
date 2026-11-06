"""Each network accepts one length and one number of files: say so before the post ships."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from sites.shared.social import Item, Kind, Media, limits


def _item(tmp_path: Path, **given: object) -> Item:
    facts: dict[str, object] = {
        "directory": tmp_path,
        "category": "posts",
        "slug": "2026-11-hmr",
        "lang": "en",
        "published": date(2026, 11, 6),
        "body": "47 ms.",
        "platforms": ("linkedin",),
        **given,
    }
    return Item(**facts)  # type: ignore[arg-type]


def _media(tmp_path: Path, kind: Kind, count: int, alts: tuple[str, ...]) -> Media:
    files = []
    for index in range(count):
        path = tmp_path / f"{index:02d}.png"
        path.write_bytes(b"x")
        files.append(path)
    return Media(kind=kind, files=tuple(files), alts=alts)


def test_a_post_within_every_limit_has_nothing_to_fix(tmp_path: Path) -> None:
    assert limits.check(_item(tmp_path)) == []


def test_an_unknown_platform_is_reported(tmp_path: Path) -> None:
    problems = limits.check(_item(tmp_path, platforms=("x",)))
    assert "'x' is not one of" in problems[0]


def test_a_caption_longer_than_the_network_accepts_is_reported(tmp_path: Path) -> None:
    problems = limits.check(_item(tmp_path, platforms=("bluesky",), body="a" * 301))
    assert "301 characters for bluesky" in problems[0]


def test_more_files_than_the_network_accepts_is_reported(tmp_path: Path) -> None:
    media = _media(tmp_path, Kind.IMAGE, 5, ("one", "two", "three", "four", "five"))
    problems = limits.check(_item(tmp_path, platforms=("bluesky",), media=media))
    assert "5 files for bluesky" in problems[0]


def test_an_image_without_alt_is_reported(tmp_path: Path) -> None:
    media = _media(tmp_path, Kind.IMAGE, 1, ())
    assert "no `alt`" in limits.check(_item(tmp_path, media=media))[0]


def test_one_alt_per_card_is_required(tmp_path: Path) -> None:
    media = _media(tmp_path, Kind.CAROUSEL, 2, ("one",))
    assert "2 file(s), one per file" in limits.check(_item(tmp_path, media=media))[0]


def test_a_carousel_of_one_card_is_reported(tmp_path: Path) -> None:
    media = _media(tmp_path, Kind.CAROUSEL, 1, ("one",))
    assert "1 cards" in limits.check(_item(tmp_path, media=media))[0]


def test_an_empty_placeholder_file_is_reported(tmp_path: Path) -> None:
    media = _media(tmp_path, Kind.IMAGE, 1, ("one",))
    media.files[0].write_bytes(b"")
    assert "is empty" in limits.check(_item(tmp_path, media=media))[0]


def test_a_video_without_a_transcript_is_reported(tmp_path: Path) -> None:
    media = _media(tmp_path, Kind.VIDEO, 1, ("one",))
    assert "transcript.md" in limits.check(_item(tmp_path, media=media))[0]


def test_a_video_with_a_transcript_is_accepted(tmp_path: Path) -> None:
    media = _media(tmp_path, Kind.VIDEO, 1, ("one",))
    (tmp_path / "transcript.md").write_text("47 ms.\n")
    assert limits.check(_item(tmp_path, media=media)) == []
