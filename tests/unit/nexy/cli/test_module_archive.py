"""Release archives give the installer only the files the manifest declares."""

from __future__ import annotations

import io
import tarfile

import pytest

from nexy.modules.cli.add.archive import ArchiveError, manifest_of, read_files

MANIFEST = b'name = "@acme/auth"\nversion = "1.2.0"\n'


def make_archive(entries: dict[str, bytes], *, symlink: tuple[str, str] | None = None) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for name, content in entries.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
        if symlink is not None:
            info = tarfile.TarInfo(symlink[0])
            info.type = tarfile.SYMTYPE
            info.linkname = symlink[1]
            tar.addfile(info)
    return buffer.getvalue()


def test_read_files_returns_the_declared_contents():
    raw = make_archive({"nx.toml": MANIFEST, "src/auth.py": b"secret = 1"})
    assert read_files(raw, ("src/auth.py",)) == {"src/auth.py": b"secret = 1"}


def test_read_files_ignores_an_undeclared_file():
    raw = make_archive({"nx.toml": MANIFEST, "src/auth.py": b"kept", "src/other.py": b"skip"})
    assert list(read_files(raw, ("src/auth.py",))) == ["src/auth.py"]


def test_read_files_refuses_a_symlink():
    raw = make_archive({"nx.toml": MANIFEST, "src/auth.py": b"x"}, symlink=("src/link.py", "/etc/passwd"))
    with pytest.raises(ArchiveError, match="not a regular file"):
        read_files(raw, ("src/link.py",))


def test_read_files_refuses_a_missing_file():
    raw = make_archive({"nx.toml": MANIFEST})
    with pytest.raises(ArchiveError, match="missing"):
        read_files(raw, ("src/auth.py",))


def test_read_files_refuses_an_oversized_archive():
    with pytest.raises(ArchiveError, match="too large"):
        read_files(b"x" * 10_000_001, ("src/auth.py",))


def test_manifest_of_reads_the_manifest_from_the_archive():
    raw = make_archive({"nx.toml": MANIFEST, "src/auth.py": b"x"})
    assert manifest_of(raw) == MANIFEST.decode()


def test_manifest_of_refuses_a_manifest_that_is_not_a_file():
    raw = make_archive({"src/auth.py": b"x"}, symlink=("nx.toml", "/etc/passwd"))
    with pytest.raises(ArchiveError, match="manifest is not a regular file"):
        manifest_of(raw)
