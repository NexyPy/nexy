"""The pages of this site are the pages of docs/: read here, drawn by the components.

An address is what follows `/docs/` in a URL: `guides/actions` for the English page,
`fr/guides/actions` for its French translation. Every function here takes one and reads the
language from it, so a component only passes along the address it was given.
"""

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
from sites.shared import home, i18n, seo  # noqa: E402
from sites.shared.icons import ICONS, MARK  # noqa: E402
from sites.shared.version import VERSION  # noqa: E402

DOCS = REPO / "docs"
ASSETS = REPO / "sites" / "vanilla" / "assets"

# The address this site is published at: the canonical tag and the cards are absolute.
SITE_URL = "https://nexy.ai"

__all__ = [
    "ASSETS",
    "ICONS",
    "MARK",
    "SITE_URL",
    "VERSION",
    "document",
    "head_of",
    "home_link",
    "i18n_payload",
    "isolate",
    "language_of",
    "language_select",
    "link",
    "localize",
    "preferred_language",
    "markdown_link",
    "markdown_source",
    "menu",
    "redirect_of",
    "router_of",
    "router_select",
    "search_entries",
    "search_link",
    "slug_of",
    "title_of",
]


def locate(address: str) -> tuple[str, str]:
    """The language and the page of an address: `fr/guides/actions` is French `guides/actions`."""
    head, _, rest = address.partition("/")
    if head in i18n.CODES and head != i18n.DEFAULT:
        return head, rest
    return i18n.DEFAULT, address


def link(slug: str, lang: str = i18n.DEFAULT) -> str:
    """The URL of a page of this site, in a language."""
    address = source.address_of(lang, slug)
    return f"/docs/{address}" if address else "/docs"


def home_link(address: str) -> str:
    """The home of the docs in the language of the page at `address`."""
    return link("", locate(address)[0])


def language_of(address: str) -> i18n.Language:
    """The language a page is served in: its code and its direction."""
    return i18n.find(locate(address)[0])


def language_select(address: str = "") -> str:
    """The compact language picker of the top bar: each language links to this very page."""
    lang, slug = locate(address)
    return i18n.select_html(lang, lambda code: link(slug, code))


def preferred_language(accept_language: str) -> str:
    """The language the browser asks for first among those of the site."""
    return i18n.preferred(accept_language)


def isolate(text: str, lang: str) -> str:
    """The `dir` a label of the outline needs on a page that reads right to left."""
    return i18n.isolate(text, lang)


def localize(html: str, address: str) -> str:
    """A served page with every word of the site in its language."""
    return i18n.localize(html, locate(address)[0])


def i18n_payload() -> dict[str, object]:
    """Every word the browser writes itself, in every language."""
    return i18n.payload()


def slug_of(pathname: str) -> str:
    """The address a URL path shows: `/docs/fr/guides/actions` is `fr/guides/actions`."""
    return pathname.removeprefix("/docs").strip("/")


def redirect_of(address: str) -> str:
    """The new address of a moved page, or the empty string when the page was not moved."""
    target = source.REDIRECTS.get(address, "")
    return link(target) if target else ""


def _tracks(lang: str) -> list[source.Track]:
    return source.read_tracks(DOCS, lang)


def _pages(lang: str) -> list[tuple[source.Page, str]]:
    return [(source.home(DOCS, lang), "Documentation")] + [
        (page, group.title)
        for track in _tracks(lang)
        for group in track.groups
        for page in group.pages
    ]


def _find(address: str) -> source.Page | None:
    lang, slug = locate(address)
    return source.home(DOCS, lang) if slug == "" else source.find(_tracks(lang), slug)


def router_select(address: str) -> list[dict[str, Any]]:
    """The routers above the menu: each picks its routing groups and leads to its overview."""
    lang, slug = locate(address)
    chosen = source.router_of(slug) or source.ROUTERS[0][0]
    return [
        {
            "key": key,
            "name": name,
            "blurb": blurb,
            "icon": ICONS[f"router_{key}"],
            "home": link(f"routing/{key}", lang),
            "current": key == chosen,
        }
        for key, name, blurb in source.ROUTERS
    ]


def router_of(address: str) -> str:
    """The router a page belongs to, for the first-paint script; empty for a shared page."""
    return source.router_of(locate(address)[1]) or ""


def title_of(address: str) -> str:
    page = _find(address)
    return f"{page.title if page else 'Not found'} - Nexy"


