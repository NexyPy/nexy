"""The whole dev stack lives under `useBasePath` when the setting names a prefix."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, Response, expect

BASE = "http://127.0.0.1"


def _status(response: Response | None) -> int:
    if response is None:
        raise RuntimeError("The navigation did not return a response")
    return response.status


def _home(stack, page: Page) -> None:
    page.goto(f"{BASE}:{stack.server_port}/app/")
    expect(page.get_by_test_id("home")).to_be_visible()


@pytest.mark.e2e
def test_the_prefixed_home_page_is_served(base_path_stack, page: Page):
    assert _status(page.goto(f"{BASE}:{base_path_stack.server_port}/app/")) == 200


@pytest.mark.e2e
def test_the_prefixed_deep_link_is_served(base_path_stack, page: Page):
    response = page.goto(f"{BASE}:{base_path_stack.server_port}/app/docs/a/b/c")
    expect(page.get_by_test_id("docs-path")).to_have_text("a/b/c")
    assert _status(response) == 200


@pytest.mark.e2e
def test_client_navigation_writes_the_prefixed_url(base_path_stack, page: Page):
    _home(base_path_stack, page)
    page.click("a[href='/about']")
    expect(page.get_by_test_id("about")).to_be_visible()
    assert page.url.endswith("/app/about")


@pytest.mark.e2e
def test_client_navigation_keeps_the_document(base_path_stack, page: Page):
    _home(base_path_stack, page)
    page.evaluate("window.__nexyBaseMarker = true")
    page.click("a[href='/about']")
    expect(page.get_by_test_id("about")).to_be_visible()
    assert page.evaluate("window.__nexyBaseMarker === true") is True


@pytest.mark.e2e
def test_the_css_asset_is_served_under_the_prefix(base_path_stack, page: Page):
    _home(base_path_stack, page)
    value = page.evaluate("getComputedStyle(document.body).getPropertyValue('--nexy-e2e')")
    assert value.strip() == "prefixed"


@pytest.mark.e2e
def test_an_action_call_uses_the_prefixed_url(base_path_stack, page: Page):
    _home(base_path_stack, page)
    answer = page.evaluate(
        """async () => {
          const actions = await import('/app/__nexy__/src/actions.ts');
          return [await actions.ping(), actions.ping.url.startsWith('/app/_nx_')];
        }"""
    )
    assert answer == ["pong", True]


@pytest.mark.e2e
def test_the_root_outside_the_prefix_is_not_found(base_path_stack, page: Page):
    assert _status(page.goto(f"{BASE}:{base_path_stack.server_port}/")) == 404
