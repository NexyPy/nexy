"""Read a release archive without extracting anything outside the declared files."""

from __future__ import annotations

import io
import tarfile
from collections.abc import Iterator
from contextlib import contextmanager
from typing import BinaryIO, cast

_MAX_ARCHIVE_BYTES = 10_000_000


class ArchiveError(ValueError):
    """The archive is too large, incomplete, or holds an unsafe entry."""


@contextmanager
def _open(archive: bytes) -> Iterator[tarfile.TarFile]:
    if len(archive) > _MAX_ARCHIVE_BYTES:
        raise ArchiveError("archive is too large")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        yield tar


def _read(tar: tarfile.TarFile, name: str, refusal: str) -> bytes:
    try:
        member = tar.getmember(name)
    except KeyError as problem:
        raise ArchiveError(f"archive member is missing: {name}") from problem
    if not member.isfile():
        raise ArchiveError(refusal)
    return cast(BinaryIO, tar.extractfile(member)).read()


def read_files(archive: bytes, declared: tuple[str, ...]) -> dict[str, bytes]:
    """The bytes of each declared path, and nothing else from the archive."""
    with _open(archive) as tar:
        return {
            name: _read(tar, name, f"archive member is not a regular file: {name}")
            for name in declared
        }


def manifest_of(archive: bytes) -> str:
    """The `nx.toml` at the root of the archive."""
    with _open(archive) as tar:
        return _read(tar, "nx.toml", "manifest is not a regular file").decode("utf-8")
