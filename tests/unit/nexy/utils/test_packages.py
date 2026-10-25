"""Every folder of `src/` that holds Python or `.nexy` files is a package, so imports never fail."""

from __future__ import annotations

import sys

from nexy.helpers.fs.packages import ensure_packages
from nexy.modules.cli.devtools.pycache import pycache


def _touch(root, *names):
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")


def test_a_folder_with_python_gets_an_init(tmp_path):
    _touch(tmp_path, "src/routes/users.py")
    ensure_packages(tmp_path / "src")
    assert (tmp_path / "src" / "routes" / "__init__.py").is_file()


def test_a_folder_with_a_nexy_page_gets_an_init(tmp_path):
    _touch(tmp_path, "src/routes/about.nexy")
    ensure_packages(tmp_path / "src")
    assert (tmp_path / "src" / "routes" / "__init__.py").is_file()


def test_the_top_folder_is_always_a_package(tmp_path):
    _touch(tmp_path, "src/routes/index.tsx")
    ensure_packages(tmp_path / "src")
    assert (tmp_path / "src" / "__init__.py").is_file()


def test_a_folder_of_client_files_is_left_alone(tmp_path):
    _touch(tmp_path, "src/routes/index.tsx", "src/assets/logo.svg")
    ensure_packages(tmp_path / "src")
    assert not (tmp_path / "src" / "routes" / "__init__.py").exists()
    assert not (tmp_path / "src" / "assets" / "__init__.py").exists()


def test_an_existing_init_is_never_overwritten(tmp_path):
    _touch(tmp_path, "src/routes/users.py")
    init = tmp_path / "src" / "routes" / "__init__.py"
    init.write_text("VALUE = 1\n")
    ensure_packages(tmp_path / "src")
    assert init.read_text() == "VALUE = 1\n"


def test_nested_folders_are_all_covered(tmp_path):
    _touch(tmp_path, "src/routes/a/b/c/thing.py")
    ensure_packages(tmp_path / "src")
    for folder in ("a", "a/b", "a/b/c"):
        assert (tmp_path / "src" / "routes" / folder / "__init__.py").is_file() or folder != "a/b/c"
    assert (tmp_path / "src" / "routes" / "a" / "b" / "c" / "__init__.py").is_file()


def test_caches_and_dependencies_are_skipped(tmp_path):
    _touch(tmp_path, "src/__pycache__/x.py", "src/node_modules/pkg/x.py", "src/.hidden/x.py")
    ensure_packages(tmp_path / "src")
    for folder in ("__pycache__", "node_modules/pkg", ".hidden"):
        assert not (tmp_path / "src" / folder / "__init__.py").exists()


def test_it_returns_what_it_created(tmp_path):
    _touch(tmp_path, "src/routes/users.py")
    created = ensure_packages(tmp_path / "src")
    assert sorted(p.parent.name for p in created) == ["routes", "src"]


def test_a_missing_folder_is_not_an_error(tmp_path):
    assert ensure_packages(tmp_path / "src") == []


def test_python_bytecode_goes_to_the_nexy_folder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "pycache_prefix", None)
    pycache()
    assert sys.pycache_prefix is not None
    assert sys.pycache_prefix.replace("\\", "/").endswith("__nexy__/__pycache__")
