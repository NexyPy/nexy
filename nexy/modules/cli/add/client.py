"""A small client for the module registry HTTP service."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol

import httpx

from nexy.modules.cli.add.urls import is_allowed_url

DEFAULT_BASE_URL = "https://registry.nexypy.dev"


class ChecksumMismatchError(ValueError):
    """The archive from the registry does not match the checksum in its response."""


@dataclass(frozen=True)
class Release:
    """The metadata the service publishes for one immutable version."""

    name: str
    version: str
    checksum: str
    nexy_version: str
    python_version: str
    signature: str | None


class ModuleClient(Protocol):
    """What the installer needs from a registry client."""

    def versions(self, name: str) -> tuple[str, ...]: ...

    def release(self, name: str, version: str) -> Release: ...

    def download(self, name: str, version: str) -> bytes: ...


def checksum_of(archive: bytes) -> str:
    return hashlib.sha256(archive).hexdigest()


class RegistryModuleClient:
    """Reads releases from a registry over the documented HTTP contract."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, client: httpx.Client | None = None) -> None:
        if not is_allowed_url(base_url):
            raise ValueError(f"invalid registry URL: {base_url}")
        self.base_url = base_url
        self._client = client if client is not None else httpx.Client(base_url=base_url)

    def versions(self, name: str) -> tuple[str, ...]:
        response = self._client.get("/versions", params={"name": name})
        response.raise_for_status()
        return tuple(sorted((str(item) for item in response.json()["versions"]), reverse=True))

    def release(self, name: str, version: str) -> Release:
        response = self._client.get("/release", params={"name": name, "version": version})
        response.raise_for_status()
        return _release_of(response.json(), response.headers.get("X-Signature"))

    def download(self, name: str, version: str) -> bytes:
        response = self._client.get("/download", params={"name": name, "version": version})
        response.raise_for_status()
        if response.headers.get("X-Checksum") != checksum_of(response.content):
            raise ChecksumMismatchError(f"{name}@{version}")
        return response.content


def _release_of(data: dict[str, object], signature: str | None) -> Release:
    return Release(
        name=str(data["name"]),
        version=str(data["version"]),
        checksum=str(data["checksum"]),
        nexy_version=str(data["nexy_version"]),
        python_version=str(data["python_version"]),
        signature=signature,
    )
