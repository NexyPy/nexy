"""Read docs/ for every site that shows it: the menu, one page's HTML, its outline, its neighbours.

The sites differ in how they look and where they run; none of them owns any text. Each passes a
``link`` function that turns a page slug into the URL its own router serves.
"""

from __future__ import annotations

import html as htmllib
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from posixpath import normpath

import cmarkgfm  # type: ignore[import-untyped]
from cmarkgfm.cmark import Options  # type: ignore[import-untyped]
from pygments import highlight  # type: ignore[import-untyped]
from pygments.formatters import HtmlFormatter  # type: ignore[import-untyped]
from pygments.lexers import HtmlDjangoLexer, get_lexer_by_name  # type: ignore[import-untyped]
from pygments.util import ClassNotFound  # type: ignore[import-untyped]

REPOSITORY = "https://github.com/NexyPy/nexy/blob/main/"
TEXT_LENGTH = 1800

_ROW_LINK = re.compile(r"\[([^\]]+)\]\(([^)#\s]+\.md)\)")
_FENCE = re.compile(r'^```(\w*)[ \t]+filename="([^"]+)"[ \t]*$', re.MULTILINE)
_PRE = re.compile(r'<pre lang="(\w*)__file(\d+)">')
_HEADING = re.compile(r"<h([2-6])>(.*?)</h\1>", re.DOTALL)
_CODE = re.compile(r'<pre lang="(\w+)"><code>(.*?)</code></pre>', re.DOTALL)
_HREF = re.compile(r'href="([^"]+)"')
_TAGS = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")

# An image of the docs is an illustration: the file is read and drawn as a figure, its alt text
# becoming the caption. The <style> inside the SVG paints it on GitHub, which shows the file alone;
# on the site it is dropped, so the colours of the page reach the drawing through currentColor.
_IMAGE = re.compile(r'<p><img src="([^"]+\.svg)" alt="([^"]*)" /></p>')
_PALETTE = re.compile(r"<style>.*?</style>", re.DOTALL)
_SVG = re.compile(r"<svg.*?</svg>", re.DOTALL)

Link = Callable[[str], str]


# The two ways to route a Nexy app, as the docs name them: (folder under docs/routing, label).
ROUTERS = (("fbr", "File-based"), ("modular", "Modular"))


@dataclass(frozen=True)
class Page:
    slug: str
    title: str
    label: str
    path: Path
    router: str | None = None


@dataclass(frozen=True)
class Section:
    title: str
    pages: list[Page]


@dataclass(frozen=True)
class Heading:
    level: int
    id: str
    text: str


@dataclass(frozen=True)
class Rendered:
    html: str
    headings: list[Heading]


def slug_of(relative: str) -> str:
    """`guides/actions.md` is `guides/actions`; a folder's README is the folder."""
    stem = relative.removesuffix(".md")
    return "" if stem == "README" else stem.removesuffix("/README")


def router_of(slug: str) -> str | None:
    """`fbr` or `modular` for a page under `routing/fbr` or `routing/modular`; None for the rest."""
    for router, _label in ROUTERS:
        folder = f"routing/{router}"
        if slug == folder or slug.startswith(f"{folder}/"):
            return router
    return None


def _title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def _page(docs: Path, relative: str, label: str) -> Page | None:
    path = docs / relative
    if not path.is_file():
        return None
    slug = slug_of(relative)
    return Page(slug, _title(path), label, path, router_of(slug))


def home(docs: Path) -> Page:
    """The landing page of the docs: their README."""
    path = docs / "README.md"
    return Page("", _title(path), "Overview", path)


