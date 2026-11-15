"""The mobile menu of the starter behaves as a sheet: the dialog a phone user expects.

Each starter is scaffolded, built and served, then a real Chromium opens its menu on a phone-sized
screen. The sheet holds the keyboard while it is open, closes on Escape, the scrim and its button,
gives the focus back to the button that opened it, plays its exit before it goes, and leaves room
for a thumb on every link.
"""

from __future__ import annotations

import subprocess  # nosec B404
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Page

from nexy.modules.cli.init.template_setup import _render_local_template
from tests.e2e.conftest import _free_port, _install_node_modules, _run, _wait_for_port

REPO = Path(__file__).resolve().parents[2]
NX = "import sys; from nexy.modules.cli import CLI; sys.argv[0] = 'nx'; CLI()"
PHONE = {"width": 390, "height": 760}
TRIGGER = "button[aria-controls][aria-expanded]"
DIALOG = "[role='dialog'][aria-modal='true']"

# (style, client framework, client-side routing)
STARTERS = [
    ("tailwind", "none", False),
    ("tailwind", "react", True),
    ("tailwind", "preact", True),
    ("tailwind", "solid", True),
    ("tailwind", "vue", True),
]


def _scaffold(project: Path, style: str, framework: str, csr: bool) -> None:
    config = {
        "client_framework": framework,
        "FBRouter": True,
        "project_type": "web",
        "orm": "None",
        "useCSR": csr,
        "style": style,
    }
    _render_local_template("web-fbr", project, config, "demo")


@pytest.fixture(scope="module", params=STARTERS, ids=lambda s: "-".join(map(str, s)))
def starter(request: pytest.FixtureRequest, tmp_path_factory) -> Iterator[str]:
    """One starter, built and served by `nx start`; yields its base URL."""
    project = tmp_path_factory.mktemp("menu") / "app"
    _scaffold(project, *request.param)
    _install_node_modules(project)
    _run(project, sys.executable, "-c", NX, "build")
    port = _free_port()
    server = subprocess.Popen(  # nosec B603 - sys.executable with a fixed launcher
        [sys.executable, "-c", NX, "start", "--port", str(port)],
        cwd=project,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        assert _wait_for_port(port), "nx start did not listen"
        yield f"http://127.0.0.1:{port}"
    finally:
        server.terminate()
        server.wait(timeout=10)


def _open(page: Page, url: str) -> None:
    page.set_viewport_size(PHONE)
    page.goto(url + "/")
    page.locator(TRIGGER).click()
    page.locator(DIALOG).wait_for(state="visible")


def _focus_in_dialog(page: Page) -> bool:
    return bool(page.evaluate(f'!!document.activeElement.closest("{DIALOG}")'))


@pytest.mark.e2e
def test_tabbing_never_leaves_the_open_menu(starter, page: Page):
    _open(page, starter)
    inside = []
    for _ in range(12):
        page.keyboard.press("Tab")
        inside.append(_focus_in_dialog(page))
    assert all(inside)


@pytest.mark.e2e
def test_shift_tab_wraps_inside_the_open_menu(starter, page: Page):
    _open(page, starter)
    for _ in range(8):
        page.keyboard.press("Shift+Tab")
    assert _focus_in_dialog(page)


@pytest.mark.e2e
def test_escape_closes_the_menu_wherever_the_focus_is(starter, page: Page):
    _open(page, starter)
    for _ in range(5):
        page.keyboard.press("Tab")
    page.keyboard.press("Escape")
    page.locator(DIALOG).wait_for(state="hidden")
    assert page.locator(TRIGGER).get_attribute("aria-expanded") == "false"


@pytest.mark.e2e
def test_closing_gives_the_focus_back_to_the_button(starter, page: Page):
    _open(page, starter)
    page.keyboard.press("Escape")
    page.locator(DIALOG).wait_for(state="hidden")
    assert page.evaluate(f'document.activeElement.matches("{TRIGGER}")')


@pytest.mark.e2e
def test_the_scrim_closes_the_menu(starter, page: Page):
    _open(page, starter)
    page.mouse.click(PHONE["width"] - 10, PHONE["height"] // 2)
    page.locator(DIALOG).wait_for(state="hidden")
    assert page.locator(TRIGGER).get_attribute("aria-expanded") == "false"


@pytest.mark.e2e
def test_the_menu_plays_its_exit_before_it_goes(starter, page: Page):
    _open(page, starter)
    page.keyboard.press("Escape")
    assert page.locator(DIALOG).get_attribute("data-state") == "closed"


@pytest.mark.e2e
def test_the_open_menu_shows_one_close_button(starter, page: Page):
    _open(page, starter)
    visible = page.locator("button[aria-label='Close menu']:visible")
    assert visible.count() == 1


@pytest.mark.e2e
def test_every_link_of_the_menu_fits_a_thumb(starter, page: Page):
    _open(page, starter)
    heights = page.locator(f"{DIALOG} a").evaluate_all(
        "links => links.map(link => link.getBoundingClientRect().height)"
    )
    assert min(heights) >= 44


@pytest.mark.e2e
def test_the_menu_is_named_by_a_visible_title(starter, page: Page):
    _open(page, starter)
    title = page.evaluate(
        f'document.getElementById(document.querySelector("{DIALOG}")'
        ".getAttribute('aria-labelledby'))?.textContent.trim()"
    )
    assert title == "Menu"


@pytest.mark.e2e
def test_a_wide_screen_closes_the_menu(starter, page: Page):
    _open(page, starter)
    page.set_viewport_size({"width": 1024, "height": 760})
    page.locator(DIALOG).wait_for(state="hidden")
    assert page.evaluate("document.body.style.overflow") == ""
