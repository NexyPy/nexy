"""What a search engine and a social card read about a page, written the same way by every site.

A page says three things: its address (`canonical`), its summary (the opening paragraph, cut) and
where it sits (`trail`, the breadcrumb the menu already shows). From those, `Head` writes the head
tags, `sitemap` lists every page and `robots` points at that list.

Nothing here knows how a site routes or looks: both docs sites publish under `/docs/`, so the
address of a page is `{site_url}/docs/{slug}/`, whatever serves it.
"""

from __future__ import annotations

import html as htmllib
import json
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from xml.sax.saxutils import escape as _xml

from sites.shared.docs_source import plain

__all__ = [
    "DEFAULT_SITE_URL",
    "Head",
    "canonical",
    "description",
    "home",
    "robots",
    "sitemap",
]

# Where the vanilla site is published when the caller says nothing: the GitHub Pages project site.
DEFAULT_SITE_URL = "https://nexypy.github.io/nexy"

SITE_NAME = "Nexy"
IMAGE = "assets/og.png"
IMAGE_WIDTH = 1200
IMAGE_HEIGHT = 630
DESCRIPTION_LENGTH = 200

_PARAGRAPH = re.compile(r"<p>(.*?)</p>", re.DOTALL)

# A tag left a space where it stood: `the <code>route</code>.` reads `the route .` once stripped.
_PUNCTUATION = re.compile(r" +([.,;:!?)\]}])(?!\w)")
# A tag inside brackets leaves a space after the opening one: `mode (<code>x</code>)` reads `( x )`.
_OPENING = re.compile(r"([(\[{]) +")


def _base(site_url: str) -> str:
    """The address of a site without its trailing slash."""
    return site_url.rstrip("/")


def home(site_url: str) -> str:
    """The address of the documentation: the page every trail starts at."""
    return f"{_base(site_url)}/docs/"


def canonical(site_url: str, slug: str) -> str:
    """The one address of a page: what the canonical tag and the sitemap both name."""
    return f"{home(site_url)}{slug}/" if slug else home(site_url)


def description(html: str) -> str:
    """The opening paragraph of a page as one line of plain text, in at most 200 characters.

    A page without a paragraph has no summary: the caller then writes no description rather than
    an empty one.
    """
    found = _PARAGRAPH.search(html)
    if not found:
        return ""
    text = _OPENING.sub(r"\1", _PUNCTUATION.sub(r"\1", plain(found[1])))
    if len(text) <= DESCRIPTION_LENGTH:
        return text
    return text[: DESCRIPTION_LENGTH - 1].rstrip() + "\u2026"


def _meta(name: str, content: str, *, prop: bool = False) -> str:
    """One `<meta>` tag, its value escaped; `prop` for the Open Graph namespace."""
    key = "property" if prop else "name"
    return f'<meta {key}="{name}" content="{htmllib.escape(content, quote=True)}">'


def _tweet(head: Head) -> list[str]:
    """The card X shows, which keeps its own names even where it reads Open Graph."""
    tags = [
        _meta("twitter:card", "summary_large_image"),
        _meta("twitter:title", head.title),
        _meta("twitter:image", head.image),
    ]
    if head.description:
        tags.append(_meta("twitter:description", head.description))
    return tags


@dataclass(frozen=True)
class Head:
    """The head tags of one page: its summary, its address, its cards and its linked data."""

    title: str
    description: str
    url: str
    site_url: str
    trail: Sequence[tuple[str, str]]
    page_type: str = "TechArticle"

    @property
    def image(self) -> str:
        """The picture a card shows, at the one size every network accepts."""
        return f"{_base(self.site_url)}/{IMAGE}"

    def _simple(self) -> list[str]:
        """The tags every crawler reads: the summary, the crawl rule and the address."""
        tags = [_meta("robots", "index, follow, max-image-preview:large")]
        if self.description:
            tags.append(_meta("description", self.description))
        tags.append(f'<link rel="canonical" href="{htmllib.escape(self.url, quote=True)}">')
        return tags

    def _cards(self) -> list[str]:
        """What a link looks like when it is pasted elsewhere: Open Graph, then Twitter."""
        kind = "article" if self.page_type == "TechArticle" else "website"
        summary = [_meta("og:description", self.description, prop=True)] if self.description else []
        graph = [
            _meta("og:type", kind, prop=True),
            _meta("og:site_name", SITE_NAME, prop=True),
            _meta("og:locale", "en", prop=True),
            _meta("og:title", self.title, prop=True),
            _meta("og:url", self.url, prop=True),
            *summary,
            _meta("og:image", self.image, prop=True),
            _meta("og:image:width", str(IMAGE_WIDTH), prop=True),
            _meta("og:image:height", str(IMAGE_HEIGHT), prop=True),
            _meta("og:image:alt", f"{SITE_NAME} documentation", prop=True),
        ]
        return [*graph, *_tweet(self)]

    def _linked_data(self) -> str:
        """The page and the menu above it, in the one graph a crawler reads without guessing."""
        article = {
            "@type": self.page_type,
            "@id": self.url,
            "headline": self.title,
            "url": self.url,
            "inLanguage": "en",
            "image": self.image,
            "isPartOf": {
                "@type": "WebSite",
                "name": f"{SITE_NAME} documentation",
                "url": home(self.site_url),
            },
        }
        if self.description:
            article["description"] = self.description
        crumbs = [
            {"@type": "ListItem", "position": index, "name": name, "item": where}
            for index, (name, where) in enumerate(self.trail, start=1)
        ]
        graph = {
            "@context": "https://schema.org",
            "@graph": [article, {"@type": "BreadcrumbList", "itemListElement": crumbs}],
        }
        payload = json.dumps(graph, separators=(",", ":"), ensure_ascii=False)
        return f'<script type="application/ld+json">{payload.replace("<", "\\u003c")}</script>'

    def html(self) -> str:
        """The whole block, one tag per line, in the order a crawler expects to read them."""
        return "\n".join([*self._simple(), *self._cards(), self._linked_data()])


def sitemap(urls: Iterable[str]) -> str:
    """The file that lists every page, so a crawler needs to follow no link to find one."""
    entries = [f"<url><loc>{_xml(url)}</loc></url>" for url in urls]
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        *entries,
        "</urlset>",
        "",
    ]
    return "\n".join(lines)


def robots(site_url: str) -> str:
    """The file that points at the sitemap and keeps the raw Markdown copies out of the index.

    A rule is read from the root of the host, never from the folder of the site: on a GitHub Pages
    project site this file only counts once the same text sits at `https://<owner>.github.io/`.
    """
    return f"User-agent: *\nAllow: /\nDisallow: /*.md$\n\nSitemap: {_base(site_url)}/sitemap.xml\n"
