"""The stylesheet styles every class the pages and components use: none is left plain by mistake."""

import re
from pathlib import Path

CLASSES = re.compile(r'class="([^"{}]+)"')


def _used() -> set[str]:
    names: set[str] = set()
    for view in Path("src").rglob("*.nexy"):
        for found in CLASSES.findall(view.read_text(encoding="utf-8")):
            names.update(found.split())
    return names


def test_every_class_in_use_is_styled():
    css = Path("src/globale.css").read_text(encoding="utf-8")
    missing = [name for name in _used() if not re.search(rf"\.{name}(?![\w-])", css)]
    assert sorted(missing) == []
