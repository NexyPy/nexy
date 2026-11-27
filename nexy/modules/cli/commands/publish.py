"""The `nx publish` command: validate a module, then upload one immutable release."""

from __future__ import annotations

import os
from pathlib import Path

import typer
from rich.markup import escape

from nexy.helpers.common.console import console
from nexy.helpers.common.messages import error, warning
from nexy.modules.cli.add.client import DEFAULT_BASE_URL
from nexy.modules.cli.add.manifest import ManifestError
from nexy.modules.cli.publish.client import PublishClient, PublishError
from nexy.modules.cli.publish.imports import undeclared_imports
from nexy.modules.cli.publish.packager import Package, PackageError, package
from nexy.modules.cli.publish.token import resolve_token
from nexy.modules.i18n import t

_HELP_PATH = t("publish.help_path", "Path to the module directory")
_HELP_REGISTRY = t("publish.help_registry", "Registry URL to publish to")
_HELP_DRY_RUN = t("publish.help_dry_run", "Validate and build the release without uploading")


def publish(
    path: Path = typer.Argument(Path("."), help=_HELP_PATH),
    registry: str = typer.Option(DEFAULT_BASE_URL, "--registry", help=_HELP_REGISTRY),
    dry_run: bool = typer.Option(False, "--dry-run", help=_HELP_DRY_RUN),
) -> None:
    """Validate a module and publish it to the Nexy registry."""
    try:
        built = package(path)
    except (ManifestError, PackageError) as problem:
        error(str(problem))
        raise typer.Exit(1) from problem
    _warn(path, built)
    if dry_run:
        _show_dry_run(built)
        return
    _upload(built, registry)


def _warn(path: Path, built: Package) -> None:
    for name in undeclared_imports(path, built.manifest.files):
        message = t("publish.undeclared", "Undeclared relative import: {name}")
        warning(message.format(name=escape(name)))


def _show_dry_run(built: Package) -> None:
    message = t("publish.dry_run", "Dry run: {name}@{version} ({size} bytes, sha256 {checksum})")
    console.print(
        message.format(
            name=escape(built.manifest.name),
            version=built.manifest.version,
            size=len(built.archive),
            checksum=built.checksum,
        )
    )


def _upload(built: Package, registry: str) -> None:
    token = resolve_token(os.environ, Path.home())
    if not token:
        error(t("publish.no_token", "No registry token. Set NEXY_REGISTRY_TOKEN or log in."))
        raise typer.Exit(1)
    try:
        released = PublishClient(registry, token).publish(built.manifest_text, built.archive)
    except PublishError as problem:
        error(str(problem))
        raise typer.Exit(1) from problem
    message = t("publish.published", "Published {name}@{version} to {registry} (sha256:{checksum})")
    console.print(
        message.format(
            name=escape(released.name),
            version=released.version,
            registry=escape(registry),
            checksum=released.checksum,
        )
    )
