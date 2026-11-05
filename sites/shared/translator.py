"""What a translator is allowed to see of a Markdown page, and how its answer is put back.

A page of `docs/` is mostly prose, but every code fence, inline code, link target, table pipe and
heading marker is skeleton: translating it breaks the page. `protect` turns each of those into a
numbered placeholder, `chunks` cuts the remaining text into pieces a service accepts, and `restore`
puts the kept parts back and refuses an answer that lost one.

Nothing here talks to a network: the same three functions serve the tests and the translator script.
"""

from __future__ import annotations

import re
from collections.abc import Collection

_PLACEHOLDER = re.compile(r"\[\[\s*(\d+)\s*\]\]")

# The names a service must not touch: a product is not a word to translate. A service rewrites
# `Python` as the snake, `Vue` as a view and `FastAPI` letter by letter. The longest name first,
# so `Jinja2` is not read as `Jinja` and a `2`.
NAMES = (
    "Claude Code", "Next.js", "Node.js", "SolidJS", "Jinja2", "Jinja", "Python",
    "FastAPI", "Starlette", "Uvicorn", "Pydantic", "Vite", "React", "Preact", "Vue", "Svelte",
    "Solid", "NestJS", "Django", "Flask", "Remix", "Astro", "Markdown", "MDX", "TypeScript",
    "JavaScript", "Tailwind", "UnoCSS", "Tortoise", "SQLModel", "SQLAlchemy", "Alembic",
    "Aerich", "SQLite", "PostgreSQL", "WebSocket", "OpenAPI", "GitHub", "Nginx", "Caddy",
    "Docker", "Codex", "OpenCode", "pnpm", "npm", "pytest", "uv",
)  # fmt: skip
_NAME = "|".join(re.escape(name) for name in sorted(NAMES, key=len, reverse=True))

# What must survive the trip, in the order that keeps the longest match first: a fenced block is
# read before a lone backtick, a comment before a tag, a link target before a bare URL.
_KEPT = re.compile(
    r"""
    (?P<fence>^```[^\n]*\n.*?^```[ \t]*$)
  | (?P<comment><!--.*?-->)
  | (?P<tag><[^>]+>)
  | (?P<code>`[^`\n]+`)
  | (?P<link>\][(][^)\s]+[)])
  | (?P<url>https?://[^\s)>\]]+)
  | (?P<name>(?<![\w.-])(?:"""
    + _NAME
    + r""")(?![\w-]))
  | (?P<separator>^\|?[ \t]*:?-{2,}:?[ \t]*(\|[ \t]*:?-{2,}:?[ \t]*)*\|?[ \t]*$)
  | (?P<marker>^[ \t]*([#]{1,6}|[-*+]|\d+\.|>)[ \t]+)
  | (?P<rule>^[ \t]*(-{3,}|\*{3,}|_{3,})[ \t]*$)
  | (?P<emphasis>\*\*|__)
  | (?P<pipe>\|)
  | (?P<token>\{[a-z,]+\})
    """,
    re.MULTILINE | re.DOTALL | re.VERBOSE,
)

# The paragraph boundary: a chunk never cuts a paragraph in two, so a service sees whole sentences.
_BLOCK = re.compile(r"\n[ \t]*\n")
CHUNK = 4500
# How far from the wanted place a cut may look for a space, when a chunk has to be split again.
WINDOW = 400

# A named fence shows its file or drawing name in a caption. The fence itself is code and never
# travels; the caption is prose, and it is the only part of a fence a reader sees translated.
_CAPTION = re.compile(r'^```\w+[ \t]+filename="(?P<caption>[^"\n]*)"', re.MULTILINE)
# A cell that starts with a list comma is an artefact of the service, not punctuation.
_CELL_COMMA = re.compile(r"(\|[ \t]*),[ \t]*")


# A line that opens a block of its own: it is never glued to the line above it.
_OPENS_BLOCK = re.compile(r"^(#{1,6}\s|[-*+]\s|\d+[.)]\s|\||```|<|>|(-{3,}|\*{3,}|_{3,})\s*$)")
# A line after which the next one starts afresh: a heading, a row, a tag, an alert, a hard break.
_CLOSES_LINE = re.compile(r"(^#{1,6}\s|^\||^```|^\[!\w+\]$|>$|\\$|  $)")
_FENCE_LINE = re.compile(r"^\s*```")


def _quoted(line: str) -> str | None:
    """The text of a blockquote line, or None when the line is not quoted."""
    stripped = line.lstrip()
    return stripped[1:].strip() if stripped.startswith(">") else None


def _glues(previous: str, line: str) -> bool:
    """Whether `line` continues the sentence of `previous`, wrapped only for the editor."""
    above, below = _quoted(previous), _quoted(line)
    if (above is None) != (below is None):
        return False
    top, bottom = (above, below) if above is not None else (previous.strip(), line.strip())
    if not top or not bottom or (above is None and previous.endswith("  ")):
        return False
    return not _CLOSES_LINE.search(top) and not _OPENS_BLOCK.match(bottom)


