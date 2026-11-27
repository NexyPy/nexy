"""`nx add @scope/name` installs a module from the configured registry."""

from __future__ import annotations

import importlib

import pytest
from typer.testing import CliRunner

from nexy.modules.cli import CLI
from nexy.modules.cli.add.installer import InstallError

# The package re-exports the command function; monkeypatching needs the module.
add = importlib.import_module("nexy.modules.cli.commands.add")


def run_add(*arguments):
    return CliRunner().invoke(CLI, ["add", *arguments])


@pytest.fixture(autouse=True)
def english(monkeypatch):
    monkeypatch.setenv("NEXY_LANG", "en")


class Installer:
    def __init__(self):
        self.calls: list[tuple[str, str | None, bool]] = []

    def install(self, reference, migrate=False):
        self.calls.append((reference.name, reference.version, migrate))


def fake_installer(monkeypatch):
    installer = Installer()
    monkeypatch.setattr(add, "RegistryModuleClient", lambda url: f"client:{url}")
    monkeypatch.setattr(add, "ModuleInstaller", lambda _client: installer)
    return installer


def test_add_installs_a_namespaced_module(nexy_project, monkeypatch):
    nexy_project()
    installer = fake_installer(monkeypatch)
    run_add("@acme/auth")
    assert installer.calls == [("@acme/auth", None, False)]


def test_add_passes_an_exact_module_version(nexy_project, monkeypatch):
    nexy_project()
    installer = fake_installer(monkeypatch)
    run_add("@acme/auth@1.2.0")
    assert installer.calls == [("@acme/auth", "1.2.0", False)]


def test_add_runs_migrations_only_with_the_flag(nexy_project, monkeypatch):
    nexy_project()
    installer = fake_installer(monkeypatch)
    run_add("@acme/auth", "--migrate")
    assert installer.calls == [("@acme/auth", None, True)]


def test_add_reads_the_module_registry_from_the_project_config(nexy_project, monkeypatch):
    nexy_project('useModuleRegistry = "https://registry.example.com"')
    urls: list[str] = []
    monkeypatch.setattr(add, "RegistryModuleClient", lambda url: urls.append(url))
    monkeypatch.setattr(add, "ModuleInstaller", lambda _client: Installer())
    run_add("@acme/auth")
    assert urls == ["https://registry.example.com"]


def test_add_refuses_a_malformed_module_reference(nexy_project, monkeypatch):
    nexy_project()
    fake_installer(monkeypatch)
    result = run_add("@Acme/auth")
    assert "error: invalid module reference: @Acme/auth" in result.stdout


def test_add_reports_an_install_error(nexy_project, monkeypatch):
    nexy_project()
    installer = fake_installer(monkeypatch)

    def fail(_reference, **_options):
        raise InstallError("archive checksum mismatch")

    installer.install = fail
    result = run_add("@acme/auth")
    assert "error: archive checksum mismatch" in result.stdout


def test_add_does_not_mix_a_module_with_a_component(nexy_project, monkeypatch):
    nexy_project()
    fake_installer(monkeypatch)
    result = run_add("@acme/auth", "button")
    assert "nexy add [COMPONENT_NAME or URL]..." in result.stdout


def test_add_rejects_component_flags_for_a_module(nexy_project, monkeypatch):
    nexy_project()
    installer = fake_installer(monkeypatch)
    result = run_add("@acme/auth", "--ui")
    assert "error:" in result.stdout and installer.calls == []
