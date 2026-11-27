"""The URL policy shared by remote components and module registries."""

from __future__ import annotations

from urllib.parse import urlsplit

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def is_allowed_url(url: str) -> bool:
    """Allow https, plus plain http only for a loopback development server."""
    parts = urlsplit(url)
    if parts.scheme == "https":
        return bool(parts.hostname)
    return parts.scheme == "http" and parts.hostname in _LOCAL_HOSTS
