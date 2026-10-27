"""docs/reference/python-api.md lists exactly the names the code exports."""

from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

PAGE = Path(__file__).resolve().parents[4] / "docs" / "reference" / "python-api.md"
SECTION = re.compile(r"^## `([\w.]+)`\n(.*?)(?=^## |\Z)", re.DOTALL | re.MULTILINE)
ROW = re.compile(r"^\| ([^|]+) \|", re.MULTILINE)


def _documented() -> dict[str, set[str]]:
    text = PAGE.read_text(encoding="utf-8")
    return {
        module: {name for cell in ROW.findall(body) for name in re.findall(r"`(\w+)`", cell)}
        for module, body in SECTION.findall(text)
    }


DOCUMENTED = _documented()


def test_the_page_covers_four_modules():
    assert set(DOCUMENTED) == {"nexy", "nexy.http", "nexy.decorators", "nexy.testing"}


@pytest.mark.parametrize("module", sorted(DOCUMENTED))
def test_every_documented_name_exists(module):
    exported = vars(importlib.import_module(module))
    assert sorted(name for name in DOCUMENTED[module] if name not in exported) == []


@pytest.mark.parametrize("module", sorted(DOCUMENTED))
def test_every_exported_name_is_documented(module):
    exported = set(importlib.import_module(module).__all__)
    assert sorted(exported - DOCUMENTED[module]) == []
