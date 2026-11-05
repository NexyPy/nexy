"""The landing page of the docs: an introduction, then one card per Getting Started page.

Only the first track becomes cards: the rest of docs/ stays one click away in the menu, so the
reader meets the first path before a hundred pages.
"""

from __future__ import annotations

import html as htmllib
from pathlib import Path

from sites.shared import docs_source as source
from sites.shared import i18n
from sites.shared.icons import HOME_ART


def _introduction(docs: Path, link: source.Link, lang: str) -> source.Rendered:
    """The words of README.md before its first section, drawn like any page."""
    page = source.home(docs, lang)
    text = page.path.read_text(encoding="utf-8").split("\n## ", 1)[0]
    return source.render_fragment(text, page.path, docs, link)


def _card(page: source.Page, link: source.Link) -> str:
    art = HOME_ART.get(page.slug, HOME_ART[""])
    return (
        f'<a class="home-card" href="{link(page.slug)}" data-card="{page.slug}">'
        f'<span class="home-card-art">{art}</span>'
        f'<span class="home-card-title">{htmllib.escape(page.label)}</span>'
        f'<span class="home-card-text">{htmllib.escape(page.summary)}</span>'
        "</a>"
    )


def _group(group: source.Group, link: source.Link) -> tuple[str, source.Heading]:
    ident = source.anchor(group.title)
    cards = "".join(_card(page, link) for page in group.pages)
    heading = source.Heading(2, ident, group.title)
    block = (
        f'<h2 id="{ident}" data-group="{ident}">{htmllib.escape(group.title)}</h2>'
        f'<div class="home-cards">{cards}</div>'
    )
    return block, heading


def render(docs: Path, link: source.Link, lang: str = i18n.DEFAULT) -> source.Rendered:
    """The home page: its introduction, then one card per page of the first section."""
    intro = _introduction(docs, link, lang)
    blocks = [intro.html]
    headings = list(intro.headings)
    for group in source.read_tracks(docs, lang)[0].groups:
        block, heading = _group(group, link)
        blocks.append(block)
        headings.append(heading)
    return source.Rendered("".join(blocks), headings)
