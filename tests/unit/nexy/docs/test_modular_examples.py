"""A reader who chose the modular router sees no example written for `src/routes/`.

A modular project has no `src/routes/`: a page it reads shows the example of `src/apps/` inside a
`<!-- router:modular -->` variant, or keeps the file-route one inside a variant of the other
routers. `KNOWN` lists the pages written before the rule, with how many such examples they still
show; it may only shrink.
"""

from __future__ import annotations

import re
from pathlib import Path

from sites.shared import docs_source

DOCS = Path(__file__).resolve().parents[4] / "docs"
_VARIANT = re.compile(r"<!-- router:([a-z, ]+) -->(.*?)<!-- /router -->", re.DOTALL)
# A code block named after a file of `src/routes/`, or the `routes/` line of a project tree.
_FILE_ROUTE_EXAMPLE = re.compile(r'filename="src/routes/|^[│├└ ─]*routes/', re.MULTILINE)

KNOWN = {
    "getting-started/core-concepts.md": 2,
    "views/frontend/actions-and-navigation.md": 2,
    "views/nexy/README.md": 2,
    "views/nexy/components.md": 2,
    "views/react/differences.md": 4,
    "views/vue/differences.md": 4,
    "views/svelte/differences.md": 4,
    "views/solid/differences.md": 4,
    "views/preact/differences.md": 4,
    "rendering/README.md": 1,
    "rendering/ssr.md": 7,
    "rendering/islands.md": 2,
    "guides/actions.md": 1,
    "guides/databases.md": 3,
    "deployment/README.md": 1,
    "deployment/performance.md": 2,
    "databases/sqlite.md": 3,
    "databases/postgresql.md": 5,
    "databases/neon.md": 1,
    "databases/mysql-mariadb.md": 4,
    "getting-started/coming-from-other-frameworks.md": 4,
    "coming-from/nestjs.md": 1,
    "reference/python-api.md": 2,
    "reference/exceptions.md": 4,
}


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
    worse = {
        page: count for page, count in _file_route_examples().items() if count > KNOWN.get(page, 0)
    }
    assert worse == {}