def unwrap(markdown: str) -> str:
    """Each paragraph on one line: a service translates a line alone, so a wrap cuts a sentence."""
    lines: list[str] = []
    fenced = False
    for line in markdown.split("\n"):
        if _FENCE_LINE.match(line):
            fenced = not fenced
        elif not fenced and lines and _glues(lines[-1], line):
            text = _quoted(line)
            lines[-1] += " " + (text if text is not None else line.strip())
            continue
        lines.append(line)
    return "\n".join(lines)


def protect(markdown: str) -> tuple[str, list[str]]:
    """The page as a template where every kept part is `[[n]]`, and the parts themselves."""
    kept: list[str] = []

    def swap(found: re.Match[str]) -> str:
        # The space after a marker stays in the text: `[[3]]Modes` is a word a service rewrites,
        # `[[3]] Modes` a token it keeps.
        part = found[0].rstrip(" \t")
        kept.append(part)
        return f"[[{len(kept) - 1}]]{found[0][len(part) :]}"

    return _KEPT.sub(swap, markdown), kept


# The kept parts that only shape the text: a reader sees them as layout, never as a word.
_SHAPE = re.compile(
    r"\A(?:[ \t]*(?:[#]{1,6}|[-*+]|\d+\.|>)|\*\*|__|\||[ \t]*(?:-{3,}|\*{3,}|_{3,})[ \t]*)\Z"
    r"|\A\|?[ \t]*:?-{2,}"
)


def structural(kept: list[str]) -> frozenset[int]:
    """The placeholders that are layout: a marker, a pipe, an emphasis, a table separator."""
    return frozenset(index for index, part in enumerate(kept) if _SHAPE.match(part))


def chunks(template: str, limit: int = CHUNK) -> list[str]:
    """The template cut at paragraph boundaries, each piece short enough for one request."""
    pieces: list[str] = []
    current = ""
    for block in _BLOCK.split(template):
        if current and len(current) + len(block) + 2 > limit:
            pieces.append(current)
            current = block
            continue
        current = f"{current}\n\n{block}" if current else block
    if current:
        pieces.append(current)
    return pieces


def split(text: str, near: int | None = None) -> tuple[str, str, str] | None:
    """The text cut in two at a space, the space kept apart, or None when it has none.

    The space is the one nearest `near` (the middle by default), on its left when there is one
    there: a kept part that starts a piece survives a service that drops the one ending a piece.
    """
    middle = len(text) // 2 if near is None else near
    cuts = [
        at
        for at in range(max(middle - WINDOW, 1), min(middle + WINDOW, len(text) - 1))
        if text[at] in " \n"
    ]
    before = [at for at in cuts if at <= middle]
    cut = max(before) if before else (min(cuts) if cuts else None)
    if cut is None:
        return None
    return text[:cut], text[cut], text[cut + 1 :]


def placeholders(text: str) -> list[int]:
    """The placeholder numbers a piece of text carries, in the order they appear."""
    return [int(found[1]) for found in _PLACEHOLDER.finditer(text)]


_EMPTY_LINK = re.compile(r"(?<!!)\[\s*(?=\[\[(\d+)\]\])")


def empty_links(text: str) -> int:
    """How many links of a piece have no words: `[[[3]]` is a link the service emptied."""
    return len(_EMPTY_LINK.findall(text))


def emptied(answer: str, chunk: str) -> int | None:
    """The placeholder closing a link the service emptied, or None when every link has words."""
    if empty_links(answer) <= empty_links(chunk):
        return None
    before = set(_EMPTY_LINK.findall(chunk))
    return next(int(n) for n in _EMPTY_LINK.findall(answer) if n not in before)


def has_words(text: str) -> bool:
    """Whether a piece holds anything to translate once its placeholders are set aside."""
    return any(char.isalpha() for char in _PLACEHOLDER.sub("", text))


def missing(translated: str, kept: list[str]) -> list[int]:
    """The placeholders the answer dropped or repeated, so the caller can retry before giving up."""
    seen = placeholders(translated)
    return [index for index in range(len(kept)) if seen.count(index) != 1]


# A piece that opens with a placeholder comes back with one bracket fewer: the service reads the
# first token it meets as a bracket pair and balances it. The number is still there, so the part
# can be put back instead of asked again.
_OPENING = re.compile(r"\A\[(?!\[)(\d+)\]\]")


def heal_opening(answer: str) -> str:
    """Give back the bracket a service drops from the placeholder that opens a piece."""
    return _OPENING.sub(r"[[\1]]", answer, count=1)


# A zero-width space a service slips between the brackets of a placeholder (Chinese does). Only
# that one and the BOM: the zero-width joiners carry meaning in Urdu, Hindi and Bengali.
_INVISIBLE = "[\u200b\ufeff]*"
_SPLIT_PLACEHOLDER = re.compile(rf"\[{_INVISIBLE}\[{_INVISIBLE}(\d+){_INVISIBLE}\]{_INVISIBLE}\]")


