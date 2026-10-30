"""The pages of this site are the pages of docs/: read here, drawn by the components."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

from nexy.http import HTTPException

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from sites.shared import docs_source as source  # noqa: E402
from sites.shared import seo  # noqa: E402
from sites.shared.icons import ICONS, MARK  # noqa: E402

DOCS = REPO / "docs"
ASSETS = REPO / "sites" / "vanilla" / "assets"

# The address this site is published at: the canonical tag and the cards are absolute.
SITE_URL = "https://nexy.ai"

__all__ = [
    "ASSETS",
    "ICONS",
    "MARK",
    "SITE_URL",
    "area_select",
    "document",
    "head_of",
    "link",
    "markdown_link",
    "markdown_source",
    "menu",
    "search_entries",
    "slug_of",
    "title_of",
]


def link(slug: str) -> str:
    return f"/docs/{slug}" if slug else "/docs"


def slug_of(pathname: str) -> str:
    """The page a URL path shows: `/docs/guides/actions` is `guides/actions`."""
    return pathname.removeprefix("/docs").strip("/")


def _pages() -> list[tuple[source.Page, str]]:
    sections = source.read_sections(DOCS)
    return [(source.home(DOCS), "Documentation")] + [
        (p, s.title) for s in sections for p in s.pages
    ]


def _sections() -> list[source.Section]:
    return source.read_sections(DOCS)


def _area_sections(slug: str) -> list[source.Section]:
    """The sections of one area: the menu and the pager of a page stay inside its own area."""
    return source.in_area(_sections(), source.area_of(slug))


def area_select(slug: str) -> dict[str, Any]:
    """The choice above the menu: the area of the page, and a link to the start of each other."""
    here = source.area_of(slug)
    choices = []
    for area in source.AREAS:
        pages = [p for s in source.in_area(_sections(), area.slug) for p in s.pages]
        choices.append(
            {
                "slug": area.slug,
                "label": area.label,
                "blurb": area.blurb,
                "icon": ICONS[f"area_{area.slug}"],
                "home": link(pages[0].slug) if pages else link(""),
                "current": area.slug == here,
            }
        )
    return {"choices": choices, "shown": next(c for c in choices if c["current"])}


def title_of(slug: str) -> str:
    found = next((page.title for page, _ in _pages() if page.slug == slug), "Not found")
    return f"{found} - Nexy"


def head_of(slug: str) -> str:
    """What a crawler reads about a page: its summary, its address, its cards, the menu above it."""
    page = next((page for page, _ in _pages() if page.slug == slug), None)
    if page is None:
        return '<meta name="robots" content="noindex">'
    url = seo.canonical(SITE_URL, slug)
    rendered = source.render(page.path, DOCS, link)
    return seo.Head(
        title=page.title,
        description=seo.description(rendered.html),
        url=url,
        site_url=SITE_URL,
        trail=(("Documentation", seo.home(SITE_URL)), (page.label, url)),
        page_type="WebPage" if slug == "" else "TechArticle",
    ).html()


def menu(current: str) -> list[dict[str, Any]]:
    """The side menu of the area of the page: one group per section, its own group open."""
    sections = _area_sections(current)
    # A reader who arrives on the home page has chosen no page yet: the first steps are open.
    holder = next(
        (i for i, section in enumerate(sections) if any(p.slug == current for p in section.pages)),
        0,
    )
    return [
        {
            "title": section.title,
            "count": len(section.pages),
            "open": i == holder,
            "pages": [
                {
                    "href": link(p.slug),
                    "label": p.label,
                    "current": p.slug == current,
                }
                for p in section.pages
            ],
        }
        for i, section in enumerate(sections)
    ]


def markdown_link(slug: str) -> str:
    """Where the button of the page fetches its raw Markdown."""
    return f"/markdown?slug={quote(slug, safe='/')}" if slug else "/markdown"


def markdown_source(slug: str) -> str:
    """The Markdown of a page as it is written in docs/: what the copy button copies."""
    return _page_of(slug).path.read_text(encoding="utf-8")


def _page_of(slug: str) -> source.Page:
    page = source.home(DOCS) if slug == "" else source.find(_sections(), slug)
    if page is None:
        raise HTTPException(status_code=404, detail="No such page")
    return page


def document(slug: str) -> dict[str, Any]:
    """One page ready to draw: its HTML, its outline and its neighbours. 404 when there is none."""
    sections = _sections()
    page = source.home(DOCS) if slug == "" else source.find(sections, slug)
    if page is None:
        raise HTTPException(status_code=404, detail="No such page")
    rendered = source.render(page.path, DOCS, link)
    before, after = source.neighbours(_area_sections(slug), slug)
    where = next((s.title for s in sections for p in s.pages if p.slug == slug), "Documentation")
    return {
        "page": page,
        "section": where,
        "html": rendered.html,
        "outline": [h for h in rendered.headings if h.level <= 3],
        "before": before,
        "after": after,
        "source": f"https://github.com/NexyPy/nexy/edit/main/docs/{page.path.relative_to(DOCS).as_posix()}",
    }


def search_entries() -> list[dict[str, str]]:
    entries = []
    for page, section in _pages():
        rendered = source.render(page.path, DOCS, link)
        entries.append(source.search_entry(page, section, rendered, link(page.slug).lstrip("/")))
    return entries
