"""The mobile bar of both sites has the shape of Fumadocs: logo left, search and menu right."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from sites.shared.icons import ICONS
from sites.vanilla import build
from tests.e2e.project import request

SITE = Path(__file__).resolve().parents[3] / "sites" / "nexy"
CSS = (build.HERE / "assets" / "style.css").read_text(encoding="utf-8")
JS = (build.HERE / "assets" / "site.js").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def vanilla(tmp_path_factory: pytest.TempPathFactory) -> str:
    target = tmp_path_factory.mktemp("vanilla")
    build.build(target)
    return (target / "docs" / "index.html").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def nexy() -> str:
    [(_status, _headers, body)] = request(SITE, ("/docs", {}))
    return body


@pytest.fixture(params=["vanilla", "nexy"])
def bar(request: pytest.FixtureRequest) -> str:
    page = request.getfixturevalue(request.param)
    return page.split('<header class="mobilebar">', 1)[1].split("</header>", 1)[0]


def _narrow() -> str:
    """The rules of a narrow screen, where the bar and the drawer live."""
    blocks = re.findall(r"@media \(max-width: 900px\) \{(.*?)\n\}", CSS, re.S)
    return "\n".join(blocks)


def test_the_logo_comes_first(bar):
    assert bar.index('class="brand"') < bar.index('class="search-open"')


def test_the_menu_button_closes_the_row(bar):
    assert bar.index('class="search-open"') < bar.index('class="menu"')


def test_the_menu_button_draws_the_sidebar_icon(bar):
    menu = bar.split('class="menu"', 1)[1].split("</button>", 1)[0]
    assert ICONS["icon_sidebar"] in menu


def test_the_bar_is_56px_high():
    assert "height: 3.5rem" in _narrow().split(".mobilebar {", 1)[1].split("}", 1)[0]


def test_the_bar_draws_a_line_under_it():
    assert "border-bottom: 1px solid var(--line)" in _narrow().split(".mobilebar {", 1)[1]


def test_the_drawer_comes_from_the_end_edge():
    side = _narrow().split("  .side {", 1)[1].split("}", 1)[0]
    assert "inset-inline-end: 0" in side


def test_the_drawer_takes_85_percent_up_to_380px():
    side = _narrow().split("  .side {", 1)[1].split("}", 1)[0]
    assert "width: min(380px, 85vw)" in side


def test_the_drawer_keeps_its_close_button():
    assert ".side-brand .side-toggle, .bar-open { display: none; }" not in CSS


def test_a_menu_folded_on_a_wide_screen_still_opens_on_a_phone():
    assert 'html[data-side="closed"] body.open .side' in _narrow()


def test_the_close_button_of_the_drawer_closes_it_on_a_phone():
    assert "narrow() ? setMenu(false, true) : fold(!html.dataset.side)" in JS