# A placeholder right after the text of a link (`[layouts[[3]]`) comes back with one bracket: the
# service pairs the bracket of the link with the first one of the placeholder.
_HALF = re.compile(r"(?<=[^\[\s])\[(\d+)\]\](?!\])")


def heal(answer: str) -> str:
    """Mend the placeholders of an answer: their dropped bracket, the invisible spaces inside."""
    whole = _SPLIT_PLACEHOLDER.sub(r"[[\1]]", answer)
    return heal_opening(_HALF.sub(r"[[\1]]", whole))


# The placeholders that open a line: a heading marker, a bullet, the first pipe of a row. Some
# services drop one that stands before a short line (`[[3]] Reference` comes back as one word).
_LEAD = re.compile(r"\[\[(\d+)\]\][ \t]*")


def _opening(line: str, shape: Collection[int] | None) -> str:
    """The layout placeholders a line opens with; a name or a code that starts a sentence stays."""
    end = 0
    while (found := _LEAD.match(line, end)) and (shape is None or int(found[1]) in shape):
        end = found.end()
    return line[:end]


def leads(chunk: str, shape: Collection[int] | None = None) -> tuple[str, list[str]]:
    """The chunk without the layout placeholders that open its lines, and those, line by line.

    `shape` names the placeholders that are layout (see `structural`); without it, every
    placeholder that opens a line is taken out.
    """
    lines = chunk.split("\n")
    openings = [_opening(line, shape) for line in lines]
    bodies = [line[len(head) :] for line, head in zip(lines, openings, strict=True)]
    return "\n".join(bodies), openings


def with_leads(answer: str, openings: list[str]) -> str | None:
    """The openings put back at the start of their lines; None when the answer has other lines."""
    lines = answer.split("\n")
    if len(lines) != len(openings):
        return None
    return "\n".join(
        head + line.lstrip() if head else line for line, head in zip(lines, openings, strict=True)
    )


def restore(translated: list[str], kept: list[str]) -> str:
    """Put the kept parts back into the translated pieces, or fail when an answer lost one."""
    text = "\n\n".join(translated)
    lost = missing(text, kept)
    if lost:
        raise ValueError(f"placeholders lost or repeated: {lost}")
    return _PLACEHOLDER.sub(lambda found: kept[int(found[1])], text)


def captions(markdown: str) -> list[str]:
    """The captions of the named fences, each once, in the order they appear."""
    seen: list[str] = []
    for found in _CAPTION.finditer(markdown):
        caption = found["caption"]
        if caption and caption not in seen:
            seen.append(caption)
    return seen


def with_captions(markdown: str, translated: dict[str, str]) -> str:
    """The same page where every caption says what the translation says."""

    def swap(found: re.Match[str]) -> str:
        caption = found.group("caption")
        start = found.start("caption") - found.start()
        end = found.end("caption") - found.start()
        return found[0][:start] + translated.get(caption, caption) + found[0][end:]

    return _CAPTION.sub(swap, markdown)


_CODE_SPAN = re.compile(r"`[^`\n]*`")


def _bold(line: str) -> str:
    """A line whose bold spans hold no space inside their stars: `** a **` reads `**a**`."""
    if "**" not in line or "**" in "".join(_CODE_SPAN.findall(line)):
        return line
    parts = line.split("**")
    if len(parts) % 2 == 0:
        return line
    return "**".join(part.strip() if index % 2 else part for index, part in enumerate(parts))


def _bolds(markdown: str) -> str:
    """Every line outside a fence with its bold spans closed tight, so Markdown draws them."""
    lines, fenced = [], False
    for line in markdown.split("\n"):
        if _FENCE_LINE.match(line):
            fenced = not fenced
        lines.append(line if fenced or _FENCE_LINE.match(line) else _bold(line))
    return "\n".join(lines)


def tidy(markdown: str) -> str:
    """Drop the list comma a service puts at the start of a cell, and the spaces inside bold."""
    return _bolds(_CELL_COMMA.sub(r"\1 ", markdown))


_SPACED_AFTER = re.compile(r"\[\[(\d+)\]\](?=\s)")
_SPACED_BEFORE = re.compile(r"(?<=\s)\[\[(\d+)\]\]")


def respace(answer: str, chunk: str) -> str:
    """Give back the space a service ate between a placeholder and a word.

    A space is put back only where the chunk had one, so a placeholder glued to its word in the
    source stays glued, and a language written without spaces gets none it did not ask for.
    """
    after = {found[1] for found in _SPACED_AFTER.finditer(chunk)}
    before = {found[1] for found in _SPACED_BEFORE.finditer(chunk)}
    answer = re.sub(r"\[\[(\d+)\]\](?=\w)", lambda m: m[0] + " " if m[1] in after else m[0], answer)
    return re.sub(r"(?<=\w)\[\[(\d+)\]\]", lambda m: " " + m[0] if m[1] in before else m[0], answer)
