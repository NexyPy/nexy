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
import re
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


def router_switch_html(current: str) -> str:
    """The choice of router above the menu: each button leads to the overview of its router."""
    buttons = "".join(
        f'<button type="button" data-router="{router}" '
        f'data-home="{relative(current, f"routing/{router}")}" aria-pressed="false">'
        f"{escape(label)}</button>"
        for router, label in source.ROUTERS
    )
    group = 'class="router-switch" role="group" aria-label="Router"'
    return f"<div {group}><span>Docs for</span>{buttons}</div>"


def router_meta(page: source.Page) -> str:
    """Tells the first-paint script which router a page belongs to; nothing for a shared page."""
    return f'<meta name="nexy-router" content="{page.router}">' if page.router else ""


def _nav_item(page: source.Page, current: str) -> str:
    mark = ' aria-current="page"' if page.slug == current else ""
    tag = f' data-router="{page.router}"' if page.router else ""
    return f'<li{tag}><a href="{relative(current, page.slug)}"{mark}>{escape(page.label)}</a></li>'


def _nav_group(section: source.Section, current: str) -> str:
    """A collapsible section: open by default, so the menu works without JavaScript."""
    items = "".join(_nav_item(page, current) for page in section.pages)
    count = len(section.pages)
    # The name and the count are joined by a dashed rule, like the Eyebrow of a starter section.
    return (
        f'<details class="group" data-section="{escape(section.title)}" open>'
        f'<summary><span class="group-name">{escape(section.title)}</span>'
        '<span class="group-rule" aria-hidden="true"></span>'
        f'<span class="group-count">{count}</span>{ICONS["icon_chev"]}</summary>'
        f"<ul>{items}</ul></details>"
    )


def nav_html(sections: list[source.Section], current: str) -> str:
    """The side menu: the router choice, and one collapsible group per section."""
    groups = "".join(_nav_group(section, current) for section in sections)
    foot = (
        '<p class="side-empty" hidden>No page matches.</p>'
        '<div class="side-foot">'
        '<a href="https://github.com/NexyPy/nexy">Source on GitHub</a>'
        '<a href="https://github.com/NexyPy/nexy/blob/main/llms.txt">llms.txt for agents</a>'
        "</div>"
    )
    return router_switch_html(current) + groups + foot


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


def _description(rendered: source.Rendered) -> str:
    first = re.search(r"<p>(.*?)</p>", rendered.html, re.DOTALL)
    return escape(source.plain(first[1]))[:200] if first else ""


def _page_html(
    template: Template,
    sections: list[source.Section],
    page: source.Page,
    section: str,
    rendered: source.Rendered,
) -> str:
    before, after = source.neighbours(sections, page.slug)
    rel = page.path.relative_to(DOCS).as_posix()
    home = not page.slug
    return template.substitute(
        title=escape(page.title),
        description=_description(rendered),
        root=_root(page.slug),
        home=relative(page.slug, ""),
        nav=nav_html(sections, page.slug),
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


def build(out: Path, docs: Path = DOCS, base: str = "") -> list[Path]:
    """Write the whole site into `out` and return the pages it wrote.

    `base` is the folder the site is served from (`/nexy` for a project page). Only 404.html needs
    it, because the server shows that page at the address that failed, whatever its depth.
    """
    sections = source.read_sections(docs)
    template = Template((HERE / "template.html").read_text(encoding="utf-8"))
    entries, written = [], []
    pages = [(source.home(docs), "Documentation")] + [
        (p, s.title) for s in sections for p in s.pages
    ]
    for page, section in pages:
        rendered = source.render(page.path, docs, lambda slug, cur=page.slug: relative(cur, slug))
        target = out / "docs" / page.slug / "index.html"
        _write(target, _page_html(template, sections, page, section, rendered))
        _write(target.with_name("index.md"), page.path.read_text(encoding="utf-8"))
        url = f"docs/{page.slug}/" if page.slug else "docs/"
        entries.append(source.search_entry(page, section, rendered, url))
        written.append(target)
    _write(out / "search-index.json", json.dumps(entries, separators=(",", ":")))
    _write(out / "index.html", _redirect())
    _write(out / "404.html", not_found_html(base))
    _write(out / ".nojekyll", "")
    shutil.copytree(HERE / "assets", out / "assets", dirs_exist_ok=True)
    # The drawings of the docs: a figure is inlined, but its file travels with the site too.
    if (docs / "assets").is_dir():
        shutil.copytree(docs / "assets", out / "docs" / "assets", dirs_exist_ok=True)
    return written


def _redirect() -> str:
    return (
        '<!doctype html><meta charset="utf-8"><title>Nexy</title>'
        '<meta http-equiv="refresh" content="0; url=docs/">'
        '<link rel="canonical" href="docs/"><a href="docs/">Nexy documentation</a>'
    )


def _arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the vanilla Nexy docs site.")
    parser.add_argument(
        "folder", nargs="?", type=Path, default=HERE / "dist", help="where to write"
    )
    parser.add_argument("--base", default="", help="folder the site is served from, e.g. /nexy")
    return parser.parse_args(argv)


if __name__ == "__main__":
    options = _arguments(sys.argv[1:])
    print(f"{len(build(options.folder, base=options.base))} pages written to {options.folder}")
