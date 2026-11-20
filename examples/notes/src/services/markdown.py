"""Markdown to HTML for the preview. Raw HTML in a note is shown as text, never run: a note is
something someone typed, and its preview must not become a page of its own."""

import re

from markdown_it import MarkdownIt

_MARKDOWN = MarkdownIt("commonmark", {"html": False, "linkify": False}).enable(
    ["table", "strikethrough"]
)
# The signs Markdown writes at the start of a line: headings, quotes, list items.
_LEAD = re.compile(r"^\s*(#{1,6}\s+|>\s*|[-*+]\s+|\d+[.)]\s+)")
_INLINE = re.compile(r"[*_`~]|\[|\]\([^)]*\)")
EXCERPT = 140


def to_html(text: str) -> str:
    return _MARKDOWN.render(text)


def excerpt(text: str) -> str:
    """The first line of a note that holds words, without its Markdown signs, at most 140 long."""
    for line in text.splitlines():
        words = _INLINE.sub("", _LEAD.sub("", line)).strip()
        if words:
            return words if len(words) <= EXCERPT else words[: EXCERPT - 3].rstrip() + "..."
    return ""
