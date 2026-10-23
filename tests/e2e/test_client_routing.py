"""End-to-end client-side routing against a real `nexy dev` stack.

Each test drives a real Chromium against uvicorn + Vite and asserts the
navigation contract the generated ``__nexy__/src/runtime.ts`` promises:
intercepted in-page navigation, no full reload, and history integration.
"""

import pytest
from playwright.sync_api import Page, expect


def _reload_marker(page: Page) -> str:
    """Tag the live document so a full reload is detectable afterwards."""
    token = "nexy-e2e-marker"
    page.evaluate("(t) => { window.__nexyMarker = t }", token)
    return token


def _marker_survived(page: Page, token: str) -> bool:
    return bool(page.evaluate("(t) => window.__nexyMarker === t", token))


@pytest.mark.e2e
def test_dev_stack_serves_home(dev_stack, page: Page):
    page.goto(dev_stack.base_url + "/")
    expect(page.get_by_test_id("home")).to_be_visible()


@pytest.mark.e2e
def test_link_navigates_without_full_reload(dev_stack, page: Page):
    page.goto(dev_stack.base_url + "/")
    expect(page.get_by_test_id("home")).to_be_visible()
    token = _reload_marker(page)

    page.click("a[href='/about']")
    expect(page.get_by_test_id("about")).to_be_visible()
    assert _marker_survived(page, token)


@pytest.mark.e2e
def test_catch_all_route_client_navigation(dev_stack, page: Page):
    page.goto(dev_stack.base_url + "/")
    expect(page.get_by_test_id("home")).to_be_visible()
    token = _reload_marker(page)

    page.click("a[href='/docs/a/b/c']")
    expect(page.get_by_test_id("docs")).to_be_visible()
    assert _marker_survived(page, token)


@pytest.mark.e2e
def test_catch_all_route_reads_path_param(dev_stack, page: Page):
    page.goto(dev_stack.base_url + "/docs/a/b/c")
    expect(page.get_by_test_id("docs-path")).to_have_text("a/b/c")


@pytest.mark.e2e
def test_link_updates_history_url(dev_stack, page: Page):
    page.goto(dev_stack.base_url + "/")
    expect(page.get_by_test_id("home")).to_be_visible()

    page.click("a[href='/about']")
    expect(page.get_by_test_id("about")).to_be_visible()
    assert page.url.endswith("/about")


@pytest.mark.e2e
def test_back_button_restores_previous_route(dev_stack, page: Page):
    page.goto(dev_stack.base_url + "/")
    expect(page.get_by_test_id("home")).to_be_visible()

    page.click("a[href='/about']")
    expect(page.get_by_test_id("about")).to_be_visible()

    page.go_back()
    expect(page.get_by_test_id("home")).to_be_visible()


@pytest.mark.e2e
def test_external_link_is_not_intercepted(dev_stack, page: Page):
    page.goto(dev_stack.base_url + "/")
    expect(page.get_by_test_id("home")).to_be_visible()

    with page.expect_navigation():
        page.click("a[href='https://example.com']")
    assert "example.com" in page.url


@pytest.mark.e2e
def test_direct_deep_link_serves_route(dev_stack, page: Page):
    page.goto(dev_stack.base_url + "/docs/a/b/c")
    expect(page.get_by_test_id("docs")).to_be_visible()
