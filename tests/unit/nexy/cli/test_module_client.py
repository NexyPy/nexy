"""The CLI reads releases from the registry service over the documented HTTP contract."""

from __future__ import annotations

import hashlib

import httpx
import pytest

from nexy.modules.cli.add.client import ChecksumMismatchError, RegistryModuleClient

BASE = "https://registry.example.com"


def client(handler) -> RegistryModuleClient:
    transport = httpx.MockTransport(handler)
    return RegistryModuleClient(BASE, httpx.Client(base_url=BASE, transport=transport))


RELEASE = {
    "name": "@acme/auth",
    "version": "1.2.0",
    "kind": "source",
    "nexy_version": ">=2.0.0",
    "python_version": ">=3.12",
    "python_dependencies": ["argon2-cffi"],
    "node_dependencies": [],
    "files": ["src/auth.py"],
    "package": None,
    "checksum": "abc",
}


def test_versions_returns_the_available_versions_newest_first():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"versions": ["1.0.0", "1.2.0"]})

    assert client(handler).versions("@acme/auth") == ("1.2.0", "1.0.0")


def test_release_reads_the_service_metadata():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=RELEASE, headers={"X-Signature": "ed25519:abc"})

    release = client(handler).release("@acme/auth", "1.2.0")
    assert (release.nexy_version, release.signature) == (">=2.0.0", "ed25519:abc")


def test_download_returns_an_archive_with_the_right_checksum():
    archive = b"archive bytes"

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=archive,
            headers={"X-Checksum": hashlib.sha256(archive).hexdigest()},
        )

    assert client(handler).download("@acme/auth", "1.2.0") == archive


def test_download_refuses_an_archive_with_the_wrong_checksum():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"tampered", headers={"X-Checksum": "abc"})

    with pytest.raises(ChecksumMismatchError):
        client(handler).download("@acme/auth", "1.2.0")


def test_client_refuses_a_source_that_is_not_https_or_loopback():
    with pytest.raises(ValueError, match="registry URL"):
        RegistryModuleClient("http://example.com")


def test_client_creates_an_httpx_client_when_none_is_injected():
    assert isinstance(RegistryModuleClient(BASE)._client, httpx.Client)
