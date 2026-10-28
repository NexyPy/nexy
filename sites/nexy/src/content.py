"""The pages of this site are the pages of docs/: read here, drawn by the components."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from nexy.http import HTTPException

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from sites.shared import docs_source as source  # noqa: E402
from sites.shared.icons import ICONS, MARK  # noqa: E402

DOCS = REPO / "docs"
ASSETS = REPO / "sites" / "vanilla" / "assets"

__all__ = [
    "ASSETS",
    "ICONS",
    "MARK",
    "document",
    "link",
    "menu",
    "router_of",
    "routers",
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


def router_of(slug: str) -> str | None:
    """`fbr` or `modular` for a page of one router, None for a page both share."""
    return source.router_of(slug)


def routers() -> list[dict[str, str]]:
    """The choice above the menu: each router and the overview it leads to."""
    return [
        {"id": router, "label": label, "home": link(f"routing/{router}")}
        for router, label in source.ROUTERS
    ]


def title_of(slug: str) -> str:
    found = next((page.title for page, _ in _pages() if page.slug == slug), "Not found")
    return f"{found} - Nexy"


def menu(current: str) -> list[dict[str, Any]]:
    """The side menu: each page with the link it points to and whether it is the open one."""
    return [
        {
            "title": section.title,
            "pages": [
                {
                    "href": link(p.slug),
                    "label": p.label,
                    "current": p.slug == current,
                    "router": p.router,
                }
                for p in section.pages
            ],
        }
        for section in source.read_sections(DOCS)
    ]


def document(slug: str) -> dict[str, Any]:
    """One page ready to draw: its HTML, its outline and its neighbours. 404 when there is none."""
    sections = source.read_sections(DOCS)
    page = source.home(DOCS) if slug == "" else source.find(sections, slug)
    if page is None:
        raise HTTPException(status_code=404, detail="No such page")
    rendered = source.render(page.path, DOCS, link)
    before, after = source.neighbours(sections, slug)
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
