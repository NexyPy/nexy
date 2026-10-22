"""Contract tests for client-navigation interception decisions.

These mirror the click and popstate handlers emitted into
``__nexy__/src/runtime.ts`` by ``vite_entry.py``.
"""

from nexy.modules.frontend.client_router import (
    is_external_href,
    should_client_navigate_on_popstate,
    should_intercept_click,
)


def test_external_http_href_is_not_intercepted():
    assert is_external_href("https://example.com") is True


def test_hash_href_is_not_intercepted():
    assert is_external_href("#section") is True


def test_mailto_href_is_not_intercepted():
    assert is_external_href("mailto:a@b.c") is True


def test_relative_href_is_not_external():
    assert is_external_href("/about") is False


def test_click_on_blank_target_is_not_intercepted():
    assert (
        should_intercept_click(href="/about", target="_blank", modifier=False, has_route=True)
        is False
    )


def test_click_with_modifier_is_not_intercepted():
    assert (
        should_intercept_click(href="/about", target=None, modifier=True, has_route=True) is False
    )


def test_click_on_external_href_is_not_intercepted():
    assert (
        should_intercept_click(
            href="https://example.com", target=None, modifier=False, has_route=True
        )
        is False
    )


def test_click_without_matching_route_is_not_intercepted():
    assert (
        should_intercept_click(href="/inconnu", target=None, modifier=False, has_route=False)
        is False
    )


def test_click_without_href_is_not_intercepted():
    assert should_intercept_click(href=None, target=None, modifier=False, has_route=True) is False


def test_click_on_known_route_is_intercepted():
    assert (
        should_intercept_click(href="/about", target=None, modifier=False, has_route=True) is True
    )


def test_popstate_without_state_reloads():
    assert should_client_navigate_on_popstate(None) is False


def test_popstate_foreign_state_reloads():
    assert should_client_navigate_on_popstate({"other": 1}) is False


def test_popstate_with_nexy_state_navigates():
    assert should_client_navigate_on_popstate({"nexy": True}) is True
