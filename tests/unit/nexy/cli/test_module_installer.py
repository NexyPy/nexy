"""Installing a registry module writes only declared files and only after every check."""

from __future__ import annotations

import io
import json
import tarfile
from importlib.metadata import version
from pathlib import Path

import pytest

from nexy.helpers.common.tasks import TaskResult
from nexy.modules.cli.add import installer as installer_module
from nexy.modules.cli.add.client import Release, checksum_of
from nexy.modules.cli.add.installer import InstallError, ModuleInstaller
from nexy.modules.cli.add.reference import ModuleReference

MANIFEST = """
name = "@acme/auth"
version = "1.2.0"
kind = "source"

[[migrations]]
argv = ["alembic", "upgrade", "head"]

[compatibility]
nexy = ">=2.0.0"
python = ">=3.12"

[dependencies]
python = ["argon2-cffi"]
node = ["zod"]

[source]
files = ["src/auth.py"]

[config.nexyconfig]
useSiteUrl = "https://example.com"
"""

PACKAGE_MANIFEST = """
name = "@acme/auth"
version = "1.2.0"
kind = "package"

[compatibility]
nexy = ">=2.0.0"
python = ">=3.12"

[dependencies]
python = []
node = []

[source]
package = "nexy-auth"
"""


def make_archive(manifest_text: str, files: dict[str, bytes] | None = None) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for name, content in {"nx.toml": manifest_text.encode(), **(files or {})}.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    return buffer.getvalue()


class FakeClient:
    def __init__(self, archive: bytes, release: Release | None = None, versions=("1.2.0",)):
        self.archive = archive
        self.release_data = release or Release(
            "@acme/auth", "1.2.0", checksum_of(archive), ">=2.0.0", ">=3.12", None
        )
        self.versions_data = versions

    def versions(self, name: str) -> tuple[str, ...]:
        return self.versions_data

    def release(self, name: str, version: str) -> Release:
        return self.release_data

    def download(self, name: str, version: str) -> bytes:
        return self.archive


class Runner:
    def __init__(self):
        self.calls: list[tuple[str, list[str], Path]] = []

    def __call__(self, label: str, argv: list[str], root: Path) -> None:
        self.calls.append((label, argv, root))


class Verifier:
    def __init__(self, signer: str | None):
        self.signer = signer

    def verify(self, archive: bytes, signature: str | None) -> str | None:
        return self.signer


def build(tmp_path, monkeypatch, client, **options):
    monkeypatch.chdir(tmp_path)
    runner = Runner()
    nodes: list[list[str]] = []
    options.setdefault("require_signed", False)
    installer = ModuleInstaller(
        client,
        root=tmp_path,
        nexy_version="2.11.2",
        python_version="3.13.0",
        runner=runner,
        install_node=lambda deps, root: nodes.append(deps),
        **options,
    )
    return installer, runner, nodes


def test_installer_writes_the_declared_file(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"secret = 1"})
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    installer.install(ModuleReference("@acme/auth", "1.2.0"))
    assert Path("src/auth.py").read_text() == "secret = 1"


