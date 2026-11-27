"""Publishing sends one immutable release and checks the registry answer."""

from __future__ import annotations

import base64
import json

import httpx
import pytest

from nexy.modules.cli.add.client import checksum_of
from nexy.modules.cli.publish.client import (
    PublishClient,
    PublishedRelease,
    PublishError,
    VersionExistsError,
)

TOKEN = "registry-secret"
ARCHIVE = b"the-package-bytes"
MANIFEST = 'name = "@acme/auth"\nversion = "1.2.0"\n'
BASE_URL = "http://localhost:8000"
CHECKED = {
    "name": "@acme/auth",
    "version": "1.2.0",
    "checksum": f"sha256:{checksum_of(ARCHIVE)}",
}


def handler(result, status: int = 201):
    requests: list[httpx.Request] = []

    def send(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if isinstance(result, Exception):
            raise result
        if isinstance(result, list):
            item = result.pop(0)
            if isinstance(item, Exception):
                raise item
            return httpx.Response(item[0], json=item[1])
        return httpx.Response(status, json=result)

    return send, requests


def client(send, token: str = TOKEN, retries: int = 2, sleeps: list[float] | None = None):
    send = send[0] if isinstance(send, tuple) else send
    sleeps = sleeps if sleeps is not None else []
    transport = httpx.MockTransport(send)
    http = httpx.Client(base_url=BASE_URL, transport=transport)
    return PublishClient(
        BASE_URL, token=token, client=http, retries=retries, sleep=lambda _: sleeps.append(0)
    )


def test_publish_sends_the_manifest_and_base64_archive():
    send, requests = handler(CHECKED)
    client(send).publish(MANIFEST, ARCHIVE)
    assert json.loads(requests[0].content) == {
        "manifest": MANIFEST,
        "archive": base64.b64encode(ARCHIVE).decode("ascii"),
    }


def test_publish_sends_the_registry_token():
    send, requests = handler(CHECKED)
    client(send).publish(MANIFEST, ARCHIVE)
    assert requests[0].headers["Authorization"] == f"Bearer {TOKEN}"


def test_publish_omits_authorization_without_a_token():
    send, requests = handler(CHECKED)
    client(send, token="").publish(MANIFEST, ARCHIVE)
    assert "Authorization" not in requests[0].headers


def test_publish_returns_the_published_release():
    release = client(handler(CHECKED)[0]).publish(MANIFEST, ARCHIVE)
    assert release == PublishedRelease("@acme/auth", "1.2.0", CHECKED["checksum"])


def test_publish_verifies_the_registry_checksum():
    wrong = {**CHECKED, "checksum": "sha256:wrong"}
    with pytest.raises(PublishError, match="checksum does not match"):
        client(handler(wrong)[0]).publish(MANIFEST, ARCHIVE)


def test_publish_retries_a_server_error():
    send, requests = handler([(503, {"detail": "busy"}), (201, CHECKED)])
    releases = client(send)
    releases.publish(MANIFEST, ARCHIVE)
    assert len(requests) == 2


def test_publish_retries_a_rate_limit():
    send, requests = handler([(429, {"detail": "slow down"}), (201, CHECKED)])
    client(send).publish(MANIFEST, ARCHIVE)
    assert len(requests) == 2


def test_publish_stops_after_the_configured_retries():
    send, requests = handler([(503, {"detail": "busy"})] * 3)
    with pytest.raises(PublishError, match="registry returned 503"):
        client(send, retries=1).publish(MANIFEST, ARCHIVE)
    assert len(requests) == 2


def test_publish_retries_a_transport_error():
    send, requests = handler([httpx.ConnectError("offline"), (201, CHECKED)])
    client(send).publish(MANIFEST, ARCHIVE)
    assert len(requests) == 2


def test_publish_reports_an_unreachable_registry():
    with pytest.raises(PublishError, match="registry is unreachable"):
        client(handler(httpx.ConnectError("offline")), retries=0).publish(MANIFEST, ARCHIVE)


def test_publish_reports_a_duplicate_release():
    detail = {"detail": "@acme/auth@1.2.0 already exists"}
    with pytest.raises(VersionExistsError, match="@acme/auth@1.2.0 already exists"):
        client(handler(detail, status=409)).publish(MANIFEST, ARCHIVE)


def test_publish_reports_a_rejected_release():
    with pytest.raises(PublishError, match="name must be"):
        client(handler({"detail": "name must be @scope/name"}, status=400)).publish(
            MANIFEST, ARCHIVE
        )


def test_publish_never_echoes_the_token_in_an_error():
    detail = {"detail": f"rejected token {TOKEN}"}
    with pytest.raises(PublishError) as error:
        client(handler(detail, status=400)).publish(MANIFEST, ARCHIVE)
    assert TOKEN not in str(error.value)


def test_publish_reports_an_error_without_a_token():
    with pytest.raises(PublishError, match="bad manifest"):
        client(handler({"detail": "bad manifest"}, status=400), token="").publish(MANIFEST, ARCHIVE)


def test_publish_reports_a_malformed_error():
    def bad_answer(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, text="not json")

    with pytest.raises(PublishError, match="registry returned 400"):
        client(bad_answer).publish(MANIFEST, ARCHIVE)


def test_publish_rejects_an_insecure_registry_url():
    with pytest.raises(ValueError, match="invalid registry URL"):
        PublishClient("http://registry.example.com", token=TOKEN)


def test_publish_reports_an_invalid_registry_answer():
    with pytest.raises(PublishError, match="invalid registry answer"):
        client(handler({"name": "@acme/auth"})).publish(MANIFEST, ARCHIVE)
