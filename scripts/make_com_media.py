"""Draw the media of a COM item as a page, then photograph it.

    python scripts/make_com_media.py --slug 2026-11-six-routes
    python scripts/make_com_media.py --slug 2026-11-six-routes --theme signal
    python scripts/make_com_media.py --check

A card is not painted pixel by pixel: it is HTML and CSS (`COM/design/cards.css`), rendered by
Chrome at twice the size and reduced to exactly 1080×1350. Type is then set by a browser, the way it
is on the page a reader will actually open, and a hairline stays one pixel wide on LinkedIn.

Everything a card shows is real: a file path that exists, a command that runs, a number from
`COM/proof/`. Nothing is generated: a model that has seen ten thousand landing pages would draw a
plausible `routes/[id].tsx`, and one wrong character in a file name is the only thing a developer
reads first.

`SPECS` holds one entry per item: the words on each card, and the composition under them. Editing a
card means editing this file and running the command.
"""

from __future__ import annotations

import argparse
import html
import shutil
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from playwright.sync_api import FloatRect, Page

REPO = Path(__file__).resolve().parent.parent
COM = REPO / "COM"
DESIGN = COM / "design"

CARD = (1080, 1350)
FIGURE = (1200, 675)
COVER = (1200, 630)
SCALE = 2
PAD_X = 88
PAD_BOTTOM = 68

THEMES = ("paper", "signal", "field")
CHROMES = (
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)


@dataclass(frozen=True)
class Sheet:
    """One page to shoot: its name in the item folder, its markup, its size and margins."""

    name: str
    markup: str
    size: tuple[int, int]
    pad_x: int = PAD_X
    pad_bottom: int = PAD_BOTTOM


@dataclass(frozen=True)
class Card:
    """One card: a headline, and the composition that proves it."""

    headline: str
    eyebrow: str = ""
    figure: str = ""


@dataclass(frozen=True)
class Spec:
    """One item's media: a carousel, a figure, or a cover."""

    kind: str
    theme: str = "paper"
    folder: str = "posts"
    eyebrow: str = ""
    cards: tuple[Card, ...] = ()
    title: str = ""
    subtitle: str = ""
    label: str = ""
    unit: str = ""
    runs: tuple[float, ...] = ()
    footnote: str = ""


# ---------- compositions: what sits under the headline ----------


def chip(path: str, name: str) -> str:
    """A file, drawn as a page: the path in grey, the name in the accent."""
    return (
        '<div class="chip"><span class="page"></span>'
        f'<span class="dir">{html.escape(path)}</span>'
        f'<span class="name">{html.escape(name)}</span></div>'
    )


def tree(rows: tuple[tuple[str, int, bool], ...]) -> str:
    """Folders and the file they become: the connector is the argument."""
    lines = [
        f'<div style="margin-left:{level * 38}px">'
        f'<span class="{"leaf" if leaf else ""}">{html.escape(text)}</span></div>'
        for text, level, leaf in rows
    ]
    return '<div class="tree">' + "".join(lines) + "</div>"


def code_panel(path: str, language: str, code: str) -> str:
    """A source file: the path on a bar, the code under it, unstyled by a highlighter."""
    return (
        '<div class="panel"><div class="bar">'
        f"<b>{html.escape(path)}</b><span>{html.escape(language)}</span></div>"
        f"<pre>{code}</pre></div>"
    )


def flow(left: str, right: str) -> str:
    """A request and its answer, one wire between them."""
    return (
        f'<div class="flow"><div class="node">{left}</div>'
        f'<div class="wire"></div><div class="node">{right}</div></div>'
    )


def host(address: str, rows: tuple[tuple[str, str, str], ...]) -> str:
    """One address, several answers: the claim of the project, as a table of routes."""
    body = "".join(
        f'<div class="row"><b>{html.escape(method)}</b>'
        f'<span class="path" style="color:inherit">{html.escape(path)}</span>'
        f"<span>{html.escape(source)}</span></div>"
        for method, path, source in rows
    )
    return (
        '<div class="host"><div class="addr">'
        f"<b>{html.escape(address)}</b><span>one origin</span></div>{body}</div>"
    )


