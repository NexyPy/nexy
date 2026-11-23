"""The error overlay of `nx dev` shows the errors of the app, not the ones of the browser.

In server mode every page is a document of its own, and the starter asks for a view transition
between documents (`@view-transition { navigation: auto; }`). Under `nx dev` Vite injects the CSS
after the page loads, so Chrome aborts that transition and rejects a promise of its own: the
overlay showed it as a "Runtime Error" over the page on every click of a link.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from nexy.helpers.server.devtools import toolbar_markup

ABORTED = (
    "Promise.reject(new DOMException("
    "'Transition was aborted because of invalid state. ViewTransition opt-in disabled',"
    " 'InvalidStateError'))"
)

OVERLAY = "() => !!document.getElementById('nexy-devtools').shadowRoot.querySelector('.overlay')"


def _page_with_toolbar(page: Page) -> None:
    toolbar = toolbar_markup("1.0", {"path": "/"}).decode()
    page.set_content(f"<!doctype html><html><body><p>Page</p>{toolbar}</body></html>")


def _overlay_shown(page: Page, rejection: str) -> bool:
    _page_with_toolbar(page)
    page.evaluate(f"() => {{ {rejection}; }}")
    page.wait_for_timeout(200)
    return bool(
        page.evaluate(
            "() => !!document.getElementById('nexy-devtools').shadowRoot.querySelector('.overlay')"
        )
    )


@pytest.mark.e2e
def test_an_aborted_view_transition_shows_no_overlay(page: Page) -> None:
    assert _overlay_shown(page, ABORTED) is False


@pytest.mark.e2e
def test_a_rejection_of_the_app_still_shows_the_overlay(page: Page) -> None:
    assert _overlay_shown(page, "Promise.reject(new Error('Not saved'))") is True
