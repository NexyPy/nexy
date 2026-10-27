"""Every relative link in the documentation, the skills and the entry points resolves to a file."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
ENTRY_POINTS = ["README.md", "llms.txt", "ARCHITECTURE.md", "CONTRIBUTING.md", "AGENTS.md"]
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
EXTERNAL = ("http://", "https://", "mailto:", "#")


def _documents() -> list[Path]:
    found = [ROOT / name for name in ENTRY_POINTS if (ROOT / name).exists()]
    found += sorted((ROOT / "docs").rglob("*.md"))
    found += sorted((ROOT / "skills").rglob("*.md"))
    return found


def _broken(document: Path) -> list[str]:
    missing = []
    for target in LINK.findall(document.read_text(encoding="utf-8")):
        path = target.split("#")[0]
        if target.startswith(EXTERNAL) or not path:
            continue
        if not (document.parent / path).resolve().exists():
            missing.append(target)
    return missing


@pytest.mark.parametrize(
    "document", _documents(), ids=lambda path: path.relative_to(ROOT).as_posix()
)
def test_every_relative_link_points_to_a_file(document):
    assert _broken(document) == []