# ---------- what each item says ----------

SPECS: dict[str, Spec] = {
    "repo-banner": Spec(
        kind="banner",
        theme="paper",
        folder="design",
        eyebrow="uvx nexy new",
        title="One file. One page. One origin.",
        subtitle="A route is a Python file. FastAPI and Vite run in one process.",
        label="nexypy.github.io/nexy/docs",
    ),
    "2026-11-page-in-1-6-ms": Spec(
        kind="figure",
        theme="signal",
        eyebrow="compile time",
        label="median of 25 compiles",
        unit="ms",
        footnote="routes/index.nexy · Ryzen 5 4500U · Python 3.13.15",
        runs=(
            1.99,
            1.86,
            2.18,
            1.71,
            1.91,
            1.66,
            1.49,
            1.51,
            1.60,
            1.55,
            1.56,
            1.58,
            1.62,
            1.63,
            1.60,
            1.61,
            1.62,
            1.71,
            1.63,
            1.66,
            1.94,
            2.16,
            1.88,
            1.98,
            2.34,
        ),
    ),
    "2026-11-six-routes": Spec(
        kind="carousel",
        theme="paper",
        eyebrow="file-based routing",
        cards=(
            Card(
                "A route is a file.",
                "one file, one page",
                chip("routes/", "about.nexy"),
            ),
            Card(
                "The folder is the URL.",
                "the path is the address",
                tree(
                    (
                        ("src/routes/", 0, False),
                        ("blog/", 1, False),
                        ("[slug].nexy", 2, True),
                    )
                ),
            ),
            Card(
                "Markdown is a route.",
                "a page with no component",
                code_panel(
                    "routes/changelog.md",
                    "markdown",
                    "# Changelog\n\n- 2.2.2 - 2026-11-05",
                ),
            ),
            Card(
                "React is a route too.",
                "client mode, no glue",
                code_panel(
                    "routes/counter.tsx",
                    "tsx",
                    "export default function Counter() {\n  const [n, setN] = useState(0)",
                ),
            ),
            Card(
                "Python is the API.",
                "the file is the endpoint",
                flow("GET /api/users", '{"users": []}'),
            ),
            Card(
                "One origin. No CORS.",
                "pages and json, same host",
                host(
                    "localhost:3000",
                    (("GET", "/", "index.nexy"), ("GET", "/api/users", "users.py")),
                ),
            ),
        ),
    ),
    "2026-11-why-a-file-is-a-route": Spec(
        kind="cover",
        theme="field",
        folder="blogs",
        eyebrow="routing / file-based",
        title="Why a route is a file",
        subtitle="one file per page, and the URL is its path",
    ),
}


def main(argv: list[str] | None = None) -> int:
    """Draw one item, or check that every item can be drawn and fits its margins."""
    args = _parser().parse_args(argv)
    if args.check:
        return _check()
    spec = SPECS.get(args.slug)
    if spec is None:
        print(f"no spec for {args.slug!r}: add one to SPECS in {Path(__file__).name}")
        return 1
    theme = args.theme or spec.theme
    folder = COM / spec.folder / args.slug
    names = draw(spec, folder, theme)
    for name in names:
        print(f"{name}  {_size(folder / name)}  {theme}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render COM media from HTML and CSS.")
    parser.add_argument("--slug", help="the item to draw, e.g. 2026-11-six-routes")
    parser.add_argument("--theme", choices=THEMES, help="the ground of the card")
    parser.add_argument("--check", action="store_true", help="draw every spec into a temp folder")
    return parser


def draw(spec: Spec, folder: Path, theme: str | None = None) -> list[str]:
    """Write the media into the item folder and return the names written."""
    folder.mkdir(parents=True, exist_ok=True)
    sheets = _sheets(spec, theme or spec.theme)
    with _session() as page:
        for sheet in sheets:
            _shoot(page, sheet.markup, folder / sheet.name, sheet.size)
            _audit(page, sheet)
    return [sheet.name for sheet in sheets]