def read_sections(docs: Path) -> list[Section]:
    """The menu: the sections and tables of docs/README.md, in the order they are written."""
    sections: list[Section] = []
    for line in (docs / "README.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            sections.append(Section(line[3:].strip(), []))
        elif line.startswith("|") and sections:
            pages = (_page(docs, rel, label) for label, rel in _ROW_LINK.findall(line))
            sections[-1].pages.extend(page for page in pages if page)
    return [section for section in sections if section.pages]


def find(sections: list[Section], slug: str) -> Page | None:
    return next((p for s in sections for p in s.pages if p.slug == slug), None)


def neighbours(sections: list[Section], slug: str) -> tuple[Page | None, Page | None]:
    """The page before and the page after, in menu order."""
    pages = [page for section in sections for page in section.pages]
    index = next((i for i, page in enumerate(pages) if page.slug == slug), None)
    if index is None:
        return None, None
    before = pages[index - 1] if index > 0 else None
    after = pages[index + 1] if index + 1 < len(pages) else None
    return before, after


def _name_files(text: str) -> tuple[str, list[str]]:
    """Move each `filename=` out of a fence, where the Markdown engine would drop it."""
    names: list[str] = []

    def keep(found: re.Match[str]) -> str:
        names.append(found[2])
        return f"```{found[1]}__file{len(names) - 1}"

    return _FENCE.sub(keep, text), names


def _caption(html: str, names: list[str]) -> str:
    """Wrap each named block in a figure that shows its file name."""

    def wrap(found: re.Match[str]) -> str:
        return f'<figure><figcaption>{names[int(found[2])]}</figcaption><pre lang="{found[1]}">'

    named = _PRE.sub(wrap, html)
    return re.sub(r"(<figure>.*?</pre>)", r"\1</figure>", named, flags=re.DOTALL)


def _anchor(text: str) -> str:
    plain = _TAGS.sub("", text).strip().lower()
    return re.sub(r"[^\w\- ]", "", plain).replace(" ", "-")


def _identify(html: str) -> Rendered:
    """Give every heading below the title an id, the way GitHub does, and list them."""
    seen: dict[str, int] = {}
    found: list[Heading] = []

    def mark(match: re.Match[str]) -> str:
        level, inner = int(match[1]), match[2]
        base = _anchor(inner)
        count = seen.get(base, 0)
        seen[base] = count + 1
        ident = base if count == 0 else f"{base}-{count}"
        found.append(Heading(level, ident, _TAGS.sub("", inner)))
        anchor = f'<a class="anchor" href="#{ident}" aria-label="Link to this section"></a>'
        return f'<h{level} id="{ident}">{inner}{anchor}</h{level}>'

    return Rendered(_HEADING.sub(mark, html), found)


def _target(href: str, page: Path, docs: Path, link: Link) -> str | None:
    """Where a relative link now points: another page, or a file of the repository."""
    name, _, fragment = href.partition("#")
    folder = page.parent.relative_to(docs).as_posix()
    suffix = f"#{fragment}" if fragment else ""
    inside = normpath(f"{folder}/{name}")
    if inside.startswith(".."):
        return REPOSITORY + normpath(f"{docs.name}/{folder}/{name}") + suffix
    return link(slug_of(inside)) + suffix if name.endswith(".md") else None


def _rewrite(html: str, page: Path, docs: Path, link: Link) -> str:
    def swap(found: re.Match[str]) -> str:
        href = found[1]
        if re.match(r"[a-z][a-z0-9+.-]*:|#|/", href):
            return found[0]
        target = _target(href, page, docs, link)
        return found[0] if target is None else f'href="{target}"'

    return _HREF.sub(swap, html)


_FORMATTER = HtmlFormatter(nowrap=True, classprefix="tok-")


def _lexer(language: str) -> object | None:
    """The colouring rules for a fence language; a .nexy file is HTML with Jinja."""
    if language == "nexy":
        return HtmlDjangoLexer()
    try:
        return get_lexer_by_name(language)
    except ClassNotFound:
        return None


def _colour(found: re.Match[str]) -> str:
    """Colour one code block at build time, so it needs no script to be readable."""
    language, escaped = found[1], found[2]
    lexer = _lexer(language)
    if lexer is None:
        return found[0]
    coloured = highlight(htmllib.unescape(escaped), lexer, _FORMATTER).rstrip("\n")
    return f'<pre lang="{language}"><code>{coloured}</code></pre>'


def _figures(html: str, page: Path, docs: Path) -> str:
    """Draw each image of the docs as a figure, the SVG it names read into the page.

    A file outside the docs, or one that is not there, stays an image: the site then serves or
    misses it exactly as the Markdown says.
    """

    def draw(found: re.Match[str]) -> str:
        target = (page.parent / normpath(found[1])).resolve()
        if docs.resolve() not in target.parents or not target.is_file():
            return found[0]
        svg = _PALETTE.sub("", target.read_text(encoding="utf-8")).strip()
        return f'<figure class="figure">{svg}<figcaption>{found[2]}</figcaption></figure>'

    return _IMAGE.sub(draw, html)


def plain(html: str) -> str:
    """The text of some HTML: no tags, no drawing, one space between words."""
    return _SPACE.sub(" ", _TAGS.sub(" ", _SVG.sub("", html))).strip()


def search_entry(page: Page, section: str, rendered: Rendered, url: str) -> dict[str, str]:
    """What a search needs to know about a page: where it is and the start of its text."""
    return {
        "title": page.title,
        "section": section,
        "url": url,
        "headings": " ".join(h.text for h in rendered.headings),
        "text": plain(rendered.html)[:TEXT_LENGTH],
    }


def render(page: Path, docs: Path, link: Link) -> Rendered:
    """One page as HTML: file names as captions, linked headings, links to the site's URLs."""
    text, names = _name_files(page.read_text(encoding="utf-8"))
    html = cmarkgfm.github_flavored_markdown_to_html(text, Options.CMARK_OPT_GITHUB_PRE_LANG)
    done = _identify(_CODE.sub(_colour, _caption(html, names)))
    # The figures are last: nothing else looks at the drawing the SVG carries.
    return Rendered(_figures(_rewrite(done.html, page, docs, link), page, docs), done.headings)
