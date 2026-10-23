"""The dev server must expose one origin; Vite is an implementation detail.

These tests guard the single-port contract: the browser only ever needs the
uvicorn port. Vite assets are served through that origin, the application is
never shadowed by Vite, and Nexy's own HMR socket keeps its own connection.
"""

import urllib.request

import pytest
from websockets.sync.client import connect

from tests.e2e.conftest import DevStack


def _fetch(url: str) -> tuple[int, str]:
    with urllib.request.urlopen(url, timeout=20) as response:
        return response.status, response.read().decode("utf-8", "replace")


@pytest.mark.e2e
def test_vite_client_is_served_from_app_origin(dev_stack: DevStack):
    status, body = _fetch(dev_stack.base_url + "/@vite/client")
    assert status == 200 and "createHotContext" in body


@pytest.mark.e2e
def test_page_uses_same_origin_script_urls(dev_stack: DevStack):
    _, html = _fetch(dev_stack.base_url + "/")
    assert 'src="/@vite/client"' in html


@pytest.mark.e2e
def test_page_does_not_leak_the_internal_vite_port(dev_stack: DevStack):
    _, html = _fetch(dev_stack.base_url + "/")
    assert f":{dev_stack.client_port}/" not in html


@pytest.mark.e2e
def test_vite_does_not_shadow_application_routes(dev_stack: DevStack):
    status, body = _fetch(dev_stack.base_url + "/about")
    assert status == 200 and "data-nexy-fw" in body


@pytest.mark.e2e
def test_nexy_hmr_socket_is_served_by_the_app(dev_stack: DevStack):
    url = dev_stack.base_url.replace("http://", "ws://") + "/_nexy/hmr"
    with connect(url, open_timeout=20) as socket:
        assert socket.close_reason is None