def _sheets(spec: Spec, theme: str) -> list[Sheet]:
    if spec.kind == "figure":
        return [Sheet("image.png", _figure(spec, theme), FIGURE, pad_x=64, pad_bottom=48)]
    if spec.kind == "cover":
        return [Sheet("cover.png", _cover(spec, theme), COVER, pad_x=64, pad_bottom=48)]
    if spec.kind == "banner":
        return [Sheet("banner.png", _banner(spec, theme), COVER, pad_x=64, pad_bottom=48)]
    return [
        Sheet(f"carousel/{index:02d}.png", _card(card, index, len(spec.cards), spec, theme), CARD)
        for index, card in enumerate(spec.cards, start=1)
    ]


def _check() -> int:
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as scratch:
        for slug, spec in SPECS.items():
            for theme in THEMES if spec.kind == "carousel" else (spec.theme,):
                try:
                    draw(spec, Path(scratch) / f"{slug}-{theme}", theme)
                except (OSError, RuntimeError, ValueError) as failure:
                    print(f"{slug} ({theme}): {failure}")
                    return 1
            print(f"{slug}: drawn")
    return 0


# ---------- markup ----------


def _card(card: Card, index: int, total: int, spec: Spec, theme: str) -> str:
    """One page of the carousel: eyebrow, headline, composition, footer."""
    eyebrow = card.eyebrow or spec.eyebrow
    body = (
        f'<div class="card-top">{_eyebrow(eyebrow)}'
        f'<span class="index">{index:02d}<s>/</s>{total:02d}</span></div>'
        f'<div class="card-body"><h1 class="headline">{html.escape(card.headline)}</h1>'
        f'<div class="figure">{card.figure}</div></div>'
        f'<div class="card-foot"><span class="mark">nx</span>'
        f"<span>nexy · file-based routing</span></div>"
    )
    markup = f'<article class="card theme-{theme}"><div class="card-grid"></div>{body}</article>'
    return _document(theme, markup)


def _figure(spec: Spec, theme: str) -> str:
    """The benchmark: the median as a number, the 25 runs as bars."""
    median = sorted(spec.runs)[len(spec.runs) // 2]
    body = (
        f'<div class="card-top">{_eyebrow(spec.eyebrow)}'
        f'<span class="index">{len(spec.runs)} runs</span></div>'
        f'<div class="body"><div class="number"><div class="big">{median:.2f}'
        f"<small>{html.escape(spec.unit)}</small></div>"
        f'<div class="big-label">{html.escape(spec.label)}<br>{html.escape(spec.footnote)}</div>'
        f'</div><div class="bars">{_bars(spec.runs, median)}</div></div>'
        f'<div class="card-foot"><span class="mark">nx</span>'
        f"<span>nexy · 2026-11-06</span></div>"
    )
    return _document(theme, f'<article class="figure-wide theme-{theme}">{body}</article>')


def _cover(spec: Spec, theme: str) -> str:
    """A blog cover: the title, one line under it, the monogram."""
    body = (
        f'<div class="card-top">{_eyebrow(spec.eyebrow)}<span class="index">blog</span></div>'
        f'<h1 class="headline">{html.escape(spec.title)}</h1>'
        f'<div class="sub">{html.escape(spec.subtitle)}</div>'
        f'<div class="card-foot"><span class="mark">nx</span>'
        f"<span>nexypy.github.io/nexy</span></div>"
    )
    return _document(theme, f'<article class="cover theme-{theme}">{body}</article>')


def _banner(spec: Spec, theme: str) -> str:
    """The repository banner: the template's own logo, the claim, and the command that runs."""
    logo = (
        '<img class="logo" alt="Nexy" height="40"'
        ' src="../../nexy/modules/cli/templates/_shared/web/public/nexy.svg">'
    )
    body = (
        f'<div class="lockup">{logo}</div>'
        f'<h1 class="headline">{html.escape(spec.title)}</h1>'
        f'<div class="sub">{html.escape(spec.subtitle)}</div>'
        f'<div class="card-foot"><span class="mark">{html.escape(spec.eyebrow)}</span>'
        f"<span>{html.escape(spec.label)}</span></div>"
    )
    return _document(theme, f'<article class="cover banner theme-{theme}">{body}</article>')


def _eyebrow(text: str) -> str:
    return f'<span class="eyebrow"><b></b>{html.escape(text)}</span>'


def _bars(runs: tuple[float, ...], median: float) -> str:
    top = max(runs)
    hot = max(index for index, run in enumerate(runs) if run == median)
    return "".join(
        f'<i class="{"hot" if index == hot else ""}" style="height:{round(run / top * 188)}px"></i>'
        for index, run in enumerate(runs)
    )


def _document(theme: str, body: str) -> str:
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        '<link rel="stylesheet" href="cards.css"></head>'
        f'<body class="theme-{theme}">{body}</body></html>'
    )


