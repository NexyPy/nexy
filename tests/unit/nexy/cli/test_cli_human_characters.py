"""The prompts of the CLI use only characters a person types.

The list and its reasons are in `skills/nexy-principles/SKILL.md` ("Characters a person does not
type"), as the `FORBIDDEN` set of `tests/unit/sites/test_human_characters.py`, reused here.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.unit.sites.test_human_characters import FORBIDDEN

ROOT = Path(__file__).resolve().parents[4]
AREAS = (Path("nexy/modules/cli"), Path("nexy/modules/i18n/en.json"))


def _prompt_files() -> list[Path]:
    files: list[Path] = []
    for area in AREAS:
        path = ROOT / area
        files.extend(sorted(path.rglob("*.py")) if path.is_dir() else [path])
    return files


def _found(text: str) -> list[str]:
    return sorted({f"U+{ord(char):04X}" for char in text if char in FORBIDDEN})


@pytest.mark.parametrize("path", _prompt_files(), ids=lambda path: str(path.relative_to(ROOT)))
def test_a_prompt_file_has_no_character_a_person_does_not_type(path: Path) -> None:
    assert _found(path.read_text(encoding="utf-8")) == []