def _rendered(page: source.Page) -> source.Rendered:
    """A page drawn with this site's URLs: the home shows its cards, not the whole menu."""

    def to(slug: str) -> str:
        return link(slug, page.lang)

    if page.slug == "":
        return home.render(DOCS, to, page.lang)
    return source.render(page.path, DOCS, to)


def _alternates(page: source.Page) -> tuple[tuple[str, str], ...]:
    """The address of the page in every language it is translated into, English first."""
    english = source.english_twin(page.path, DOCS).relative_to(DOCS).as_posix()
    return tuple(
        (one.code, seo.canonical(SITE_URL, source.address_of(one.code, page.slug)))
        for one in i18n.LANGUAGES
        if one.code == i18n.DEFAULT or (DOCS / one.code / english).is_file()
    )


def head_of(address: str) -> str:
    """What a crawler reads about a page: its summary, its address, its cards, the menu above it.

    A page still in English names the English page as its own, like the vanilla site.
    """
    page = _find(address)
    if page is None:
        return '<meta name="robots" content="noindex">'
    url = seo.canonical(SITE_URL, page.slug if page.fallback else page.address)
    home_url = seo.canonical(SITE_URL, source.address_of(page.lang, ""))
    return seo.Head(
        title=page.title,
        description=seo.description(_rendered(page).html),
        url=url,
        site_url=SITE_URL,
        trail=(("Documentation", home_url), (page.label, url)),
        page_type="WebPage" if page.slug == "" else "TechArticle",
        lang=i18n.DEFAULT if page.fallback else page.lang,
        alternates=_alternates(page),
    ).html()


def _menu_group(group: source.Group, current: str, opened: source.Group) -> dict[str, Any]:
    return {
        "title": group.title,
        "count": len(group.pages),
        "open": group is opened,
        "router": group.router or "",
        "scope": group.scope,
        "pages": [
            {
                "href": link(p.slug, p.lang),
                "label": p.label,
                "badge": p.badge,
                "current": p.slug == current,
            }
            for p in group.pages
        ],
    }


def menu(address: str) -> list[dict[str, Any]]:
    """The side menu: every section under its heading, the folder of the page open."""
    lang, current = locate(address)
    tracks = _tracks(lang)
    # A reader who arrives on the home page has chosen no page yet: the first group is open.
    opened = source.group_of(tracks, current)
    return [
        {
            "label": track.label,
            "groups": [_menu_group(group, current, opened) for group in track.groups],
        }
        for track in tracks
    ]


def markdown_link(address: str) -> str:
    """Where the button of the page fetches its raw Markdown."""
    return f"/markdown?slug={quote(address, safe='/')}" if address else "/markdown"


def markdown_source(address: str) -> str:
    """The Markdown of a page as it is written in docs/: what the copy button copies."""
    return _page_of(address).path.read_text(encoding="utf-8")


def _page_of(address: str) -> source.Page:
    page = _find(address)
    if page is None:
        raise HTTPException(status_code=404, detail="No such page")
    return page


def _source_url(page: source.Page) -> str:
    """The English page on GitHub: a translation is written by the script, never by hand."""
    english = source.english_twin(page.path, DOCS).relative_to(DOCS).as_posix()
    return f"https://github.com/NexyPy/nexy/edit/main/docs/{english}"


def document(address: str) -> dict[str, Any]:
    """One page ready to draw: its HTML, its outline and its neighbours. 404 when there is none."""
    page = _page_of(address)
    rendered = _rendered(page)
    before, after = source.neighbours(source.track_of(_tracks(page.lang), page.slug), page.slug)
    return {
        "page": page,
        "home": link("", page.lang),
        "section": page.group or "Documentation",
        "html": rendered.html,
        "outline": [h for h in rendered.headings if h.level <= 3],
        "before": before,
        "after": after,
        "source": _source_url(page),
        "note": i18n.text(page.lang, "fallback_note") if page.fallback else "",
    }


def search_link(address: str) -> str:
    """Where the search of a page reads its index: the pages of its own language."""
    lang = locate(address)[0]
    return "/search-index" if lang == i18n.DEFAULT else f"/search-index?lang={lang}"


def search_entries(lang: str = i18n.DEFAULT) -> list[dict[str, str | None]]:
    """What the search of a language knows about each of its pages."""
    code = lang if i18n.is_known(lang) else i18n.DEFAULT
    entries: list[dict[str, str | None]] = []
    for page, section in _pages(code):
        url = link(page.slug, page.lang).lstrip("/")
        entries.append(source.search_entry(page, section, _rendered(page), url))
    return entries
