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
_TABLE = re.compile(r"<table>.*?</table>", re.DOTALL)
_HREF = re.compile(r'href="([^"]+)"')

# A line marker, the way AdonisJS and Shiki read it:
# `// [!code ++]`, `# [!code --]`, `<!-- [!code highlight] -->`.
_MARK = re.compile(
    r"[ \t]*(?://|#|<!--)[ \t]*\[!code (\+{2}|-{2}|highlight)\][ \t]*(?:-->)?[ \t]*$"
)
_LINE_KIND = {"++": "add", "--": "del", "highlight": "hl"}
# Pygments writes spans only: this walks them to close and reopen a token on each newline.
_TAG = re.compile(r"<span[^>]*>|</span>|\n")
# A .nexy file opens with its Python logic between two bars; the template follows.
_FRONTMATTER = re.compile(r"\A---[ \t]*\n(?P<logic>.*?)^---[ \t]*$", re.DOTALL | re.MULTILINE)

# A `diagram` fence is an illustration drawn with characters: no language, no colouring.
_DIAGRAM = re.compile(r'<pre lang="diagram(__file(\d+))?"><code>(.*?)</code></pre>', re.DOTALL)
# A tree drawn with branch glyphs keeps its ASCII shape; anything else is drawn with blocks.
_BOX = re.compile(r"[│├└┌┐┘┬┴]")
_ARROW = re.compile(r"\s*(?:──+►|──+>|►|→|=>)\s*")
_FLOW_LABEL = re.compile(r"^([A-Za-z][\w ]{0,14}?)\s{2,}(\S.*)$")
_MAP = re.compile(r"^(\S.*?)\s+→\s+(\S.*)$")
_GAP = re.compile(r"\s{2,}")

# A folder listing, as a `text` fence draws it: `├─ src/`, or a line with no glyph for the root.
_BRANCH = re.compile(r"[├└]─")
_BRANCH_LINE = re.compile(r"^(?P<pad>(?:│  |   )*)(?P<glyph>├─|└─) ?(?P<rest>.*)$")
_TREE_PRE = re.compile(r'<pre lang="text"><code>(.*?)</code></pre>', re.DOTALL)

_ICONS = {
    "folder": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5'
    'a2 2 0 0 1-2-2z"/>',
    "file": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/>'
    '<path d="M14 3v5h5"/>',
    "terminal": '<path d="m5 8 5 4-5 4"/><path d="M13 17h6"/>',
    "pencil": '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    "box": '<path d="m21 8-9-5-9 5 9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/>',
    "play": '<path d="m8 5 11 7-11 7z"/>',
    "plug": '<path d="M9 2v6"/><path d="M15 2v6"/>'
    '<path d="M6 8h12v3a6 6 0 0 1-12 0z"/><path d="M12 17v5"/>',
    "database": '<ellipse cx="12" cy="5" rx="8" ry="3"/>'
    '<path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/>'
    '<path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>'
    '<path d="M12 3c2.5 2.6 4 5.7 4 9s-1.5 6.4-4 9c-2.5-2.6-4-5.7-4-9s1.5-6.4 4-9z"/>',
    "dot": '<circle cx="12" cy="12" r="3"/>',
    "arrow": '<path d="M4 12h15"/><path d="m14 6 6 6-6 6"/>',
}
_ICON_TPL = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"'
    ' stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{}</svg>'
)
_STEPS = (
    (re.compile(r"\b(build|bundle|compile)\b"), "box"),
    (re.compile(r"\b(start|serve|launch)\b"), "play"),
    (re.compile(r"^(uvx|nx|nexy|npm|pnpm|uv|pip|python|git|cd|npx)\b"), "terminal"),
    (re.compile(r"\b(endpoint|api|route|handler)\b"), "plug"),
    (re.compile(r"\b(data|share|state|store|database)\b"), "database"),
    (re.compile(r"\b(edit|write)\b"), "pencil"),
    (re.compile(r"\b(layout|page|file|markdown|mdx?)\b"), "file"),
    (re.compile(r"\b(request|browser|html|server)\b"), "globe"),
)

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


def _icon(name: str) -> str:
    return _ICON_TPL.format(_ICONS[name])


def _diagrams(html: str, names: list[str]) -> str:
    """Draw each `diagram` fence as a figure, named when the fence carries a `filename=`."""

    def draw(found: re.Match[str]) -> str:
        text = htmllib.unescape(found[3]).strip("\n")
        caption = names[int(found[2])] if found[2] is not None else ""
        label = f"<figcaption>{htmllib.escape(caption)}</figcaption>" if caption else ""
        return f'<figure class="diagram">{label}{_diagram_body(text)}</figure>'

    return _DIAGRAM.sub(draw, html)


