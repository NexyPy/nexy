"""Install one module from the registry after every check has passed."""

from __future__ import annotations

import json
import platform
from collections.abc import Callable
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path
from typing import Any

from rich.markup import escape

from nexy.core.config import Config
from nexy.helpers.common.console import console
from nexy.helpers.common.messages import warning
from nexy.helpers.common.tasks import run_task
from nexy.helpers.fs.path import PathUtil
from nexy.modules.cli.add.archive import manifest_of, read_files
from nexy.modules.cli.add.client import ModuleClient, Release, checksum_of
from nexy.modules.cli.add.compatibility import is_compatible
from nexy.modules.cli.add.config import apply_config_hooks
from nexy.modules.cli.add.manifest import ModuleManifest, parse_manifest
from nexy.modules.cli.add.reference import ModuleReference
from nexy.modules.cli.add.signature import SignatureError, SignatureVerifier, verify_signature
from nexy.modules.cli.init.dependencies import install_packages
from nexy.modules.i18n import t

Runner = Callable[[str, list[str], Path], None]
NodeInstaller = Callable[[list[str], Path], None]


class InstallError(ValueError):
    """The module cannot be installed without breaking the project's contract."""


@dataclass(frozen=True)
class InstallResult:
    """What happened during one install attempt."""

    name: str
    version: str
    signer: str | None
    already_installed: bool
    written: tuple[str, ...]
    skipped: tuple[str, ...]


def _run_task(label: str, argv: list[str], root: Path) -> None:
    result = run_task(label, argv, cwd=root, done=f"{label} done")
    if not result.ok:
        raise InstallError(f"{label} failed")


def _install_node(deps: list[str], root: Path) -> None:
    install_packages(deps, root)


def _ledger(root: Path) -> dict[str, dict[str, str]]:
    path = root / ".nexy/modules.json"
    if not path.exists():
        return {}
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _save_ledger(root: Path, ledger: dict[str, dict[str, str]]) -> None:
    path = root / ".nexy/modules.json"
    PathUtil.write_file(path, json.dumps(ledger, indent=2, sort_keys=True) + "\n")


def _write_files(root: Path, files: dict[str, bytes]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    written: list[str] = []
    skipped: list[str] = []
    for name, content in files.items():
        path = root / name
        if path.exists():
            warning(t("add.exists", "Skipping: {path} already exists.").format(path=name))
            skipped.append(name)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        console.print(f" [green]+[/green] {escape(name)}")
        written.append(name)
    return tuple(written), tuple(skipped)


def _install_dependencies(
    runner: Runner, node_installer: NodeInstaller, manifest: ModuleManifest, root: Path
) -> None:
    python = [*manifest.python_dependencies]
    if manifest.package:
        python.append(manifest.package)
    if python:
        runner("dependencies", ["uv", "add", *python], root)
    if manifest.node_dependencies:
        node_installer([*manifest.node_dependencies], root)


def _run_migrations(runner: Runner, manifest: ModuleManifest, root: Path) -> None:
    for argv in manifest.migrations:
        console.print(f" [green]+[/green] {escape(' '.join(argv))}")
        runner("migration", [*argv], root)


def _checked_manifest(
    archive: bytes,
    reference: ModuleReference,
    release: Release,
    nexy_version: str,
    python_version: str,
) -> ModuleManifest:
    manifest = parse_manifest(manifest_of(archive))
    if manifest.name != reference.name:
        raise InstallError(f"release manifest is for {manifest.name}, not {reference.name}")
    if manifest.version != release.version:
        raise InstallError("release manifest version does not match the release")
    if not is_compatible(manifest.nexy_version, nexy_version):
        raise InstallError(f"module requires Nexy {manifest.nexy_version}")
    if not is_compatible(manifest.python_version, python_version):
        raise InstallError(f"module requires Python {manifest.python_version}")
    return manifest


def _verified_signer(
    verifier: SignatureVerifier | None,
    archive: bytes,
    release: Release,
    required: bool,
) -> str | None:
    try:
        return verify_signature(verifier, archive, release.signature, required)
    except SignatureError as problem:
        raise InstallError(str(problem)) from problem


def _already_installed(ledger: dict[str, dict[str, str]], name: str, selected: str) -> bool:
    """Say whether this exact version is already recorded in the project."""
    if ledger.get(name, {}).get("version") != selected:
        return False
    message = t("add.module.already", "{name}@{version} is already installed.")
    console.print(message.format(name=name, version=selected))
    return True


def _report_install(name: str, selected: str, signer: str | None) -> None:
    """Print the install line and, when there is one, the identity of the signer."""
    console.print(
        t("add.module.installed", "Installed {name}@{version}").format(name=name, version=selected)
    )
    if signer:
        console.print(t("add.module.signed", "Verified by {signer}").format(signer=signer))


class ModuleInstaller:
    """Resolve, check and install one registry module into a Nexy project."""

    def __init__(
        self,
        client: ModuleClient,
        root: Path = Path("."),
        nexy_version: str | None = None,
        python_version: str | None = None,
        runner: Runner | None = None,
        install_node: NodeInstaller | None = None,
        verifier: SignatureVerifier | None = None,
        require_signed: bool | None = None,
    ) -> None:
        self.client = client
        self.root = root
        self.nexy_version = nexy_version or version("nexy")
        self.python_version = python_version or platform.python_version()
        self.runner = runner or _run_task
        self.install_node = install_node or _install_node
        self.verifier = verifier
        self.require_signed = (
            Config().useRequireSignedModules if require_signed is None else require_signed
        )

    def install(self, reference: ModuleReference, migrate: bool = False) -> InstallResult:
        """Install the pinned version, or the newest release, once."""
        selected = self._selected_version(reference)
        ledger = _ledger(self.root)
        if _already_installed(ledger, reference.name, selected):
            return InstallResult(reference.name, selected, None, True, (), ())
        release = self.client.release(reference.name, selected)
        archive = self._archive(release, reference)
        manifest = _checked_manifest(
            archive, reference, release, self.nexy_version, self.python_version
        )
        signer = _verified_signer(self.verifier, archive, release, self.require_signed)
        written, skipped = self._apply(archive, manifest)
        if migrate:
            _run_migrations(self.runner, manifest, self.root)
        ledger[reference.name] = {"version": selected, "checksum": release.checksum}
        _save_ledger(self.root, ledger)
        _report_install(reference.name, selected, signer)
        return InstallResult(reference.name, selected, signer, False, written, skipped)

    def _selected_version(self, reference: ModuleReference) -> str:
        if reference.version:
            return reference.version
        versions = self.client.versions(reference.name)
        if not versions:
            raise InstallError(
                t("add.module.no_releases", "No releases found for {name}").format(
                    name=reference.name
                )
            )
        return versions[0]

    def _archive(self, release: Release, reference: ModuleReference) -> bytes:
        archive = self.client.download(reference.name, release.version)
        if checksum_of(archive) != release.checksum:
            raise InstallError("archive checksum mismatch")
        return archive

    def _apply(self, archive: bytes, manifest: ModuleManifest) -> tuple[tuple[str, ...], ...]:
        files = read_files(archive, manifest.files)
        written, skipped = _write_files(self.root, files)
        for change in apply_config_hooks(manifest.config, self.root):
            console.print(f" [green]+[/green] {escape(change)}")
        _install_dependencies(self.runner, self.install_node, manifest, self.root)
        return written, skipped
