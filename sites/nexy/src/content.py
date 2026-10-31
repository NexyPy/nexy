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
    "document",
    "head_of",
    "link",
    "markdown_link",
    "markdown_source",
    "menu",
    "router_of",
    "router_select",
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
    return [(source.home(DOCS), "Documentation")] + [
        (page, group.title) for track in _tracks() for group in track.groups for page in group.pages
    ]


def _tracks() -> list[source.Track]:
    return source.read_tracks(DOCS)


def router_select(slug: str) -> list[dict[str, Any]]:
    """The routers above the menu: each picks its routing groups and leads to its overview."""
    chosen = source.router_of(slug) or source.ROUTERS[0][0]
    return [
        {
            "key": key,
            "name": name,
            "blurb": blurb,
            "icon": ICONS[f"router_{key}"],
            "home": link(f"routing/{key}"),
            "current": key == chosen,
        }
        for key, name, blurb in source.ROUTERS
    ]


def router_of(slug: str) -> str:
    """The router a page belongs to, for the first-paint script; empty for a shared page."""
    return source.router_of(slug) or ""


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


def _menu_group(group: source.Group, current: str, opened: source.Group) -> dict[str, Any]:
    return {
        "title": group.title,
        "count": len(group.pages),
        "open": group is opened,
        "router": group.router or "",
        "pages": [
            {"href": link(p.slug), "label": p.label, "current": p.slug == current}
            for p in group.pages
        ],
    }


def menu(current: str) -> list[dict[str, Any]]:
    """The side menu: every section under its heading, the folder of the page open."""
    tracks = _tracks()
    # A reader who arrives on the home page has chosen no page yet: the first group is open.
    opened = source.group_of(tracks, current)
    return [
        {
            "label": track.label,
            "groups": [_menu_group(group, current, opened) for group in track.groups],
        }
        for track in tracks
    ]


def markdown_link(slug: str) -> str:
    """Where the button of the page fetches its raw Markdown."""
    return f"/markdown?slug={quote(slug, safe='/')}" if slug else "/markdown"


def markdown_source(slug: str) -> str:
    """The Markdown of a page as it is written in docs/: what the copy button copies."""
    return _page_of(slug).path.read_text(encoding="utf-8")


def _page_of(slug: str) -> source.Page:
    page = source.home(DOCS) if slug == "" else source.find(_tracks(), slug)
    if page is None:
        raise HTTPException(status_code=404, detail="No such page")
    return page


def document(slug: str) -> dict[str, Any]:
    """One page ready to draw: its HTML, its outline and its neighbours. 404 when there is none."""
    tracks = _tracks()
    page = source.home(DOCS) if slug == "" else source.find(tracks, slug)
    if page is None:
        raise HTTPException(status_code=404, detail="No such page")
    rendered = source.render(page.path, DOCS, link)
    before, after = source.neighbours(source.track_of(tracks, slug), slug)
    return {
        "page": page,
        "section": page.group or "Documentation",
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
