"""Build the immutable archive a module release sends to the registry."""

from __future__ import annotations

import io
import tarfile
from dataclasses import dataclass
from pathlib import Path

from nexy.modules.cli.add.client import checksum_of
from nexy.modules.cli.add.manifest import ModuleManifest, parse_manifest

_MANIFEST = "nx.toml"


class PackageError(ValueError):
    """The module directory cannot be published as declared."""


@dataclass(frozen=True)
class Package:
    """The validated manifest and the exact bytes sent to the registry."""

    manifest: ModuleManifest
    manifest_text: str
    archive: bytes
    checksum: str


def package(root: Path) -> Package:
    """Archive the manifest and every file it declares, and nothing else."""
    path, text = _manifest(root)
    manifest = parse_manifest(text)
    entries = [("nx.toml", path)]
    entries.extend((name, _declared(root, name)) for name in manifest.files)
    archive = _archive(entries)
    return Package(manifest, text, archive, checksum_of(archive))


def _manifest(root: Path) -> tuple[Path, str]:
    path = root / _MANIFEST
    if not path.is_file():
        raise PackageError(f"{_MANIFEST} is missing")
    return path, path.read_text(encoding="utf-8")


def _declared(root: Path, name: str) -> Path:
    path = root / name
    if not path.exists():
        raise PackageError(f"{name} is missing")
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise PackageError(f"{name} is not a regular file")
    return path


def _archive(entries: list[tuple[str, Path]]) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as tar:
        for name, path in entries:
            data = path.read_bytes()
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            tar.addfile(info, io.BytesIO(data))
    return output.getvalue()
