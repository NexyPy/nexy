"""A reader who chose the modular router sees no example written for `src/routes/`.

A modular project has no `src/routes/`: a page it reads shows the example of `src/apps/` inside a
`<!-- router:modular -->` variant, or keeps the file-route one inside a variant of the other
routers.
"""

from __future__ import annotations

import re
from pathlib import Path

from sites.shared import docs_source

DOCS = Path(__file__).resolve().parents[4] / "docs"
_VARIANT = re.compile(r"<!-- router:([a-z, ]+) -->(.*?)<!-- /router -->", re.DOTALL)
# A code block named after a file of `src/routes/`, or the `routes/` line of a project tree.
_FILE_ROUTE_EXAMPLE = re.compile(r'filename="src/routes/|^[│├└ ─]*routes/', re.MULTILINE)


def _seen_by_modular(text: str) -> str:
    """The page as a modular reader sees it: the variants of the other routers taken out."""
    return _VARIANT.sub(lambda found: found[2] if "modular" in found[1] else "", text)


def _file_route_examples() -> dict[str, int]:
    found: dict[str, int] = {}
    for track in docs_source.read_tracks(DOCS):
        for group in track.groups:
            if group.scope != "core" and "modular" not in group.scope.split():
                continue
            for page in group.pages:
                text = _seen_by_modular(page.path.read_text(encoding="utf-8"))
                count = len(_FILE_ROUTE_EXAMPLE.findall(text))
                if count:
                    found[page.path.relative_to(DOCS).as_posix()] = count
    return found


def test_no_page_shows_more_file_route_examples_to_a_modular_reader():
    assert _file_route_examples() == {}
