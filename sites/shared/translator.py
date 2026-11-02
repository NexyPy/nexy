"""What a translator is allowed to see of a Markdown page, and how its answer is put back.

A page of `docs/` is mostly prose, but every code fence, inline code, link target, table pipe and
heading marker is skeleton: translating it breaks the page. `protect` turns each of those into a
numbered placeholder, `chunks` cuts the remaining text into pieces a service accepts, and `restore`
puts the kept parts back and refuses an answer that lost one.

Nothing here talks to a network: the same three functions serve the tests and the translator script.
"""

from __future__ import annotations

import re

_PLACEHOLDER = re.compile(r"\[\[\s*(\d+)\s*\]\]")

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

# A named fence shows its file or drawing name in a caption. The fence itself is code and never
# travels; the caption is prose, and it is the only part of a fence a reader sees translated.
_CAPTION = re.compile(r'^```\w+[ \t]+filename="(?P<caption>[^"\n]*)"', re.MULTILINE)
# A cell that starts with a list comma is an artefact of the service, not punctuation.
_CELL_COMMA = re.compile(r"(\|[ \t]*),[ \t]*")


def protect(markdown: str) -> tuple[str, list[str]]:
    """The page as a template where every kept part is `[[n]]`, and the parts themselves."""
    kept: list[str] = []

    def swap(found: re.Match[str]) -> str:
        kept.append(found[0])
        return f"[[{len(kept) - 1}]]"

    return _KEPT.sub(swap, markdown), kept


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


def placeholders(text: str) -> list[int]:
    """The placeholder numbers a piece of text carries, in the order they appear."""
    return [int(found[1]) for found in _PLACEHOLDER.finditer(text)]


def missing(translated: str, kept: list[str]) -> list[int]:
    """The placeholders the answer dropped or repeated, so the caller can retry before giving up."""
    seen = placeholders(translated)
    return [index for index in range(len(kept)) if seen.count(index) != 1]


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


def tidy(markdown: str) -> str:
    """Drop the list comma a service inserts at the start of a table cell."""
    return _CELL_COMMA.sub(r"\1 ", markdown)
