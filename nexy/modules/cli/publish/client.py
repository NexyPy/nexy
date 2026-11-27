"""Send module releases to the registry over its documented HTTP contract."""

from __future__ import annotations

import base64
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

import httpx

from nexy.modules.cli.add.client import DEFAULT_BASE_URL, checksum_of
from nexy.modules.cli.add.urls import is_allowed_url

_RETRYABLE = frozenset({429, 500, 502, 503, 504})


class PublishError(RuntimeError):
    """The registry did not accept the release."""


class VersionExistsError(PublishError):
    """This name and version is already published."""


@dataclass(frozen=True)
class PublishedRelease:
    """The immutable release the registry recorded."""

    name: str
    version: str
    checksum: str


class PublishClient:
    """Post one signed release, retrying only transient failures."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        token: str = "",
        client: httpx.Client | None = None,
        retries: int = 2,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if not is_allowed_url(base_url):
            raise ValueError(f"invalid registry URL: {base_url}")
        self.token = token
        self.retries = retries
        self._sleep = sleep
        self._client = client if client is not None else httpx.Client(base_url=base_url)

    def publish(self, manifest: str, archive: bytes) -> PublishedRelease:
        """Send the manifest and archive, then verify the registry answer."""
        body = {"manifest": manifest, "archive": base64.b64encode(archive).decode("ascii")}
        attempt = 0
        while True:
            try:
                response = self._client.post("/releases", json=body, headers=self._headers())
            except httpx.TransportError as problem:
                if attempt >= self.retries:
                    raise PublishError("registry is unreachable") from problem
                self._wait(attempt)
                attempt += 1
                continue
            if response.status_code in _RETRYABLE:
                if attempt >= self.retries:
                    raise PublishError(f"registry returned {response.status_code}")
                self._wait(attempt)
                attempt += 1
                continue
            self._check(response)
            return self._release(response.json(), archive)

    def _headers(self) -> Mapping[str, str]:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def _wait(self, attempt: int) -> None:
        self._sleep(0.1 * (attempt + 1))

    def _check(self, response: httpx.Response) -> None:
        if response.status_code == 409:
            raise VersionExistsError(self._detail(response))
        if response.status_code >= 400:
            raise PublishError(self._detail(response))

    def _detail(self, response: httpx.Response) -> str:
        try:
            data = response.json()
            detail = data.get("detail", f"registry returned {response.status_code}")
        except (ValueError, AttributeError):
            detail = f"registry returned {response.status_code}"
        return self._redact(str(detail))

    def _redact(self, text: str) -> str:
        return text.replace(self.token, "[redacted]") if self.token else text

    def _release(self, data: Any, archive: bytes) -> PublishedRelease:
        try:
            name, version, checksum = str(data["name"]), str(data["version"]), str(data["checksum"])
        except (KeyError, TypeError, ValueError) as problem:
            raise PublishError("invalid registry answer") from problem
        if checksum != f"sha256:{checksum_of(archive)}":
            raise PublishError("registry checksum does not match the archive")
        return PublishedRelease(name, version, checksum)
