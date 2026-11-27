"""Publishing a module archives only the files its manifest declares."""

from __future__ import annotations

import hashlib
import io
import tarfile
from pathlib import Path

import pytest

from nexy.modules.cli.add.manifest import ManifestError
from nexy.modules.cli.publish.packager import PackageError, package

MANIFEST = """
name = "@acme/auth"
version = "1.2.0"
kind = "source"

[compatibility]
nexy = ">=2.0.0"
python = ">=3.12"

[dependencies]
python = []
node = []

[source]
files = ["src/auth.py"]
"""


def project(tmp_path: Path, manifest: str = MANIFEST) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "nx.toml").write_text(manifest, encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/auth.py").write_text("token = 1\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("private\n", encoding="utf-8")
    return tmp_path


def names(archive: bytes) -> tuple[str, ...]:
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        return tuple(tar.getnames())


def test_package_reads_the_manifest(tmp_path):
    built = package(project(tmp_path))
    assert built.manifest.name == "@acme/auth"


def test_package_archives_only_declared_files(tmp_path):
    built = package(project(tmp_path))
    assert names(built.archive) == ("nx.toml", "src/auth.py")


def test_package_computes_the_checksum_of_the_archive(tmp_path):
    built = package(project(tmp_path))
    assert built.checksum == hashlib.sha256(built.archive).hexdigest()


def test_package_keeps_the_manifest_text(tmp_path):
    root = project(tmp_path)
    built = package(root)
    assert built.manifest_text == (root / "nx.toml").read_text(encoding="utf-8")


def test_package_reports_a_missing_manifest(tmp_path):
    with pytest.raises(PackageError, match="nx.toml is missing"):
        package(tmp_path)


def test_package_reports_a_missing_declared_file(tmp_path):
    root = project(tmp_path)
    (root / "src/auth.py").unlink()
    with pytest.raises(PackageError, match="src/auth.py is missing"):
        package(root)


def test_package_refuses_a_symlinked_declared_file(tmp_path):
    root = project(tmp_path)
    (root / "src/auth.py").unlink()
    (root / "src/auth.py").symlink_to("/etc/passwd")
    with pytest.raises(PackageError, match="src/auth.py is not a regular file"):
        package(root)


def test_package_propagates_an_invalid_manifest(tmp_path):
    root = project(tmp_path, MANIFEST.replace("@acme/auth", "@Acme/auth"))
    with pytest.raises(ManifestError, match="name must be"):
        package(root)


def test_package_refuses_a_declared_directory(tmp_path):
    root = project(tmp_path, MANIFEST.replace('["src/auth.py"]', '["src"]'))
    with pytest.raises(PackageError, match="src is not a regular file"):
        package(root)


def test_package_refuses_a_declared_file_through_a_symlinked_directory(tmp_path):
    root = project(tmp_path / "module", MANIFEST.replace("src/auth.py", "linked/secret.txt"))
    (tmp_path / "secret.txt").write_text("private\n", encoding="utf-8")
    (root / "src/auth.py").unlink()
    (root / "linked").symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(PackageError, match="linked/secret.txt is not a regular file"):
        package(root)
