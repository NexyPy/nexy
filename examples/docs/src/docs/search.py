"""Search the docs: every heading of every page is an entry, found when it holds every word."""

import re
from dataclasses import dataclass

from src.docs.nav import PAGES, Page

_HEADING = re.compile(r"^(#{1,3})\s+(.*)$")
_FENCE = re.compile(r"^(```|~~~)")
_MARKS = re.compile(r"[`*_>|]|\[([^\]]*)\]\([^)]*\)")


@dataclass(frozen=True)
class Entry:
    title: str
    heading: str
    url: str
    text: str
    snippet: str = ""


def _slug(text: str) -> str:
    """The id Nexy gives a heading: the same rule, so a result lands on its heading."""
    slug = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "-", slug)


def _plain(line: str) -> str:
    return re.sub(r"\s+", " ", _MARKS.sub(lambda m: m.group(1) or " ", line)).strip()


def _entry(page: Page, title: str, heading: str, lines: list[str]) -> Entry:
    anchor = "" if heading == title else f"#{_slug(heading)}"
    return Entry(title, heading, page.url + anchor, _plain(" ".join(lines)))


def _entries(page: Page) -> list[Entry]:
    """One entry per heading, with the text up to the next heading. Code is searched too."""
    entries, title, heading, lines = [], "", "", []
    for line in page.file.read_text(encoding="utf-8").splitlines():
        found = _HEADING.match(line)
        if found and not _FENCE.match(line):
            if heading:
                entries.append(_entry(page, title, heading, lines))
            heading, lines = _plain(found.group(2)), []
            title = title or heading
        elif not _FENCE.match(line):
            lines.append(line)
    entries.append(_entry(page, title, heading, lines))
    return entries


ENTRIES = [entry for page in PAGES for entry in _entries(page)]


def _snippet(text: str, word: str, width: int = 140) -> str:
    """The words around the first match, so the result shows why it was found."""
    at = max(text.lower().find(word) - width // 3, 0)
    if at:
        at = text.find(" ", at) + 1  # start on a whole word
    cut = text[at : at + width]
    return ("..." if at else "") + cut + ("..." if at + width < len(text) else "")


def _score(entry: Entry, words: list[str]) -> int | None:
    haystack = f"{entry.title} {entry.heading} {entry.text}".lower()
    if not all(word in haystack for word in words):
        return None
    return sum(_weight(entry, word) for word in words)


def _weight(entry: Entry, word: str) -> int:
    """A word in the page title counts most, then in the heading, then in the text."""
    if word in entry.title.lower():
        return 20
    return 10 if word in entry.heading.lower() else 1


def search(query: str, limit: int = 8) -> list[Entry]:
    """The entries that hold every word of the query, the ones that name it in a title first."""
    words = query.lower().split()
    if not words:
        return []
    scored = [(score, entry) for entry in ENTRIES if (score := _score(entry, words)) is not None]
    scored.sort(key=lambda pair: -pair[0])
    return [
        Entry(e.title, e.heading, e.url, e.text, _snippet(e.text, words[0])) for _, e in scored
    ][:limit]
