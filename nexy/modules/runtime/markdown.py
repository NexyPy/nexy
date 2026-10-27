"""Markdown to HTML, and what a page derives from it: heading ids and a table of contents."""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from html import escape

import cmarkgfm  # type: ignore[import-untyped]

from nexy.core.config import Config

_HEADING_OPEN = re.compile(r"<h([1-6])(?:\s+[^>]*)?>", re.IGNORECASE)
_HEADING_CLOSE = {n: re.compile(rf"</h{n}>", re.IGNORECASE) for n in range(1, 7)}
_ID = re.compile(r'\s+id="([^"]+)"')
_TAG = re.compile(r"<[^>]+>")
_DEFAULT_DEPTH = (2, 6)


@dataclass(frozen=True)
class Heading:
    """A heading found in rendered HTML: where its opening tag is, its id and its text."""

    level: int
    open_start: int
    open_end: int
    id: str
    text: str


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "-", slug)


def render_markdown(content: str) -> str:
    """Render a markdown string to HTML using cmarkgfm (GFM)."""
    options = getattr(Config, "MARKDOWN_OPTIONS", 0)
    return str(cmarkgfm.github_flavored_markdown_to_html(content, options))


def scan_headings(html: str) -> Iterator[Heading]:
    """Each heading of *html* that has a closing tag and some text, in document order."""
    pos = 0
    while match := _HEADING_OPEN.search(html, pos):
        level = int(match.group(1))
        # Tag names are case-insensitive in HTML: `<H2>` closes with `</H2>`.
        closing = _HEADING_CLOSE[level].search(html, match.end())
        if closing is None:
            pos = match.end()
            continue
        text = _TAG.sub("", html[match.end() : closing.start()]).strip()
        pos = closing.end()
        if text:
            found = _ID.search(match.group(0))
            yield Heading(level, match.start(), match.end(), found.group(1) if found else "", text)


def inject_heading_ids(html: str) -> str:
    """Ensure every heading in HTML has an id attribute, adding slugs as needed."""
    parts: list[str] = []
    pos = 0
    for heading in scan_headings(html):
        if heading.id:
            continue
        opening = html[heading.open_start : heading.open_end]
        parts.append(html[pos : heading.open_start])
        parts.append(opening[:-1] + f' id="{_slugify(heading.text)}">')
        pos = heading.open_end
    parts.append(html[pos:])
    return "".join(parts)


def _depth_range(spec: str) -> tuple[int, int]:
    """``"2-4"`` as (2, 4), ``"3"`` as (3, 3); anything else is the default depth."""
    parts = spec.split("-")
    try:
        low = int(parts[0])
        return low, int(parts[1]) if len(parts) > 1 else low
    except ValueError:
        return _DEFAULT_DEPTH


def _link(heading: Heading) -> str:
    anchor = escape(heading.id or _slugify(heading.text), quote=True)
    return f'<li><a href="#{anchor}" class="toc-link">{escape(heading.text)}</a>'


def _nest(headings: list[Heading]) -> list[str]:
    """The list items of *headings*, nested one ``<ul>`` per level of depth."""
    lines = [_link(headings[0])]
    previous = headings[0].level
    for heading in headings[1:]:
        if heading.level > previous:
            lines += ["<ul>"] * (heading.level - previous)
        else:
            lines += ["</li></ul>"] * (previous - heading.level)
            lines.append("</li>")
        lines.append(_link(heading))
        previous = heading.level
    return [*lines, *["</li></ul>"] * (previous - headings[0].level + 1)]


def build_toc_html(html: str, depth_range: str = "2-6") -> str:
    """Extract headings from rendered HTML and build a hierarchical TOC."""
    low, high = _depth_range(depth_range)
    headings = [h for h in scan_headings(html) if low <= h.level <= high]
    if not headings:
        return ""
    return "\n".join(['<nav class="toc"><ul>', *_nest(headings), "</nav>"])


__all__ = [
    "render_markdown",
    "inject_heading_ids",
    "build_toc_html",
    "_slugify",
]
