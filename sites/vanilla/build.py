"""Build the vanilla docs site: static HTML, one stylesheet, one script, no framework.

    python sites/vanilla/build.py            # writes sites/vanilla/dist
    python sites/vanilla/build.py out/       # writes another folder

Every link is relative, so the folder works from a project URL such as
https://nexypy.github.io/nexy/ as well as from a domain root.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import shutil
import sys
from html import escape as _escape
from pathlib import Path
from string import Template

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from sites.shared import docs_source as source  # noqa: E402
from sites.shared import home, i18n, seo  # noqa: E402
from sites.shared.icons import ICONS, MARK  # noqa: E402
from sites.shared.version import VERSION  # noqa: E402

DOCS = REPO / "docs"

# The arrows of the starter's Button: a line with a head, drawn at build time.
_ARROW = (
    '<svg class="arrow" width="15" height="15" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true"><path d="{path}"/></svg>'
)
ARROW_PREV = _ARROW.format(path="M19 12H5M12 19l-7-7 7-7")
ARROW_NEXT = _ARROW.format(path="M5 12h14M12 5l7 7-7 7")


def escape(text: str) -> str:
    return _escape(text, quote=True)


def relative(current: str, target: str) -> str:
    """The URL of the page `target` as seen from the page `current`, both given as slugs."""
    here = posixpath.join("docs", current) if current else "docs"
    there = posixpath.join("docs", target) if target else "docs"
    return posixpath.relpath(there, here) + "/"


def _root(current: str) -> str:
    depth = len(current.split("/")) + 1 if current else 1
    return posixpath.join(*[".."] * depth)


def _router_word(key: str) -> str:
    """The key that translates the name of a router; FBR is a name in every language."""
    return f' data-i18n="router_{key}"' if key != "fbr" else ""


def _router_face(key: str, name: str, _: str) -> str:
    return (
        f'<span class="area-icon">{ICONS[f"router_{key}"]}</span>'
        f'<span class="area-text"><b{_router_word(key)}>{escape(name)}</b></span>'
    )


def _at(page: source.Page, slug: str) -> str:
    """The address of another page of the same language."""
    return source.address_of(page.lang, slug)


def router_select_html(page: source.Page) -> str:
    """The router above the menu: it picks the routing groups; each choice leads to its overview.

    The summary holds every face and the stylesheet shows the chosen one, so a page shared by the
    three routers is drawn once and still names the router the reader chose.
    """
    chosen = page.router or source.ROUTERS[0][0]
    faces = "".join(
        f'<span class="area-face" data-router="{key}">{_router_face(key, name, blurb)}</span>'
        for key, name, blurb in source.ROUTERS
    )
    items = "".join(
        f'<li><a href="{relative(page.address, _at(page, f"routing/{key}"))}" data-pick="{key}"'
        f"{' aria-current="true"' if key == chosen else ''}>"
        f"{_router_face(key, name, blurb)}{ICONS['icon_check']}</a></li>"
        for key, name, blurb in source.ROUTERS
    )
    return (
        f'<details class="area-select" aria-label="Router" data-i18n-aria="router_aria">'
        f"<summary>{faces}{ICONS['icon_select']}</summary>"
        f"<ul>{items}</ul></details>"
    )


def router_meta(page: source.Page) -> str:
    """Tells the first-paint script which router a page belongs to; nothing for a shared page."""
    return f'<meta name="nexy-router" content="{page.router}">' if page.router else ""


def _nav_item(page: source.Page, current: str) -> str:
    mark = ' aria-current="page"' if page.slug == current else ""
    badge = '<span class="badge-new" data-i18n="new_badge">New</span>' if page.badge else ""
    href = relative(_at(page, current), page.address)
    return f'<li><a href="{href}"{mark}>{escape(page.label)}</a>{badge}</li>'


def _nav_group(group: source.Group, current: str, opens: bool) -> str:
    """An accordion group: the one holding the current page, or the first one, stays open."""
    items = "".join(_nav_item(page, current) for page in group.pages)
    opened = " open" if opens else ""
    router = f' data-router="{group.router}"' if group.router else ""
    # The chevron closes the line: no other ornament.
    return (
        f'<details class="group" data-section="{escape(group.title)}"'
        f' data-scope="{group.scope}"{router}{opened}>'
        f'<summary><span class="group-name">{escape(group.title)}</span>'
        f"{ICONS['icon_chev']}</summary>"
        f"<ul>{items}</ul></details>"
    )


def _nav_part(track: source.Track, current: str, opened: source.Group | None) -> str:
    """One section of the menu: its heading, then its folders."""
    groups = "".join(_nav_group(group, current, group is opened) for group in track.groups)
    return f'<div class="side-part"><p class="side-section">{escape(track.label)}</p>{groups}</div>'


def nav_html(tracks: list[source.Track], current: str) -> str:
    """The side menu: every section under its heading, one accordion group per folder."""
    # A reader who arrives on the home page has chosen no page yet: the first group is open.
    opened = source.group_of(tracks, current)
    parts = "".join(_nav_part(track, current, opened) for track in tracks)
    foot = (
        '<p class="side-empty" data-i18n="no_match" hidden>No page matches.</p>'
        '<div class="side-foot">'
        # The button of the menu is a plain hidden link: `site.js` points it at the next page
        # this browser has not read, so every page serves exactly the same bytes.
        '<a href="#" class="continue" hidden>Continue</a>'
        '<a href="#" class="all-docs" data-i18n="all_docs">All documentation</a>'
        '<a href="https://github.com/NexyPy/nexy" data-i18n="source_github">Source on GitHub</a>'
        '<a href="https://github.com/NexyPy/nexy/blob/main/llms.txt" data-i18n="llms">'
        "llms.txt for agents</a>"
        "</div>"
    )
    return parts + foot


def _toc_item_class(heading: source.Heading) -> str:
    """The class of an outline entry: a heading of a router variant is hidden like its variant."""
    if not heading.routers:
        return f'class="l{heading.level}"'
    return f'class="l{heading.level} router-variant" data-router="{heading.routers}"'


def toc_html(headings: list[source.Heading], lang: str = i18n.DEFAULT) -> str:
    items = "".join(
        f'<li {_toc_item_class(h)}><a href="#{h.id}"{i18n.isolate(h.text, lang)}>'
        f"{escape(h.text)}</a></li>"
        for h in headings
        if h.level <= 3
    )
    if not items:
        return ""
    return (
        '<h2 data-i18n="on_this_page">On this page</h2>'
        f"<ul>{items}</ul>"
        '<p class="top-link"><a href="#content" data-i18n="back_to_top">Back to top</a></p>'
    )


def pager_html(before: source.Page | None, after: source.Page | None, current: str) -> str:
    def link(page: source.Page | None, rel: str, label: str) -> str:
        if page is None:
            return "<span></span>"
        arrow = ARROW_PREV if rel == "prev" else ARROW_NEXT
        text = (
            f'<span class="pager-text"><small data-i18n="{label.lower()}">{label}</small>'
            f"<span>{escape(page.label)}</span></span>"
        )
        return (
            f'<a rel="{rel}" href="{relative(_at(page, current), page.address)}">'
            f'<span class="pager-arrow" aria-hidden="true">{arrow}</span>{text}</a>'
        )

    previous, following = link(before, "prev", "Previous"), link(after, "next", "Next")
    label = 'aria-label="Pages" data-i18n-aria="pager_aria"'
    return f'<nav class="pager" {label}>{previous}{following}</nav>'


def _alternates(page: source.Page, docs: Path, site_url: str) -> tuple[tuple[str, str], ...]:
    """The address of the page in every language it is translated into, English first."""
    english = source.english_twin(page.path, docs).relative_to(docs).as_posix()
    return tuple(
        (one.code, seo.canonical(site_url, source.address_of(one.code, page.slug)))
        for one in i18n.LANGUAGES
        if one.code == i18n.DEFAULT or (docs / one.code / english).is_file()
    )


def _head(page: source.Page, rendered: source.Rendered, site_url: str, docs: Path) -> str:
    """The tags a crawler reads: the address of the page, its cards, the menu above it.

    A page still in English names the English page as its own: the same words at two addresses
    would compete with each other.
    """
    url = seo.canonical(site_url, page.slug if page.fallback else page.address)
    home_url = seo.canonical(site_url, _at(page, ""))
    return seo.Head(
        title=page.title,
        description=seo.description(rendered.html),
        url=url,
        site_url=site_url,
        trail=(("Documentation", home_url), (page.label, url)),
        page_type="TechArticle" if page.slug else "WebPage",
        lang=i18n.DEFAULT if page.fallback else page.lang,
        alternates=_alternates(page, docs, site_url),
    ).html()


def _lang_note(page: source.Page) -> str:
    """One line above a page still in English, in the language the reader chose."""
    if not page.fallback:
        return ""
    note = escape(i18n.text(page.lang, "fallback_note"))
    return f'<p class="lang-note" data-i18n="fallback_note">{note}</p>'


def search_file(lang: str) -> str:
    """The search index of a language: one file each, so a reader searches what they read."""
    return "search-index.json" if lang == i18n.DEFAULT else f"search-index.{lang}.json"


def _page_html(
    template: Template,
    tracks: list[source.Track],
    page: source.Page,
    section: str,
    rendered: source.Rendered,
    site_url: str,
    docs: Path,
) -> str:
    track = source.track_of(tracks, page.slug)
    before, after = source.neighbours(track, page.slug)
    rel = source.english_twin(page.path, docs).relative_to(docs).as_posix()
    home = not page.slug
    language = i18n.find(page.lang)
    html = template.substitute(
        lang=language.code,
        dir=language.direction,
        title=escape(page.title),
        seo=_head(page, rendered, site_url, docs),
        root=_root(page.address),
        search_index=search_file(page.lang),
        home=relative(page.address, _at(page, "")),
        nav=nav_html(tracks, page.slug),
        area_select=router_select_html(page),
        language_select=i18n.select_html(
            page.lang, lambda code: relative(page.address, source.address_of(code, page.slug))
        ),
        lang_note=_lang_note(page),
        router_meta=router_meta(page),
        home_attr=' data-home="true"' if home else "",
        article_class="doc home" if home else "doc",
        article=rendered.html,
        toc=toc_html(rendered.headings, page.lang),
        pager=pager_html(before, after, page.slug),
        section=escape(section),
        source=f"https://github.com/NexyPy/nexy/edit/main/docs/{rel}",
        mark=MARK,
        version=VERSION,
        **ICONS,
    )
    return i18n.localize(html, page.lang)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def base_of(base: str) -> str:
    """The folder the site is served from, with a slash on both ends: `nexy` is `/nexy/`."""
    inner = base.strip("/")
    return f"/{inner}/" if inner else "/"


def not_found_html(base: str) -> str:
    """The page for a wrong address. GitHub Pages serves it at any depth, so links are absolute."""
    root = base_of(base)
    template = Template((HERE / "not_found.html").read_text(encoding="utf-8"))
    return template.substitute(base=root, mark=MARK, words=_lost_words(), **ICONS)


def _lost_words() -> str:
    """The words of the 404 page in every language but English, for the script that picks one."""
    keys = ("lost_title", "lost_text", "lost_link")
    words = {
        one.code: {key: i18n.text(one.code, key) for key in keys}
        for one in i18n.LANGUAGES
        if one.code != i18n.DEFAULT
    }
    return json.dumps(words, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def _pages(docs: Path, lang: str = i18n.DEFAULT) -> list[tuple[source.Page, str]]:
    """Every page of a language, the home first, each with the group that lists it."""
    tracks = source.read_tracks(docs, lang)
    return [(source.home(docs, lang), "Documentation")] + [
        (page, group.title) for track in tracks for group in track.groups for page in group.pages
    ]


def _rendered(page: source.Page, docs: Path) -> source.Rendered:
    """A page as HTML: the home is composed from Getting Started, not from the whole README."""

    def link(slug: str) -> str:
        return relative(page.address, _at(page, slug))

    if not page.slug:
        return home.render(docs, link, page.lang)
    return source.render(page.path, docs, link)


def _write_pages(
    out: Path,
    docs: Path,
    pages: list[tuple[source.Page, str]],
    template: Template,
    site_url: str,
) -> list[Path]:
    """Write one HTML and one Markdown file per page of a language; return the HTML files."""
    lang = pages[0][0].lang
    tracks = source.read_tracks(docs, lang)
    written, entries = [], []
    for page, section in pages:
        rendered = _rendered(page, docs)
        target = out / "docs" / page.address / "index.html"
        _write(target, _page_html(template, tracks, page, section, rendered, site_url, docs))
        _write(target.with_name("index.md"), page.path.read_text(encoding="utf-8"))
        url = f"docs/{page.address}/" if page.address else "docs/"
        entries.append(source.search_entry(page, section, rendered, url))
        written.append(target)
    payload = json.dumps(entries, ensure_ascii=False, separators=(",", ":"))
    _write(out / search_file(lang), payload)
    return written


def _write_redirects(out: Path, site_url: str) -> None:
    """An old address of a page that moved hands the reader to the new one."""
    for old_slug, new_slug in source.REDIRECTS.items():
        _write(out / "docs" / old_slug / "index.html", redirect_html(old_slug, new_slug, site_url))


def redirect_html(old: str, new: str, site_url: str) -> str:
    """An old address that hands the reader and the crawler to the page that replaced it.

    The address is relative to the old page, so the folder works from any host; the canonical tag
    names the one address the new page has.
    """
    href = relative(old, new)
    canonical = seo.canonical(site_url, new)
    return (
        '<!doctype html><meta charset="utf-8"><title>Redirecting...</title>'
        f'<meta http-equiv="refresh" content="0; url={href}">'
        f'<link rel="canonical" href="{canonical}">'
        f'<a href="{href}">This page has moved</a>'
    )


def _write_crawl(out: Path, pages: list[tuple[source.Page, str]], site_url: str) -> None:
    """Write the two files a crawler asks for: the list of pages, and where that list lives."""
    _write(out / "robots.txt", seo.robots(site_url))
    urls = (seo.canonical(site_url, p.address) for p, _ in pages if not p.fallback)
    _write(out / "sitemap.xml", seo.sitemap(urls))


def build(
    out: Path,
    docs: Path = DOCS,
    base: str = "",
    site_url: str = seo.DEFAULT_SITE_URL,
) -> list[Path]:
    """Write the whole site into `out` and return the pages it wrote.

    `base` is the folder the site is served from (`/nexy` for a project page): only 404.html needs
    it, because the server shows that page at the address that failed, whatever its depth.
    `site_url` is the address the site is published at, for the canonical tags and the sitemap.
    """
    template = Template((HERE / "template.html").read_text(encoding="utf-8"))
    pages, written = [], []
    for language in i18n.LANGUAGES:
        found = _pages(docs, language.code)
        written += _write_pages(out, docs, found, template, site_url)
        pages += found
    _write_redirects(out, site_url)
    _write_crawl(out, pages, site_url)
    _write(out / "index.html", _redirect(site_url))
    _write(out / "404.html", not_found_html(base))
    _write(out / ".nojekyll", "")
    shutil.copytree(HERE / "assets", out / "assets", dirs_exist_ok=True)
    _write(
        out / "assets" / "i18n.json",
        json.dumps(i18n.payload(), ensure_ascii=False, separators=(",", ":")),
    )
    # The drawings of the docs: a figure is inlined, but its file travels with the site too.
    if (docs / "assets").is_dir():
        shutil.copytree(docs / "assets", out / "docs" / "assets", dirs_exist_ok=True)
    return written


# The root picks the language the reader chose last, else the first one the browser prefers that
# the site speaks, else English. A crawler and a reader without script follow the refresh.
_PICK = (
    "<script>try{{var k={codes},s=localStorage.getItem('nexy-docs-lang'),"
    "w=[s].concat(navigator.languages||[navigator.language]),c='en';"
    "for(var i=0;i<w.length;i++){{var l=String(w[i]||'').slice(0,2).toLowerCase();"
    "if(k.indexOf(l)>=0){{c=l;break}}}}"
    "location.replace(c==='en'?'docs/':'docs/'+c+'/')}}catch(e){{}}</script>"
)


def _redirect(site_url: str) -> str:
    """The root of the site: a short page that hands the reader, and the crawler, to the docs."""
    codes = json.dumps([language.code for language in i18n.LANGUAGES])
    return (
        '<!doctype html><meta charset="utf-8"><title>Nexy</title>'
        f"{_PICK.format(codes=codes)}"
        '<meta http-equiv="refresh" content="0; url=docs/">'
        f'<link rel="canonical" href="{seo.home(site_url)}">'
        '<a href="docs/">Nexy documentation</a>'
    )


def _arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the vanilla Nexy docs site.")
    parser.add_argument(
        "folder", nargs="?", type=Path, default=HERE / "dist", help="where to write"
    )
    parser.add_argument("--base", default="", help="folder the site is served from, e.g. /nexy")
    parser.add_argument(
        "--site-url",
        default=seo.DEFAULT_SITE_URL,
        help="address the site is published at, for canonical tags and the sitemap",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    options = _arguments(sys.argv[1:])
    count = len(build(options.folder, base=options.base, site_url=options.site_url))
    print(f"{count} pages written to {options.folder}")
