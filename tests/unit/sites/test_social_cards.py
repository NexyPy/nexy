"""Cards are read at feed size first, so the machine measures them before a human judges them."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from PIL import Image

from sites.shared.social import Item, Kind, Media, cards


def _card(directory: Path, name: str, size: tuple[int, int]) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    Image.new("RGB", size, "white").save(path)
    return path


def _item(tmp_path: Path, files: tuple[Path, ...], kind: Kind = Kind.CAROUSEL) -> Item:
    return Item(
        directory=tmp_path,
        category="posts",
        slug="2026-11-six-routers",
        lang="en",
        published=date(2026, 11, 6),
        body="Six routers.",
        media=Media(kind=kind, files=files, alts=tuple("card" for _ in files)),
    )


def test_sizes_are_read_from_the_file(tmp_path: Path) -> None:
    files = (_card(tmp_path, "01.png", (1080, 1350)),)
    assert cards.sizes(files) == [(1080, 1350)]


def test_a_carousel_of_matching_cards_has_nothing_to_fix(tmp_path: Path) -> None:
    files = tuple(_card(tmp_path, f"{index}.png", (1080, 1350)) for index in range(2))
    assert cards.check(_item(tmp_path, files)) == []


def test_two_page_sizes_are_reported(tmp_path: Path) -> None:
    files = (_card(tmp_path, "01.png", (1080, 1350)), _card(tmp_path, "02.png", (1080, 1080)))
    assert "same size" in cards.check(_item(tmp_path, files))[0]


def test_a_landscape_card_is_reported(tmp_path: Path) -> None:
    files = (_card(tmp_path, "01.png", (1600, 900)),)
    assert "square (1.00)" in cards.check(_item(tmp_path, files))[0]


def test_a_card_narrower_than_four_hundred_pixels_is_reported(tmp_path: Path) -> None:
    files = (_card(tmp_path, "01.png", (300, 300)),)
    assert "300 px wide" in cards.check(_item(tmp_path, files))[0]


def test_an_image_post_is_not_measured_as_a_carousel(tmp_path: Path) -> None:
    files = (_card(tmp_path, "image.png", (1200, 675)),)
    assert cards.check(_item(tmp_path, files, Kind.IMAGE)) == []


def test_pack_writes_one_pdf_for_the_cards(tmp_path: Path) -> None:
    files = tuple(_card(tmp_path / "carousel", f"{index}.png", (1080, 1350)) for index in range(2))
    target = cards.pack(_item(tmp_path, files), tmp_path / "build")
    assert target.read_bytes().startswith(b"%PDF")


def test_pack_refuses_an_item_without_a_carousel(tmp_path: Path) -> None:
    item = _item(tmp_path, (tmp_path / "image.png",), Kind.IMAGE)
    try:
        cards.pack(item, tmp_path / "build")
    except ValueError as error:
        assert "no carousel to pack" in str(error)
    else:
        raise AssertionError("packing an image as a carousel should fail")


def test_the_contact_sheet_is_one_image_of_every_card(tmp_path: Path) -> None:
    files = tuple(_card(tmp_path / "carousel", f"{index}.png", (1080, 1350)) for index in range(2))
    target = cards.contact_sheet(_item(tmp_path, files), tmp_path / "build")
    with Image.open(target) as sheet:
        assert sheet.height > 0
