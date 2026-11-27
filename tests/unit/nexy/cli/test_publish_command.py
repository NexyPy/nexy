"`nx publish` validates a module, then sends it with a registry token."""

from __future__ import annotations

import importlib
from dataclasses import dataclass

import pytest
from typer.testing import CliRunner

from nexy.modules.cli import CLI
from nexy.modules.cli.add.manifest import ManifestError
from nexy.modules.cli.publish.client import PublishError, PublishedRelease
from nexy.modules.cli.publish.packager import PackageError

publish = importlib.import_module("nexy.modules.cli.commands.publish")

MANIFEST = "name = \"@acme/auth\"\nversion = \"1.2.0\"\n"
ARCHIVE = b"the-package-bytes"
TOKEN = "registry-secret"


@dataclass(frozen=True)
class Built:
    manifest: object
    manifest_text: str = MANIFEST
    archive: bytes = ARCHIVE
    checksum: str = "abc123"


class Publisher:
    def __init__(self, failure: Exception | None = None) -> None:
        self.calls: list[tuple[str, bytes, str, str]] = []
        self.failure = failure

    def __call__(self, registry: str, token: str):
        return self

    def publish(self, manifest: str, archive: bytes) -> PublishedRelease:
        if self.failure is not None:
            raise self.failure
        self.calls.append((manifest, archive, "", ""))
        return PublishedRelease("@acme/auth", "1.2.0", "abc123")


@pytest.fixture(autouse=True)
def english(monkeypatch):
    monkeypatch.setenv("NEXY_LANG", "en")


def run(tmp_path, *arguments):
    return CliRunner().invoke(CLI, ["publish", str(tmp_path), *arguments])


def fake(monkeypatch, publisher: Publisher, missing: tuple[str, ...] = ()) -> Publisher:
    built = Built(type("Manifest", (), {"name": "@acme/auth", "version": "1.2.0", "files": ()})())
    monkeypatch.setattr(publish, "package", lambda _root: built)
    monkeypatch.setattr(publish, "undeclared_imports", lambda _root, _files: missing)
    monkeypatch.setattr(publish, "resolve_token", lambda _env, _home: TOKEN)
    monkeypatch.setattr(publish, "PublishClient", publisher)
    return publisher


def test_publish_is_registered():
    assert CliRunner().invoke(CLI, ["publish", "--help"]).exit_code == 0


def test_publish_uploads_the_built_release(tmp_path, monkeypatch):
    publisher = fake(monkeypatch, Publisher())
    run(tmp_path)
    assert [(manifest, archive) for manifest, archive, _, _ in publisher.calls] == [
        (MANIFEST, ARCHIVE)
    ]


def test_publish_uses_the_registry_option(tmp_path, monkeypatch):
    registries: list[str] = []

    class Client(Publisher):
        def __call__(self, registry: str, token: str):
            registries.append(registry)
            return self

    fake(monkeypatch, Client())
    run(tmp_path, "--registry", "http://localhost:9000")
    assert registries == ["http://localhost:9000"]


def test_publish_sends_the_resolved_token(tmp_path, monkeypatch):
    tokens: list[str] = []

    class Client(Publisher):
        def __call__(self, registry: str, token: str):
            tokens.append(token)
            return self

    fake(monkeypatch, Client())
    run(tmp_path)
    assert tokens == [TOKEN]


def test_publish_dry_run_does_not_upload(tmp_path, monkeypatch):
    publisher = fake(monkeypatch, Publisher())
    run(tmp_path, "--dry-run")
    assert publisher.calls == []


def test_publish_dry_run_reports_the_checksum(tmp_path, monkeypatch):
    fake(monkeypatch, Publisher())
    result = run(tmp_path, "--dry-run")
    assert "sha256 abc123" in result.stdout


def test_publish_warns_about_undeclared_imports(tmp_path, monkeypatch):
    fake(monkeypatch, Publisher(), missing=("src/helpers.py",))
    result = run(tmp_path, "--dry-run")
    assert "warning: Undeclared relative import: src/helpers.py" in result.stdout


def test_publish_reports_a_missing_token(tmp_path, monkeypatch):
    fake(monkeypatch, Publisher())
    monkeypatch.setattr(publish, "resolve_token", lambda _env, _home: "")
    result = run(tmp_path)
    assert "error: No registry token" in result.stdout


def test_publish_reports_a_package_error(tmp_path, monkeypatch):
    monkeypatch.setattr(publish, "package", lambda _root: (_ for _ in ()).throw(
        PackageError("nx.toml is missing")
    ))
    result = run(tmp_path)
    assert "error: nx.toml is missing" in result.stdout


def test_publish_reports_an_invalid_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(publish, "package", lambda _root: (_ for _ in ()).throw(
        ManifestError("name must be @scope/name")
    ))
    result = run(tmp_path)
    assert "error: name must be @scope/name" in result.stdout


def test_publish_reports_a_rejected_release(tmp_path, monkeypatch):
    fake(monkeypatch, Publisher(PublishError("registry refused the release")))
    result = run(tmp_path)
    assert "error: registry refused the release" in result.stdout


def test_publish_never_prints_the_token(tmp_path, monkeypatch):
    fake(monkeypatch, Publisher())
    result = run(tmp_path)
    assert TOKEN not in result.stdout
