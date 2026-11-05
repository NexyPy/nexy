"""Every translated page keeps the skeleton of its English page: code, links, headings, tables."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pytest

from sites.shared import i18n

DOCS = Path(__file__).resolve().parents[3] / "docs"
CODES = [one.code for one in i18n.LANGUAGES if one.code != i18n.DEFAULT]

_FENCE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
_LINK = re.compile(r"\]\(([^)\s]+)\)")
_HEADING = re.compile(r"^(#{1,6}) ", re.MULTILINE)
_ROW = re.compile(r"^\|", re.MULTILINE)
_PLACEHOLDER = re.compile(r"\[\[\s*\d+\s*\]\]")
_FILENAME = re.compile(r'filename="[^"]*"')


def _pairs() -> list[tuple[str, str]]:
    return [
        (code, relative)
        for code in CODES
        for relative in i18n.english_pages(DOCS)
        if (DOCS / code / relative).is_file()
    ]


def _code(text: str) -> list[str]:
    """The fences of a page; a caption is prose and is translated, the code is not."""
    return [_FILENAME.sub("", fence) for fence in _FENCE.findall(text)]


def _prose(text: str) -> str:
    return _FENCE.sub("", text)


PAIRS = _pairs()


@pytest.fixture(scope="module", params=PAIRS, ids=[f"{code}/{rel}" for code, rel in PAIRS])
def pair(request: pytest.FixtureRequest) -> tuple[str, str]:
    code, relative = request.param
    english = (DOCS / relative).read_text(encoding="utf-8")
    return english, (DOCS / code / relative).read_text(encoding="utf-8")


def test_the_code_is_the_code_of_the_english_page(pair):
    english, translated = pair
    assert _code(translated) == _code(english)


def test_every_link_points_where_the_english_one_does(pair):
    english, translated = pair
    assert Counter(_LINK.findall(_prose(translated))) == Counter(_LINK.findall(_prose(english)))


def test_the_outline_has_the_same_headings(pair):
    english, translated = pair
    assert _HEADING.findall(_prose(translated)) == _HEADING.findall(_prose(english))


def test_every_table_row_survives(pair):
    english, translated = pair
    assert len(_ROW.findall(_prose(translated))) == len(_ROW.findall(_prose(english)))


def test_no_placeholder_is_left_behind(pair):
    _english, translated = pair
    assert not _PLACEHOLDER.search(_prose(translated))


def test_no_link_lost_its_words(pair):
    english, translated = pair
    empty = re.compile(r"(?<!!)\[\s*\]\(")
    assert len(empty.findall(_prose(translated))) == len(empty.findall(_prose(english)))
