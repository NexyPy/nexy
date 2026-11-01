"""The machine-readable docs index covers every page in the navigation."""

from __future__ import annotations

import re
from pathlib import Path

from sites.shared import docs_source

ROOT = Path(__file__).resolve().parents[4]
DOCS = ROOT / "docs"
LLMS = ROOT / "llms.txt"
DOC_LINK = re.compile(r"\]\((docs/[^)#\s]+\.md)(?:#[^)]*)?\)")


def _doc_links() -> set[str]:
    return set(DOC_LINK.findall(LLMS.read_text(encoding="utf-8")))


def test_llms_index_covers_every_navigation_page():
    pages = {
        page.path.relative_to(ROOT).as_posix()
        for track in docs_source.read_tracks(DOCS)
        for group in track.groups
        for page in group.pages
    }
    pages.add("docs/README.md")

    assert _doc_links() == pages


def test_llms_index_links_exist():
    missing = [link for link in sorted(_doc_links()) if not (ROOT / link).is_file()]

    assert missing == []