def _diagram_body(text: str) -> str:
    """A branch drawing stays ASCII; a flow becomes blocks, a mapping a table of pairs."""
    lines = [line for line in text.splitlines() if line.strip()]
    if _BOX.search(text):
        return f'<pre lang="diagram"><code>{htmllib.escape(text)}</code></pre>'
    if len(lines) > 1 and all(_MAP.match(line) for line in lines):
        return f'<div class="map">{"".join(_map_row(line) for line in lines)}</div>'
    if _ARROW.search(text):
        return f'<div class="flow">{"".join(_flow_row(line) for line in lines)}</div>'
    return f'<pre lang="diagram"><code>{htmllib.escape(text)}</code></pre>'


def _flow_row(line: str) -> str:
    """One line of a flow: an optional label, then its steps joined by arrows."""
    found = _FLOW_LABEL.match(line)
    label, body = (found[1], found[2]) if found else ("", line)
    chips: list[str] = []
    for index, step in enumerate(step for step in _ARROW.split(body) if step.strip()):
        if index:
            chips.append(f'<span class="flow-arrow">{_icon("arrow")}</span>')
        chips.append(
            f'<span class="flow-step"><span class="flow-icon">{_icon(_step_icon(step))}</span>'
            f'<span class="flow-text">{htmllib.escape(step.strip())}</span></span>'
        )
    head = f'<span class="flow-label">{htmllib.escape(label)}</span>' if label else ""
    return f'<div class="flow-row">{head}<span class="flow-steps">{"".join(chips)}</span></div>'


def _step_icon(step: str) -> str:
    for pattern, name in _STEPS:
        if pattern.search(step.strip().lower()):
            return name
    return "dot"


def _map_row(line: str) -> str:
    """One line of a mapping: the source on the left, what it answers on the right."""
    found = _MAP.match(line)
    left, right = found[1].strip(), found[2].strip()
    parts = _GAP.split(right, maxsplit=1)
    target = parts[0]
    note = parts[1] if len(parts) > 1 else ""
    if not note and " (" in target:
        target, _, note = target.rpartition(" (")
        note = f"({note}"
    tail = f'<span class="map-note">{htmllib.escape(note)}</span>' if note else ""
    return (
        f'<div class="map-row">{_map_source(left)}'
        f'<span class="map-arrow">{_icon("arrow")}</span>'
        f'<span class="map-to"><code>{htmllib.escape(target)}</code>{tail}</span></div>'
    )


def _map_source(left: str) -> str:
    if "/" in left or re.search(r"\.\w+$", left):
        return (
            f'<span class="map-from"><span class="map-icon">{_icon("file")}</span>'
            f"<code>{htmllib.escape(left)}</code></span>"
        )
    return f'<span class="map-from map-text">{htmllib.escape(left)}</span>'


def _structures(html: str) -> str:
    """Draw a folder listing as an explorer: folders, files, and the note each line carries."""

    def draw(found: re.Match[str]) -> str:
        text = htmllib.unescape(found[1])
        if not _BRANCH.search(text):
            return found[0]
        rows = _branches(text)
        if not rows:
            return found[0]
        return f'<figure class="diagram tree"><div class="tree">{"".join(rows)}</div></figure>'

    return _TREE_PRE.sub(draw, html)


def _branches(text: str) -> list[str]:
    """Read the glyphs of a listing into rows, each carrying the guides of its ancestors."""
    rows: list[tuple[str, str, str, str]] = []
    for line in text.splitlines():
        branch = _BRANCH_LINE.match(line)
        if branch:
            name, note = _split_note(branch["rest"])
            rows.append((branch["pad"], branch["glyph"], name, note))
        elif line.strip() and line[:1].isspace() and rows:
            pad, glyph, name, note = rows[-1]
            rows[-1] = (pad, glyph, name, f"{note} {line.strip()}".strip())
        elif line.strip():
            rows.append(("", "", line.strip(), ""))
    return [_tree_row(*row) for row in rows]


def _split_note(rest: str) -> tuple[str, str]:
    parts = _GAP.split(rest.strip(), maxsplit=1)
    return parts[0], parts[1] if len(parts) > 1 else ""


