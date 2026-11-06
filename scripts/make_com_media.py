"""Draw the media of one COM item with type only: a terminal capture, or the cards of a carousel.

    python scripts/make_com_media.py --slug 2026-11-page-in-1-6-ms
    python scripts/make_com_media.py --slug 2026-11-six-routes
    python scripts/make_com_media.py --check          # every spec, in a temporary folder

There is no illustration in `COM/` (see `COM/BRAND.md`): a post shows a terminal, a browser, or a
card. This script draws the two we can draw from text, at the sizes the brand pins, so a card is
reproducible instead of hand-made once and never again.

The copy lives in `SPECS`, one entry per item slug: the same text a reader sees on the card, and the
verbatim output of the command a terminal capture shows. Editing a card means editing this file and
running the command, not opening an image editor.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
COM = REPO / "COM"

PAPER = "#fafafa"
INK = "#0a0a0a"
MUTED = "#52525b"
ACCENT = "#0f766e"
ACCENT_LIT = "#5eead4"

CARD = (1080, 1350)
TERMINAL = (1200, 675)
MARGIN = 64
FOOTER = 40
HEADLINE = 92
CODE = 56
CAPTURE = 24

FONT_DIRS = (
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/TTF",
    "/Library/Fonts",
    "/System/Library/Fonts/Supplemental",
)
FACES = {
    "sans": "DejaVuSans.ttf",
    "bold": "DejaVuSans-Bold.ttf",
    "mono": "DejaVuSansMono.ttf",
    "mono-bold": "DejaVuSansMono-Bold.ttf",
}


@dataclass(frozen=True)
class Card:
    """One card: a headline, and the one line of code that proves it."""

    headline: str
    code: str = ""


@dataclass(frozen=True)
class Spec:
    """One item's media: a terminal capture, or a numbered set of cards."""

    kind: str
    title: str = ""
    capture: tuple[str, ...] = ()
    cards: tuple[Card, ...] = ()
    folder: str = "posts"
    extras: dict[str, str] = field(default_factory=dict)


SPECS: dict[str, Spec] = {
    "2026-11-page-in-1-6-ms": Spec(
        kind="terminal",
        title="25 compiles of one route, Python 3.13, Ryzen 5 4500U",
        capture=(
            "$ uv run python bench.py",
            "25 compiles of routes/index.nexy, warm-up excluded",
            "",
            "median   1.66 ms",
            "min      1.49 ms",
            "max      2.34 ms",
            "",
            "1.99, 1.86, 2.18, 1.71, 1.91, 1.66, 1.49, 1.51, 1.60, 1.55,",
            "1.56, 1.58, 1.62, 1.63, 1.60, 1.61, 1.62, 1.71, 1.63, 1.66,",
            "1.94, 2.16, 1.88, 1.98, 2.34",
        ),
    ),
    "2026-11-six-routes": Spec(
        kind="carousel",
        cards=(
            Card("A file is a route.", "routes/about.nexy"),
            Card("The folder is the URL.", "routes/blog/[slug].nexy"),
            Card("Markdown is a route.", "routes/changelog.md"),
            Card("Your React file is an island.", "routes/counter.tsx"),
            Card("Your Python is the API.", "routes/hello.py"),
            Card("One origin. One port.", "nx dev  ->  :8000"),
        ),
    ),
}


def main(argv: list[str] | None = None) -> int:
    """Draw the media of one item, or check every spec can be drawn."""
    args = _parser().parse_args(argv)
    if args.check:
        return _check()
    spec = SPECS.get(args.slug)
    if spec is None:
        print(f"no spec for {args.slug!r}: add one to SPECS in {Path(__file__).name}")
        return 1
    folder = COM / spec.folder / args.slug
    names = draw(spec, folder)
    for name in names:
        print(f"{name}  {_size(folder / name)}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Draw COM media from its text spec.")
    parser.add_argument("--slug", help="the item to draw, e.g. 2026-11-six-routes")
    parser.add_argument("--check", action="store_true", help="draw every spec into a temp folder")
    return parser


