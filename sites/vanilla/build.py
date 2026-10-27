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


def nav_html(sections: list[source.Section], current: str) -> str:
    def item(page: source.Page) -> str:
        mark = ' aria-current="page"' if page.slug == current else ""
        return f'<li><a href="{relative(current, page.slug)}"{mark}>{escape(page.label)}</a></li>'

    groups = (
        f"<section><h2>{escape(s.title)}</h2><ul>{''.join(item(p) for p in s.pages)}</ul></section>"
        for s in sections
    )
    return "".join(groups)


def toc_html(headings: list[source.Heading]) -> str:
    items = "".join(
        f'<li class="l{h.level}"><a href="#{h.id}">{escape(h.text)}</a></li>'
        for h in headings
        if h.level <= 3
    )
    return f"<h2>On this page</h2><ul>{items}</ul>" if items else ""


def pager_html(before: source.Page | None, after: source.Page | None, current: str) -> str:
    def link(page: source.Page | None, rel: str, label: str) -> str:
        if page is None:
            return "<span></span>"
        return (
            f'<a rel="{rel}" href="{relative(current, page.slug)}"><small>{label}</small>'
            f"<span>{escape(page.label)}</span></a>"
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
    return template.substitute(
        title=escape(page.title),
        description=_description(rendered),
        root=_root(page.slug),
        home=relative(page.slug, ""),
        nav=nav_html(sections, page.slug),
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
        url = f"docs/{page.slug}/" if page.slug else "docs/"
        entries.append(source.search_entry(page, section, rendered, url))
        written.append(target)
    _write(out / "search-index.json", json.dumps(entries, separators=(",", ":")))
    _write(out / "index.html", _redirect())
    _write(out / "404.html", not_found_html(base))
    _write(out / ".nojekyll", "")
    shutil.copytree(HERE / "assets", out / "assets", dirs_exist_ok=True)
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
