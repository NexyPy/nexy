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

# A `diagram` fence is an illustration drawn with characters: no language, no colouring.
_DIAGRAM = re.compile(r'<pre lang="diagram(__file(\d+))?"><code>(.*?)</code></pre>', re.DOTALL)

# A GitHub alert (`> [!NOTE]`) becomes a callout: the marker names the kind, the rest is the body.
_ALERT = re.compile(
    r"<blockquote>\s*<p>\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\](.*?)</blockquote>", re.DOTALL
)
_ALERT_TITLES = {
    "NOTE": "Note",
    "TIP": "Tip",
    "IMPORTANT": "Important",
    "WARNING": "Warning",
    "CAUTION": "Caution",
}
_TAGS = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")

# An image of the docs is an illustration: the file is read and drawn as a figure, its alt text
# becoming the caption. The <style> inside the SVG paints it on GitHub, which shows the file alone;
# on the site it is dropped, so the colours of the page reach the drawing through currentColor.
_IMAGE = re.compile(r'<p><img src="([^"]+\.svg)" alt="([^"]*)" /></p>')
_PALETTE = re.compile(r"<style>.*?</style>", re.DOTALL)
_SVG = re.compile(r"<svg.*?</svg>", re.DOTALL)

Link = Callable[[str], str]


# The three ways to route a Nexy app, as the docs name them: (folder under docs/routing, label).
ROUTERS = (("fbr", "File-based"), ("modular", "Modular"), ("custom", "Custom"))


@dataclass(frozen=True)
class Page:
    """One page of the docs, with the words the menu shows for it."""

    slug: str
    title: str
    label: str
    path: Path
    router: str | None = None
    summary: str = ""
    track: str = ""
    group: str = ""


@dataclass(frozen=True)
class Group:
    """A menu folder: the pages that answer one question, and a line saying why."""

    title: str
    blurb: str
    pages: list[Page]


@dataclass(frozen=True)
class Track:
    """A learning path: one step of the docs, made of ordered groups."""

    slug: str
    label: str
    blurb: str
    groups: list[Group]


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
    """`fbr`, `modular` or `custom` for a `routing/<router>` page; None for the rest."""
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


def _page(
    docs: Path,
    relative: str,
    label: str,
    *,
    summary: str = "",
    track: str = "",
    group: str = "",
) -> Page | None:
    path = docs / relative
    if not path.is_file():
        return None
    slug = slug_of(relative)
    return Page(slug, _title(path), label, path, router_of(slug), summary, track, group)


def home(docs: Path) -> Page:
    """The landing page of the docs: their README."""
    path = docs / "README.md"
    return Page("", _title(path), "Overview", path)


def _slugify(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def _summary(row: str) -> str:
    cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
    return " ".join(cells[1].replace("`", "").split()) if len(cells) > 1 else ""


def read_tracks(docs: Path) -> list[Track]:
    """The learning path of docs/README.md: `##` a track, `###` a group, each table its pages."""
    tracks: list[Track] = []
    label = blurb = ""
    groups: list[Group] = []
    group_title = group_blurb = ""
    pages: list[Page] = []
    reading: str | None = None
    fenced = False

    def close_group() -> None:
        nonlocal group_title, group_blurb, pages
        if group_title and pages:
            groups.append(Group(group_title, group_blurb, pages))
        group_title, group_blurb, pages = "", "", []

    def close_track() -> None:
        nonlocal label, blurb, groups
        close_group()
        if label and groups:
            tracks.append(Track(_slugify(label), label, blurb, groups))
        label, blurb, groups = "", "", []

    for line in (docs / "README.md").read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if text.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if text.startswith("## "):
            close_track()
            label = text[3:].strip()
            reading = "track"
            continue
        if text.startswith("### "):
            close_group()
            if label:
                group_title = text[4:].strip()
                reading = "group"
            continue
        if text.startswith("|"):
            reading = None
            found = _ROW_LINK.search(text)
            if group_title and found:
                page = _page(
                    docs,
                    found[2],
                    found[1],
                    summary=_summary(text),
                    track=_slugify(label),
                    group=group_title,
                )
                if page:
                    pages.append(page)
            continue
        if not text:
            if (reading == "track" and blurb) or (reading == "group" and group_blurb):
                reading = None
            continue
        if text.startswith(("-", "*", ">", "`")):
            reading = None
            continue
        if reading == "track":
            blurb = f"{blurb} {text}".strip()
        elif reading == "group":
            group_blurb = f"{group_blurb} {text}".strip()
        else:
            reading = None
    close_track()
    return tracks


def pages_of(track: Track) -> list[Page]:
    return [page for group in track.groups for page in group.pages]


def track_of(tracks: list[Track], slug: str) -> Track:
    """The track that holds a page; the first track when the page is the home page."""
    for track in tracks:
        if any(page.slug == slug for page in pages_of(track)):
            return track
    return tracks[0]


def group_of(tracks: list[Track], slug: str) -> Group:
    for track in tracks:
        for group in track.groups:
            if any(page.slug == slug for page in group.pages):
                return group
    return tracks[0].groups[0]


def find(tracks: list[Track], slug: str) -> Page | None:
    return next((page for track in tracks for page in pages_of(track) if page.slug == slug), None)


def neighbours(track: Track, slug: str) -> tuple[Page | None, Page | None]:
    """The page before and the page after, in the order of the track."""
    pages = pages_of(track)
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


def _diagrams(html: str, names: list[str]) -> str:
    """Draw each `diagram` fence as a figure, named when the fence carries a `filename=`."""

    def draw(found: re.Match[str]) -> str:
        body = f'<pre lang="diagram"><code>{found[3]}</code></pre>'
        if found[2] is None:
            return f'<figure class="diagram">{body}</figure>'
        caption = names[int(found[2])]
        return f'<figure class="diagram"><figcaption>{caption}</figcaption>{body}</figure>'

    return _DIAGRAM.sub(draw, html)


def _callouts(html: str) -> str:
    """Turn each GitHub alert into an aside, keeping the paragraphs it holds."""

    def convert(found: re.Match[str]) -> str:
        kind = found[1]
        body = found[2].lstrip()
        body = body[4:].lstrip() if body.startswith("</p>") else f"<p>{body}"
        title = f'<p class="callout-title">{_ALERT_TITLES[kind]}</p>'
        return f'<aside class="callout callout-{kind.lower()}">{title}{body}</aside>'

    return _ALERT.sub(convert, html)


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
    """One page as HTML: illustrations, callouts, captions, linked headings, links to site URLs."""
    text, names = _name_files(page.read_text(encoding="utf-8"))
    html = cmarkgfm.github_flavored_markdown_to_html(text, Options.CMARK_OPT_GITHUB_PRE_LANG)
    drawn = _diagrams(html, names)
    coloured = _CODE.sub(_colour, _caption(drawn, names))
    done = _identify(_callouts(coloured))
    # The figures are last: nothing else looks at the drawing the SVG carries.
    return Rendered(_figures(_rewrite(done.html, page, docs, link), page, docs), done.headings)
