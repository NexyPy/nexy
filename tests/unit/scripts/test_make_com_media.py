"""The media of a COM item is drawn from text, at the sizes the brand pins."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest
from PIL import Image

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "make_com_media.py"


def _load() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("make_com_media", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["make_com_media"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(name="media")
def media_fixture() -> types.ModuleType:
    return _load()


def test_a_terminal_capture_is_a_sixteen_by_nine_image(
    media: types.ModuleType, tmp_path: Path
) -> None:
    spec = media.SPECS["2026-11-page-in-1-6-ms"]
    media.draw(spec, tmp_path)
    with Image.open(tmp_path / "image.png") as image:
        assert (image.width, image.height) == (1200, 675)


def test_a_carousel_is_one_card_per_idea(media: types.ModuleType, tmp_path: Path) -> None:
    spec = media.SPECS["2026-11-six-routes"]
    names = media.draw(spec, tmp_path)
    assert len(names) == len(spec.cards) == 6


def test_every_card_is_four_by_five(media: types.ModuleType, tmp_path: Path) -> None:
    spec = media.SPECS["2026-11-six-routes"]
    media.draw(spec, tmp_path)
    with Image.open(tmp_path / "carousel" / "01.png") as image:
        assert (image.width, image.height) == (1080, 1350)


def test_cards_alternate_between_paper_and_ink(media: types.ModuleType, tmp_path: Path) -> None:
    spec = media.SPECS["2026-11-six-routes"]
    media.draw(spec, tmp_path)
    with (
        Image.open(tmp_path / "carousel" / "01.png") as first,
        Image.open(tmp_path / "carousel" / "02.png") as second,
    ):
        assert first.getpixel((0, 0)) != second.getpixel((0, 0))


def test_a_headline_wraps_inside_the_card_margin(media: types.ModuleType) -> None:
    font = media._font("bold", media.HEADLINE)
    lines = media._wrap("Your React file is an island.", font, media.CARD[0] - 2 * media.MARGIN)
    assert all(font.getlength(line) <= media.CARD[0] - 2 * media.MARGIN for line in lines)


def test_every_spec_slug_is_a_folder_name_com_accepts(media: types.ModuleType) -> None:
    from sites.shared.social import com

    assert all(com.SLUG.match(slug) for slug in media.SPECS)