# ---------- browser ----------


@contextmanager
def _session() -> Iterator[Page]:
    """One Chrome, one page, at twice the size: the cards are shot in one run."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=_chrome(), args=["--no-sandbox"])
        try:
            yield browser.new_page(
                viewport={"width": CARD[0], "height": CARD[1]}, device_scale_factor=SCALE
            )
        finally:
            browser.close()


def _chrome() -> str | None:
    found = next((path for path in CHROMES if Path(path).is_file()), None)
    return found or shutil.which("google-chrome") or shutil.which("chromium")


def _shoot(page: Page, markup: str, target: Path, size: tuple[int, int]) -> None:
    """Load the page from disk, wait for the fonts, and shoot it at 2x."""
    source = DESIGN / ".render.html"
    source.write_text(markup, encoding="utf-8")
    try:
        page.goto(source.as_uri())
        page.evaluate("() => document.fonts.ready.then(() => true)")
        shot = target.with_suffix(".2x.png")
        page.screenshot(path=str(shot), clip=_clip(size))
        with Image.open(shot) as image:
            resample = Image.Resampling.LANCZOS
            image.convert("RGB").resize(size, resample).save(target, optimize=True)
        shot.unlink()
    finally:
        source.unlink(missing_ok=True)


def _clip(size: tuple[int, int]) -> FloatRect:
    return {"x": 0, "y": 0, "width": float(size[0]), "height": float(size[1])}


def _audit(page: Page, sheet: Sheet) -> None:
    """Refuse a card whose text leaves the margin, overflows, or lost its typeface."""
    boxes = page.evaluate(_PROBE)
    problems = _problems(boxes, sheet) + _missing_fonts(boxes)
    if problems:
        raise RuntimeError(f"{sheet.name}: " + "; ".join(problems))


_PROBE = """() => {
  const box = (sel) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return {x: r.x, y: r.y, w: r.width, h: r.height,
            over: el.scrollWidth - el.clientWidth, tall: el.scrollHeight - el.clientHeight};
  };
  return {top: box('.card-top'), body: box('.card-body'), foot: box('.card-foot'),
          head: box('.headline'), figure: box('.figure') || box('.bars'),
          fonts: [document.fonts.check('800 118px Archivo'),
                  document.fonts.check('400 30px "JetBrains Mono"')]};
}"""


def _missing_fonts(boxes: dict[str, object]) -> list[str]:
    loaded = boxes.get("fonts")
    if isinstance(loaded, list) and all(loaded):
        return []
    return ["Archivo or JetBrains Mono did not load"]


def _problems(boxes: dict[str, dict[str, float] | None], sheet: Sheet) -> list[str]:
    width, height = sheet.size
    pad_x, pad_bottom = sheet.pad_x, sheet.pad_bottom
    found: list[str] = []
    for key in ("top", "body", "foot", "head", "figure"):
        box = boxes.get(key)
        if box is None:
            continue
        if box["x"] < pad_x - 1 or box["x"] + box["w"] > width - pad_x + 1:
            found.append(f"{key} leaves the side margin")
        if box["y"] + box["h"] > height - pad_bottom + 1:
            found.append(f"{key} runs past the footer")
        if box["over"] > 1:
            found.append(f"{key} overflows its box")
    body, foot = boxes.get("body"), boxes.get("foot")
    if body and foot and body["y"] + body["h"] > foot["y"] + 1:
        found.append("the body touches the footer")
    return found


def _size(path: Path) -> str:
    with Image.open(path) as image:
        return f"{image.width}x{image.height}"


if __name__ == "__main__":
    sys.exit(main())
