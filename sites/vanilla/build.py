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
from sites.shared import seo  # noqa: E402
from sites.shared.icons import ICONS, MARK  # noqa: E402

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


def _router_face(key: str, name: str, blurb: str) -> str:
    return (
        f'<span class="area-icon">{ICONS[f"router_{key}"]}</span>'
        f'<span class="area-text"><b>{escape(name)}</b></span>'
    )


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
        f'<li><a href="{relative(page.slug, f"routing/{key}")}" data-pick="{key}"'
        f"{' aria-current="true"' if key == chosen else ''}>"
        f"{_router_face(key, name, blurb)}{ICONS['icon_check']}</a></li>"
        for key, name, blurb in source.ROUTERS
    )
    return (
        f'<details class="area-select" aria-label="Router">'
        f"<summary>{faces}{ICONS['icon_select']}</summary>"
        f"<ul>{items}</ul></details>"
    )


def router_meta(page: source.Page) -> str:
    """Tells the first-paint script which router a page belongs to; nothing for a shared page."""
    return f'<meta name="nexy-router" content="{page.router}">' if page.router else ""


def _nav_item(page: source.Page, current: str) -> str:
    mark = ' aria-current="page"' if page.slug == current else ""
    return f'<li><a href="{relative(current, page.slug)}"{mark}>{escape(page.label)}</a></li>'


def _nav_group(group: source.Group, current: str, opens: bool) -> str:
    """An accordion group: the one holding the current page, or the first one, stays open."""
    items = "".join(_nav_item(page, current) for page in group.pages)
    opened = " open" if opens else ""
    router = f' data-router="{group.router}"' if group.router else ""
    # The chevron closes the line: no other ornament.
    return (
        f'<details class="group" data-section="{escape(group.title)}"{router}{opened}>'
        f'<summary><span class="group-name">{escape(group.title)}</span>'
        f'{ICONS["icon_chev"]}</summary>'
        f"<ul>{items}</ul></details>"
    )


def nav_html(tracks: list[source.Track], current: str) -> str:
    """The side menu: every section under its heading, one accordion group per folder."""
    # A reader who arrives on the home page has chosen no page yet: the first group is open.
    opened = source.group_of(tracks, current)
    parts = "".join(
        f'<div class="side-part">{''.join(_nav_group(group, current, group is opened) for group in track.groups)}</div>'
        for track in tracks
    )
    foot = (
        '<p class="side-empty" hidden>No page matches.</p>'
        '<div class="side-foot">'
        '<a href="https://github.com/NexyPy/nexy">Source on GitHub</a>'
        '<a href="https://github.com/NexyPy/nexy/blob/main/llms.txt">llms.txt for agents</a>'
        "</div>"
    )
    return parts + foot


def toc_html(headings: list[source.Heading]) -> str:
    items = "".join(
        f'<li class="l{h.level}"><a href="#{h.id}">{escape(h.text)}</a></li>'
        for h in headings
        if h.level <= 3
    )
    if not items:
        return ""
    return (
        f"<h2>On this page</h2><ul>{items}</ul>"
        '<p class="top-link"><a href="#content">Back to top</a></p>'
    )


def pager_html(before: source.Page | None, after: source.Page | None, current: str) -> str:
    def link(page: source.Page | None, rel: str, label: str) -> str:
        if page is None:
            return "<span></span>"
        arrow = ARROW_PREV if rel == "prev" else ARROW_NEXT
        text = (
            f'<span class="pager-text"><small>{label}</small>'
            f"<span>{escape(page.label)}</span></span>"
        )
        return (
            f'<a rel="{rel}" href="{relative(current, page.slug)}">'
            f'<span class="pager-arrow" aria-hidden="true">{arrow}</span>{text}</a>'
        )

    previous, following = link(before, "prev", "Previous"), link(after, "next", "Next")
    return f'<nav class="pager" aria-label="Pages">{previous}{following}</nav>'


