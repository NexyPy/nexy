"""A scan compiles what its pages need: the layout around them and the components they import.

`nx dev` compiles the whole project before it scans. The bare application (`nexy.app.app` in a
test with `TestClient`, on a fresh checkout) only had its scan, so every page answered "Layout not
available" and lost the components it imports.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

from nexy.core.config import Config
from nexy.helpers.fs.vfs import VFS
from nexy.modules.routers.fbrouter.discovery import RouteDiscovery
from nexy.modules.routers.fbrouter.scanner import LOAD_FAILURES, RouteScanner

LAYOUT = """---
from "../components/badge.nexy" import Badge

children:prop[NexyElement]
---
<body><Badge />{{ children | safe }}</body>
"""

PAGE = """---
from "../components/card.nexy" import Card
---
<main><Card /></main>
"""

FILES = {
    "src/routes/layout.nexy": LAYOUT,
    "src/routes/index.nexy": PAGE,
    "src/components/badge.nexy": "<b>from the layout</b>\n",
    "src/components/card.nexy": "<i>from the page</i>\n",
}


def _forget_compiled_modules() -> None:
    prefix = Config.NAMESPACE.strip("/")
    for name in [name for name in sys.modules if name.split(".")[0] == prefix]:
        del sys.modules[name]


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """The HTML of the home page of a project that was never compiled, after a scan alone."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setattr(Config, "PROJECT_ROOT", tmp_path)
    for name, source in FILES.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(source, encoding="utf-8")
    VFS().clear()
    _forget_compiled_modules()
    route = RouteScanner(RouteDiscovery()).scan().routes[0]
    yield str(getattr(route.module, route.comp_name)())
    VFS().clear()
    _forget_compiled_modules()


def test_a_scanned_page_renders_inside_its_layout(home: str) -> None:
    assert "<b>from the layout</b>" in home


def test_a_scanned_page_renders_the_components_it_imports(home: str) -> None:
    assert "<i>from the page</i>" in home


@pytest.mark.usefixtures("home")
def test_a_layout_that_does_not_compile_is_a_load_failure() -> None:
    Path("src/routes/layout.nexy").write_text("---\nfrom import\n---\n<p></p>\n", encoding="utf-8")
    RouteScanner(RouteDiscovery()).scan()
    assert any("layout.nexy" in failure for failure in LOAD_FAILURES)
