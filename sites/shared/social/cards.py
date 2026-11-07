"""The cards of a carousel: are they readable on a phone, and do they make one document?

LinkedIn publishes three rules (same size on every page, 300 pages, 100 MB) and one piece of advice
that matters more than the rest: 1080×1350 or 1080×1080. A card is read at feed size first, so the
same cards are also assembled into one `-feed.png`: a contact sheet at thumbnail size, where a
carousel that cannot be read shows it in two seconds.

`pack` writes the PDF into `build/com/`, never into the repository: the cards are the source, the
document is a build artifact.
"""

from __future__ import annotations

from pathlib import Path

import img2pdf  # type: ignore[import-untyped]  # no stubs published; the call below is one line
from PIL import Image

from sites.shared.social import Item, Kind
from sites.shared.social.limits import CAROUSEL

__all__ = ["PACK_DIR", "check", "contact_sheet", "pack", "sizes"]

PACK_DIR = Path("build") / "com"
FEED_WIDTH = 270
SHEET_COLUMNS = 3
SHEET_GAP = 12
TOLERANCE = 0.01


def sizes(files: tuple[Path, ...]) -> list[tuple[int, int]]:
    """The pixel size of every card, read from the file itself."""
    found: list[tuple[int, int]] = []
    for path in files:
        with Image.open(path) as image:
            found.append((image.width, image.height))
    return found


def check(item: Item) -> list[str]:
    """Every pixel-level rule this carousel breaks."""
    media = item.media
    if media is None or media.kind is not Kind.CAROUSEL or not media.files:
        return []
    found = sizes(media.files)
    problems = _same_size(item, found)
    problems.extend(_shape(item, found[0]))
    return problems


def pack(item: Item, out_dir: Path = PACK_DIR) -> Path:
    """One PDF for LinkedIn, from the cards as they are, without re-encoding them."""
    media = item.media
    if media is None or media.kind is not Kind.CAROUSEL:
        raise ValueError(f"{item.name()}: there is no carousel to pack")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{item.slug}.pdf"
    target.write_bytes(img2pdf.convert([str(path) for path in media.files]))
    return target


def contact_sheet(item: Item, out_dir: Path = PACK_DIR) -> Path:
    """Every card at feed size, on one image: the two-second test before sending."""
    media = item.media
    if media is None or media.kind is not Kind.CAROUSEL:
        raise ValueError(f"{item.name()}: there is no carousel to show")
    thumbs = [_thumbnail(path) for path in media.files]
    sheet = _grid(thumbs)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{item.slug}-feed.png"
    sheet.save(target)
    return target


def _thumbnail(path: Path) -> Image.Image:
    with Image.open(path) as image:
        copy = image.convert("RGB")
    copy.thumbnail((FEED_WIDTH, FEED_WIDTH * 2))
    return copy


def _grid(thumbs: list[Image.Image]) -> Image.Image:
    columns = min(SHEET_COLUMNS, len(thumbs))
    rows = (len(thumbs) + columns - 1) // columns
    width = columns * FEED_WIDTH + (columns + 1) * SHEET_GAP
    height = rows * max(thumb.height for thumb in thumbs) + (rows + 1) * SHEET_GAP
    sheet = Image.new("RGB", (width, height), "white")
    for index, thumb in enumerate(thumbs):
        left = SHEET_GAP + (index % columns) * (FEED_WIDTH + SHEET_GAP)
        top = SHEET_GAP + (index // columns) * (thumb.height + SHEET_GAP)
        sheet.paste(thumb, (left, top))
    return sheet


def _same_size(item: Item, found: list[tuple[int, int]]) -> list[str]:
    if len(set(found)) == 1:
        return []
    return [
        f"{item.name()}: every page of a document has the same size, "
        f"found {len(set(found))} different ones"
    ]


def _shape(item: Item, size: tuple[int, int]) -> list[str]:
    width, height = size
    problems: list[str] = []
    if width < CAROUSEL.min_width:
        problems.append(
            f"{item.name()}: {width} px wide, LinkedIn reads {CAROUSEL.min_width} at least"
        )
    ratio = width / height if height else 0
    if not any(abs(ratio - wide / tall) < TOLERANCE for wide, tall in CAROUSEL.ratios):
        problems.append(
            f"{item.name()}: {width}×{height} is {ratio:.2f}, a card is square (1.00) or 4:5 (0.80)"
        )
    return problems