def _head(page: source.Page, rendered: source.Rendered, site_url: str) -> str:
    """The tags a crawler reads: the address of the page, its cards, the menu above it."""
    url = seo.canonical(site_url, page.slug)
    return seo.Head(
        title=page.title,
        description=seo.description(rendered.html),
        url=url,
        site_url=site_url,
        trail=(("Documentation", seo.home(site_url)), (page.label, url)),
        page_type="TechArticle" if page.slug else "WebPage",
    ).html()


def _page_html(
    template: Template,
    tracks: list[source.Track],
    page: source.Page,
    section: str,
    rendered: source.Rendered,
    site_url: str,
) -> str:
    track = source.track_of(tracks, page.slug)
    before, after = source.neighbours(track, page.slug)
    rel = page.path.relative_to(DOCS).as_posix()
    home = not page.slug
    return template.substitute(
        title=escape(page.title),
        seo=_head(page, rendered, site_url),
        root=_root(page.slug),
        home=relative(page.slug, ""),
        nav=nav_html(tracks, page.slug),
        area_select=router_select_html(page),
        router_meta=router_meta(page),
        home_attr=' data-home="true"' if home else "",
        article_class="doc home" if home else "doc",
        article=rendered.html,
        toc=toc_html(rendered.headings),
        pager=pager_html(before, after, page.slug),
        section=escape(section),
        source=f"https://github.com/NexyPy/nexy/edit/main/docs/{rel}",
        mark=MARK,
        **ICONS,
    )


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
    return template.substitute(base=root, mark=MARK, **ICONS)


def _pages(docs: Path) -> list[tuple[source.Page, str]]:
    """Every page of the site, the home first, each with the group that lists it."""
    tracks = source.read_tracks(docs)
    return [(source.home(docs), "Documentation")] + [
        (page, group.title) for track in tracks for group in track.groups for page in group.pages
    ]


def _write_pages(
    out: Path,
    docs: Path,
    pages: list[tuple[source.Page, str]],
    template: Template,
    site_url: str,
) -> list[Path]:
    """Write one HTML and one Markdown file per page; return the HTML files."""
    tracks = source.read_tracks(docs)
    written, entries = [], []
    for page, section in pages:
        rendered = source.render(page.path, docs, lambda slug, cur=page.slug: relative(cur, slug))
        target = out / "docs" / page.slug / "index.html"
        _write(target, _page_html(template, tracks, page, section, rendered, site_url))
        _write(target.with_name("index.md"), page.path.read_text(encoding="utf-8"))
        url = f"docs/{page.slug}/" if page.slug else "docs/"
        entries.append(source.search_entry(page, section, rendered, url))
        written.append(target)
    _write(out / "search-index.json", json.dumps(entries, separators=(",", ":")))
    return written


def _write_crawl(out: Path, pages: list[tuple[source.Page, str]], site_url: str) -> None:
    """Write the two files a crawler asks for: the list of pages, and where that list lives."""
    _write(out / "robots.txt", seo.robots(site_url))
    _write(out / "sitemap.xml", seo.sitemap(seo.canonical(site_url, p.slug) for p, _ in pages))


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
    pages = _pages(docs)
    written = _write_pages(out, docs, pages, template, site_url)
    _write_crawl(out, pages, site_url)
    _write(out / "index.html", _redirect(site_url))
    _write(out / "404.html", not_found_html(base))
    _write(out / ".nojekyll", "")
    shutil.copytree(HERE / "assets", out / "assets", dirs_exist_ok=True)
    # The drawings of the docs: a figure is inlined, but its file travels with the site too.
    if (docs / "assets").is_dir():
        shutil.copytree(docs / "assets", out / "docs" / "assets", dirs_exist_ok=True)
    return written


def _redirect(site_url: str) -> str:
    """The root of the site: a short page that hands the reader, and the crawler, to the docs."""
    return (
        '<!doctype html><meta charset="utf-8"><title>Nexy</title>'
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
