"""A release warns when a declared Python file imports a file it does not ship."""

from __future__ import annotations

from pathlib import Path

from nexy.modules.cli.publish.imports import undeclared_imports


def project(tmp_path: Path, source: str, code: str) -> Path:
    write(tmp_path, source, code)
    return tmp_path


def write(root: Path, source: str, code: str) -> None:
    path = root / source
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding="utf-8")


def test_undeclared_imports_flags_a_missing_relative_module(tmp_path):
    root = project(tmp_path, "src/auth.py", "from .helpers import token\n")
    assert undeclared_imports(root, ("src/auth.py",)) == ("src/helpers.py",)


def test_undeclared_imports_accepts_a_declared_module(tmp_path):
    root = project(tmp_path, "src/auth.py", "from .helpers import token\n")
    (root / "src/helpers.py").write_text("token = 1\n", encoding="utf-8")
    assert undeclared_imports(root, ("src/auth.py", "src/helpers.py")) == ()


def test_undeclared_imports_ignores_standard_library_imports(tmp_path):
    root = project(tmp_path, "src/auth.py", "import os\nfrom pathlib import Path\n")
    assert undeclared_imports(root, ("src/auth.py",)) == ()


def test_undeclared_imports_flags_a_missing_from_import(tmp_path):
    root = project(tmp_path, "src/auth.py", "from . import helpers, utils\n")
    assert undeclared_imports(root, ("src/auth.py",)) == ("src/helpers.py", "src/utils.py")


def test_undeclared_imports_accepts_a_declared_package_module(tmp_path):
    root = project(tmp_path, "pkg/auth.py", "from .helpers import token\n")
    write(root, "pkg/__init__.py", "")
    write(root, "pkg/helpers.py", "token = 1\n")
    declared = ("pkg/auth.py", "pkg/__init__.py", "pkg/helpers.py")
    assert undeclared_imports(root, declared) == ()


def test_undeclared_imports_flags_a_missing_package_module(tmp_path):
    root = project(tmp_path, "pkg/auth.py", "from .helpers import token\n")
    write(root, "pkg/__init__.py", "")
    assert undeclared_imports(root, ("pkg/auth.py", "pkg/__init__.py")) == ("pkg/helpers.py",)


def test_undeclared_imports_accepts_a_declared_package_directory(tmp_path):
    root = project(tmp_path, "pkg/auth.py", "from .helpers import token\n")
    write(root, "pkg/helpers/__init__.py", "")
    declared = ("pkg/auth.py", "pkg/helpers/__init__.py")
    assert undeclared_imports(root, declared) == ()


def test_undeclared_imports_resolves_a_parent_import(tmp_path):
    root = project(tmp_path, "pkg/sub/auth.py", "from ..shared import token\n")
    write(root, "pkg/shared.py", "token = 1\n")
    assert undeclared_imports(root, ("pkg/sub/auth.py",)) == ("pkg/shared.py",)


def test_undeclared_imports_ignores_an_import_above_the_module_root(tmp_path):
    root = project(tmp_path, "src/auth.py", "from ...shared import token\n")
    assert undeclared_imports(root, ("src/auth.py",)) == ()


def test_undeclared_imports_ignores_non_python_files(tmp_path):
    root = project(tmp_path, "notes.txt", "from .helpers import token\n")
    assert undeclared_imports(root, ("notes.txt",)) == ()


def test_undeclared_imports_ignores_unparseable_python(tmp_path):
    root = project(tmp_path, "src/auth.py", "from . helpers\n")
    assert undeclared_imports(root, ("src/auth.py",)) == ()
