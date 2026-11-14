"""The interfaces of the docs sites and of the starters use only characters a person types.

The list and its reasons are in `skills/nexy-principles/SKILL.md` ("Characters a person does not
type"). The characters are written as escapes here, so this file follows its own rule.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from sites.shared import i18n

ROOT = Path(__file__).resolve().parents[3]

# Em and en dash, arrows, ellipsis, curly quotes, bullet, middle dot, almost equal, times, check
# marks, ballot x, warning sign, star, box drawing, no-break space, zero-width characters.
FORBIDDEN = frozenset(
    chr(code)
    for code in (
        *(0x2014, 0x2013, 0x2192, 0x2190, 0x21D2, 0x2026),
        *(0x201C, 0x201D, 0x2018, 0x2019, 0x2022, 0x00B7, 0x2248, 0x00D7),
        *(0x2713, 0x2714, 0x2717, 0x26A0, 0x2605, 0x2500, 0x2502, 0x251C, 0x2514),
        *(0x00A0, 0x200B, 0x200C, 0x200D, 0xFEFF),
    )
)

# Where a reader sees the interface: the two docs sites and every starter `nx new` writes.
AREAS = ("sites/", "nexy/modules/cli/templates/")
SUFFIXES = (".html", ".nexy", ".css", ".js", ".jinja2", ".md", ".svg")
GENERATED = "/__nexy__/"


def _interface_files() -> list[str]:
    listed = subprocess.run(
        ["git", "ls-files", *AREAS], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    return sorted(
        name for name in listed if name.endswith(SUFFIXES) and GENERATED not in f"/{name}"
    )


def _found(text: str) -> list[str]:
    return sorted({f"U+{ord(char):04X}" for char in text if char in FORBIDDEN})


@pytest.mark.parametrize("name", _interface_files())
def test_an_interface_file_has_no_character_a_person_does_not_type(name):
    assert _found((ROOT / name).read_text(encoding="utf-8")) == []


def test_the_english_labels_of_the_sites_have_no_character_a_person_does_not_type():
    assert _found(" ".join(i18n.UI[i18n.DEFAULT].values())) == []
