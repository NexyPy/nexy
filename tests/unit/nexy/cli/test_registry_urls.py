"""Only https registries, or a local http server, are allowed to serve module code."""

from __future__ import annotations

import pytest

from nexy.modules.cli.add.urls import is_allowed_url


@pytest.mark.parametrize("url", ["https://registry.nexypy.dev", "https://example.com/nx"])
def test_is_allowed_url_accepts_https(url):
    assert is_allowed_url(url) is True


@pytest.mark.parametrize(
    "url", ["http://localhost:8000", "http://127.0.0.1:8000", "http://[::1]:8000"]
)
def test_is_allowed_url_accepts_a_local_development_server(url):
    assert is_allowed_url(url) is True


@pytest.mark.parametrize(
    "url", ["http://example.com", "file:///etc/passwd", "ftp://example.com", "https://"]
)
def test_is_allowed_url_refuses_other_sources(url):
    assert is_allowed_url(url) is False