def test_installer_installs_python_and_node_dependencies(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    installer, runner, nodes = build(tmp_path, monkeypatch, FakeClient(raw))
    installer.install(ModuleReference("@acme/auth", "1.2.0"))
    assert runner.calls[0][1] == ["uv", "add", "argon2-cffi"] and nodes == [["zod"]]


def test_installer_installs_the_package_of_a_package_module(tmp_path, monkeypatch):
    raw = make_archive(PACKAGE_MANIFEST)
    installer, runner, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    installer.install(ModuleReference("@acme/auth", "1.2.0"))
    assert runner.calls[0][1] == ["uv", "add", "nexy-auth"]


def test_installer_applies_config_hooks(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    installer.install(ModuleReference("@acme/auth", "1.2.0"))
    assert 'useSiteUrl = "https://example.com"' in Path("nexyconfig.py").read_text()


def test_installer_records_the_installed_version(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    installer.install(ModuleReference("@acme/auth", "1.2.0"))
    assert json.loads(Path(".nexy/modules.json").read_text())["@acme/auth"]["version"] == "1.2.0"


def test_installer_does_nothing_on_a_second_run(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    installer, runner, nodes = build(tmp_path, monkeypatch, FakeClient(raw))
    installer.install(ModuleReference("@acme/auth", "1.2.0"))
    runner.calls.clear()
    nodes.clear()
    result = installer.install(ModuleReference("@acme/auth", "1.2.0"))
    assert result.already_installed is True and runner.calls == [] and nodes == []


def test_installer_keeps_a_file_the_developer_owns(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"from module"})
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    Path("src").mkdir()
    Path("src/auth.py").write_text("mine")
    installer.install(ModuleReference("@acme/auth", "1.2.0"))
    assert Path("src/auth.py").read_text() == "mine"


def test_installer_refuses_a_checksum_mismatch_before_writing(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    release = Release("@acme/auth", "1.2.0", "wrong", ">=2.0.0", ">=3.12", None)
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw, release))
    with pytest.raises(InstallError, match="checksum"):
        installer.install(ModuleReference("@acme/auth", "1.2.0"))


def test_installer_writes_nothing_after_a_checksum_mismatch(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    release = Release("@acme/auth", "1.2.0", "wrong", ">=2.0.0", ">=3.12", None)
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw, release))
    try:
        installer.install(ModuleReference("@acme/auth", "1.2.0"))
    except InstallError:
        pass
    assert not Path("src/auth.py").exists()


def test_installer_refuses_a_signature_mismatch_before_writing(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    release = Release("@acme/auth", "1.2.0", checksum_of(raw), ">=2.0.0", ">=3.12", "bad")
    installer, _, _ = build(
        tmp_path, monkeypatch, FakeClient(raw, release), verifier=Verifier(None)
    )
    with pytest.raises(InstallError, match="signature"):
        installer.install(ModuleReference("@acme/auth", "1.2.0"))


def test_installer_writes_nothing_after_a_signature_mismatch(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    release = Release("@acme/auth", "1.2.0", checksum_of(raw), ">=2.0.0", ">=3.12", "bad")
    installer, _, _ = build(
        tmp_path, monkeypatch, FakeClient(raw, release), verifier=Verifier(None)
    )
    try:
        installer.install(ModuleReference("@acme/auth", "1.2.0"))
    except InstallError:
        pass
    assert not Path("src/auth.py").exists()


def test_installer_refuses_an_incompatible_nexy_version(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST.replace(">=2.0.0", ">=9.0.0"), {"src/auth.py": b"x"})
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    with pytest.raises(InstallError, match="requires Nexy"):
        installer.install(ModuleReference("@acme/auth", "1.2.0"))


def test_installer_refuses_an_incompatible_python_version(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST.replace(">=3.12", ">=4.0"), {"src/auth.py": b"x"})
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    with pytest.raises(InstallError, match="requires Python"):
        installer.install(ModuleReference("@acme/auth", "1.2.0"))


def test_installer_refuses_a_manifest_that_does_not_match_the_release(tmp_path, monkeypatch):
    raw = make_archive(
        MANIFEST.replace('version = "1.2.0"', 'version = "1.3.0"'), {"src/auth.py": b"x"}
    )
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    with pytest.raises(InstallError, match="does not match"):
        installer.install(ModuleReference("@acme/auth", "1.2.0"))


def test_installer_refuses_a_module_with_no_releases(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw, versions=()))
    with pytest.raises(InstallError, match="No releases"):
        installer.install(ModuleReference("@acme/auth", None))


def test_installer_does_not_run_migrations_by_default(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    installer, runner, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    installer.install(ModuleReference("@acme/auth", "1.2.0"))
    assert [call[1] for call in runner.calls if call[0] == "migration"] == []


def test_installer_runs_migrations_when_asked(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    installer, runner, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    installer.install(ModuleReference("@acme/auth", "1.2.0"), migrate=True)
    assert [call[1] for call in runner.calls if call[0] == "migration"] == [
        ["alembic", "upgrade", "head"]
    ]


def test_installer_uses_the_newest_available_release(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    client = FakeClient(raw, versions=("1.2.0", "1.0.0"))
    installer, _, _ = build(tmp_path, monkeypatch, client)
    installer.install(ModuleReference("@acme/auth", None))
    assert json.loads(Path(".nexy/modules.json").read_text())["@acme/auth"]["version"] == "1.2.0"


def test_installer_prints_the_signer(tmp_path, monkeypatch, capsys):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    release = Release("@acme/auth", "1.2.0", checksum_of(raw), ">=2.0.0", ">=3.12", "ed25519:abc")
    installer, _, _ = build(
        tmp_path, monkeypatch, FakeClient(raw, release), verifier=Verifier("Acme Inc")
    )
    installer.install(ModuleReference("@acme/auth", "1.2.0"))
    assert "Verified by Acme Inc" in capsys.readouterr().out


def test_installer_refuses_a_manifest_for_another_module(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST.replace("@acme/auth", "@acme/other"), {"src/auth.py": b"x"})
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    with pytest.raises(InstallError, match="not @acme/auth"):
        installer.install(ModuleReference("@acme/auth", "1.2.0"))


def test_installer_refuses_an_unsigned_module_when_required(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw), require_signed=True)
    with pytest.raises(InstallError, match="requires signed"):
        installer.install(ModuleReference("@acme/auth", "1.2.0"))


def test_installer_ignores_a_corrupt_ledger(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    (tmp_path / ".nexy").mkdir()
    (tmp_path / ".nexy/modules.json").write_text("not json")
    installer.install(ModuleReference("@acme/auth", "1.2.0"))
    assert Path("src/auth.py").exists()


def test_installer_ignores_a_ledger_that_is_not_an_object(tmp_path, monkeypatch):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    (tmp_path / ".nexy").mkdir()
    (tmp_path / ".nexy/modules.json").write_text("[]")
    installer.install(ModuleReference("@acme/auth", "1.2.0"))
    assert Path("src/auth.py").exists()


def test_installer_reports_a_conflicting_file(tmp_path, monkeypatch, capsys):
    raw = make_archive(MANIFEST, {"src/auth.py": b"from module"})
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    (tmp_path / "src").mkdir()
    (tmp_path / "src/auth.py").write_text("mine")
    installer.install(ModuleReference("@acme/auth", "1.2.0"))
    assert "Skipping: src/auth.py already exists." in capsys.readouterr().out


def test_installer_prints_each_migration(tmp_path, monkeypatch, capsys):
    raw = make_archive(MANIFEST, {"src/auth.py": b"x"})
    installer, _, _ = build(tmp_path, monkeypatch, FakeClient(raw))
    installer.install(ModuleReference("@acme/auth", "1.2.0"), migrate=True)
    assert "alembic upgrade head" in capsys.readouterr().out


def test_installer_uses_the_installed_framework_version(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    installer = ModuleInstaller(
        FakeClient(b""),
        root=tmp_path,
        runner=Runner(),
        install_node=lambda *_args: None,
        require_signed=False,
    )
    assert installer.nexy_version == version("nexy")


def test_installer_reads_the_project_signature_policy(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    installer = ModuleInstaller(
        FakeClient(b""),
        root=tmp_path,
        runner=Runner(),
        install_node=lambda *_args: None,
    )
    assert installer.require_signed is False


def test_installer_uses_the_default_task_runner(monkeypatch):
    monkeypatch.setattr(
        installer_module, "run_task", lambda *_args, **_kwargs: TaskResult(True, 0.0)
    )
    assert installer_module._run_task("dependencies", ["uv", "add", "x"], Path(".")) is None


def test_installer_raises_when_the_default_task_runner_fails(monkeypatch):
    monkeypatch.setattr(
        installer_module, "run_task", lambda *_args, **_kwargs: TaskResult(False, 0.0)
    )
    with pytest.raises(InstallError, match="failed"):
        installer_module._run_task("dependencies", ["uv", "add", "x"], Path("."))


def test_installer_uses_the_detected_node_package_manager(monkeypatch):
    calls: list[list[str]] = []
    monkeypatch.setattr(installer_module, "install_packages", lambda deps, root: calls.append(deps))
    installer_module._install_node(["zod"], Path("."))
    assert calls == [["zod"]]
