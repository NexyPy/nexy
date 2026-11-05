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


def test_a_menu_folded_on_a_wide_screen_still_opens_on_a_phone():
    assert 'html[data-side="closed"] body.open .side' in _narrow()


@pytest.fixture(params=["vanilla", "nexy"])
def sheet(request: pytest.FixtureRequest) -> str:
    """The top row of the drawer: GitHub, the language, the theme and the close button."""
    page = request.getfixturevalue(request.param)
    return page.split('<div class="sheet-bar">', 1)[1].split('<details class="area-select"', 1)[0]


def test_the_sheet_links_to_github(sheet):
    assert 'href="https://github.com/NexyPy/nexy"' in sheet


def test_the_sheet_picks_the_language(sheet):
    assert 'class="lang-select"' in sheet


def test_the_sheet_switches_the_theme(sheet):
    assert "data-theme-toggle" in sheet


def test_the_sheet_ends_with_its_close_button(sheet):
    assert sheet.index("data-theme-toggle") < sheet.index('class="side-close"')


def test_the_close_button_draws_the_sidebar_icon(sheet):
    close = sheet.split('class="side-close"', 1)[1].split("</button>", 1)[0]
    assert ICONS["icon_sidebar"] in close


def test_the_sheet_row_is_hidden_on_a_wide_screen():
    assert ".sheet-bar { display: none; }" in CSS


def test_the_sheet_row_shows_on_a_phone():
    assert ".sheet-bar {\n    display: flex;" in _narrow()


def test_the_logo_of_the_menu_has_no_hover_background():
    rule = ".side .brand, .side .brand:hover { min-height: 0; padding: 0; background: none; }"
    assert rule in CSS


def test_the_page_has_no_frame_on_a_phone():
    panel = _narrow().split("  .panel {", 1)[1].split("}", 1)[0]
    assert "border: 0" in panel and "border-radius: 0" in panel and "margin: 0" in panel


def test_the_bar_of_the_page_leaves_its_controls_to_the_sheet():
    assert ".panel-bar > :not(.progress) { display: none; }" in _narrow()


def test_every_theme_switch_changes_the_theme():
    assert "$$('[data-theme-toggle]')" in JS


def test_every_language_picker_closes_on_a_click_elsewhere():
    assert "$$('.lang-select').forEach" in JS


def test_the_close_button_closes_the_drawer():
    assert "$('.side-close').addEventListener('click', () => setMenu(false, true))" in JS