def _guides(pad: str, glyph: str) -> str:
    """One column per ancestor folder: a line while its siblings go on, an elbow for this row."""
    spans = [
        f'<span class="tree-guide {"tree-guide-line" if pad[at] == "│" else ""}"></span>'
        for at in range(0, len(pad), 3)
    ]
    if glyph:
        elbow = "tree-guide-elbow" if glyph == "├─" else "tree-guide-last"
        spans.append(f'<span class="tree-guide {elbow}"></span>')
    return "".join(spans)


def _tree_row(pad: str, glyph: str, name: str, note: str) -> str:
    folder = name.endswith("/")
    icon = _icon("folder" if folder else "file")
    kind = "tree-icon-folder" if folder else "tree-icon-file"
    if note.startswith("→"):
        said = f'<span class="tree-route">{htmllib.escape(note)}</span>'
    else:
        said = f'<span class="tree-note">{_note(note)}</span>' if note else ""
    name_class = "tree-name tree-dir" if folder else "tree-name"
    return (
        f'<div class="tree-row"><span class="tree-guides">{_guides(pad, glyph)}</span>'
        f'<span class="tree-icon {kind}">{icon}</span>'
        f'<span class="{name_class}">{htmllib.escape(name)}</span>{said}</div>'
    )


def _note(text: str) -> str:
    """A note keeps the backticked names it carries, drawn as code."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", htmllib.escape(text))


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


def _marked(text: str) -> tuple[str, list[str]]:
    """Take the line markers out of the source and say what each line is."""
    kinds: list[str] = []
    lines: list[str] = []
    for line in text.split("\n"):
        mark = _MARK.search(line)
        kinds.append(_LINE_KIND[mark[1]] if mark else "")
        lines.append(line[: mark.start()] if mark else line)
    return "\n".join(lines), kinds


def _rows(coloured: str) -> list[str]:
    """Split coloured HTML on its newlines, closing and reopening a token on each line."""
    rows: list[str] = []
    stack: list[str] = []
    current: list[str] = []
    at = 0
    for tag in _TAG.finditer(coloured):
        current.append(coloured[at : tag.start()])
        token = tag[0]
        if token == "\n":
            current.extend("</span>" for _ in stack)
            rows.append("".join(current))
            current = list(stack)
        elif token == "</span>":
            stack.pop()
            current.append(token)
        else:
            stack.append(token)
            current.append(token)
        at = tag.end()
    current.append(coloured[at:])
    rows.append("".join(current))
    return rows


def _lines(coloured: str, kinds: list[str]) -> str:
    """One span per line, so a marker can paint the row it marks."""
    rows = []
    for index, row in enumerate(_rows(coloured)):
        kind = kinds[index] if index < len(kinds) else ""
        name = f"line line-{kind}" if kind else "line"
        rows.append(f'<span class="{name}">{row or " "}</span>')
    return "".join(rows)


def _paint(text: str, language: str) -> str:
    """One stretch of a fence, coloured by the rules of the language it is written in."""
    lexer = _lexer(language)
    return text if lexer is None else highlight(text, lexer, _FORMATTER)


def _nexy(text: str) -> str:
    """A .nexy file is Python between its bars, then the template it renders."""
    head = _FRONTMATTER.match(text)
    if head is None:
        return _paint(text, "nexy").rstrip("\n")
    bar = '<span class="tok-bar">---</span>'
    parts = [bar, _paint(head["logic"], "python").rstrip("\n"), bar]
    view = text[head.end() :].lstrip("\n")
    if view.strip():
        parts.append(_paint(view, "nexy").rstrip("\n"))
    return "\n".join(parts)


def _colour(found: re.Match[str]) -> str:
    """Colour one code block at build time, so it needs no script to be readable."""
    language, escaped = found[1], found[2]
    if _lexer(language) is None:
        return found[0]
    text, kinds = _marked(htmllib.unescape(escaped))
    coloured = _nexy(text) if language == "nexy" else _paint(text, language).rstrip("\n")
    return f'<pre lang="{language}"><code>{_lines(coloured, kinds)}</code></pre>'


def _tables(html: str) -> str:
    """Wrap each table so a wide one scrolls inside its card instead of widening the page."""
    return _TABLE.sub(lambda found: f'<div class="table-wrap">{found[0]}</div>', html)


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
    shaped = _structures(_diagrams(html, names))
    coloured = _CODE.sub(_colour, _caption(shaped, names))
    done = _identify(_callouts(_tables(coloured)))
    # The figures are last: nothing else looks at the drawing the SVG carries.
    return Rendered(_figures(_rewrite(done.html, page, docs, link), page, docs), done.headings)