def draw(spec: Spec, folder: Path) -> list[str]:
    """Write the media into the item folder and return the names written."""
    if spec.kind == "terminal":
        folder.mkdir(parents=True, exist_ok=True)
        image = _capture(spec)
        image.save(folder / "image.png")
        return ["image.png"]
    cards = folder / "carousel"
    cards.mkdir(parents=True, exist_ok=True)
    names = []
    for index, card in enumerate(spec.cards, start=1):
        name = f"{index:02d}.png"
        _card(card, index, len(spec.cards)).save(cards / name)
        names.append(f"carousel/{name}")
    return names


def _check() -> int:
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as scratch:
        for slug, spec in SPECS.items():
            try:
                draw(spec, Path(scratch) / slug)
            except (OSError, ValueError) as failure:
                print(f"{slug}: {failure}")
                return 1
            print(f"{slug}: drawn")
    return 0


def _font(face: str, size: int) -> ImageFont.FreeTypeFont:
    name = FACES[face]
    for directory in FONT_DIRS:
        path = Path(directory) / name
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    raise ValueError(f"{name} not found: install DejaVu fonts, or add its folder to FONT_DIRS")


def _wrap(text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if font.getlength(candidate) <= width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    return [*lines, current] if current else lines


def _block(
    draw_: ImageDraw.ImageDraw,
    lines: list[str],
    xy: tuple[int, int],
    font: ImageFont.FreeTypeFont,
    fill: str,
    step: int,
) -> int:
    x, y = xy
    for line in lines:
        draw_.text((x, y), line, font=font, fill=fill)
        y += step
    return y


def _card(card: Card, index: int, total: int) -> Image.Image:
    dark = index % 2 == 0
    back, front = (INK, PAPER) if dark else (PAPER, INK)
    accent = ACCENT_LIT if dark else ACCENT
    image = Image.new("RGB", CARD, back)
    draw_ = ImageDraw.Draw(image)
    headline = _wrap(card.headline, _font("bold", HEADLINE), CARD[0] - 2 * MARGIN)
    y = _block(draw_, headline, (MARGIN, 360), _font("bold", HEADLINE), front, int(HEADLINE * 1.15))
    if card.code:
        lines = _wrap(card.code, _font("mono", CODE), CARD[0] - 2 * MARGIN)
        _block(draw_, lines, (MARGIN, y + 40), _font("mono", CODE), accent, int(CODE * 1.3))
    _footer(draw_, front, dark, index, total)
    return image


def _footer(draw_: ImageDraw.ImageDraw, front: str, dark: bool, index: int, total: int) -> None:
    y = CARD[1] - MARGIN - FOOTER
    mono = _font("mono", FOOTER)
    draw_.text((MARGIN, y), "nx", font=mono, fill=front if dark else INK)
    position = f"{index} / {total}"
    draw_.text((CARD[0] - MARGIN - mono.getlength(position), y), position, font=mono, fill=MUTED)


def _capture(spec: Spec) -> Image.Image:
    image = Image.new("RGB", TERMINAL, INK)
    draw_ = ImageDraw.Draw(image)
    mono = _font("mono", CAPTURE)
    title = _font("sans", 20)
    draw_.text((MARGIN, 40), spec.title, font=title, fill=MUTED)
    width = TERMINAL[0] - 2 * MARGIN
    lines: list[str] = []
    for line in spec.capture:
        lines.extend(_wrap(line, mono, width) if line else [""])
    y = 110
    for line in lines:
        draw_.text((MARGIN, y), line, font=mono, fill=_capture_fill(line))
        y += int(CAPTURE * 1.6)
    return image


def _capture_fill(line: str) -> str:
    """The summary lines carry the accent; everything else is plain terminal text."""
    return ACCENT_LIT if line.split()[:1] in (["median"], ["min"], ["max"]) else PAPER


def _size(path: Path) -> str:
    with Image.open(path) as image:
        return f"{image.width}x{image.height}"


if __name__ == "__main__":
    sys.exit(main())
