"""The import hook that serves compiled modules from the VFS, tolerant of `-`/`_` and case."""

from __future__ import annotations

import pytest

from nexy.helpers.fs.vfs import VFS
from nexy.modules.runtime.importer import NexyVFSFinder, install_vfs_importer


@pytest.fixture
def finder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    vfs = VFS()
    saved = VFS.is_dev_mode()
    vfs.clear()
    VFS.set_dev_mode(True)
    yield NexyVFSFinder()
    vfs.clear()
    VFS.set_dev_mode(saved)


def _put(path: str) -> None:
    VFS().write(path, "")


def test_a_module_that_is_not_compiled_by_nexy_is_left_alone(finder):
    assert finder.find_spec("json", None) is None


def test_a_compiled_module_is_found(finder):
    _put("__nexy__/page.py")
    assert finder.find_spec("__nexy__.page", None) is not None


def test_a_dotted_module_is_a_path(finder):
    _put("__nexy__/src/routes/index.py")
    assert finder.find_spec("__nexy__.src.routes.index", None) is not None


def test_a_package_has_an_init_file(finder):
    _put("__nexy__/pkg/__init__.py")
    spec = finder.find_spec("__nexy__.pkg", None)
    assert spec is not None and spec.submodule_search_locations is not None


def test_a_missing_module_is_not_found(finder):
    assert finder.find_spec("__nexy__.ghost", None) is None


def test_an_underscore_may_stand_for_a_hyphen(finder):
    _put("__nexy__/my-page.py")
    assert finder.find_spec("__nexy__.my_page", None) is not None


def test_a_hyphen_may_stand_for_an_underscore(finder):
    _put("__nexy__/my_page.py")
    assert finder._find_vfs_path("__nexy__/my-page.py") == "__nexy__/my_page.py"


def test_a_lowercase_file_answers_for_a_mixed_case_name(finder):
    _put("__nexy__/page.py")
    assert finder.find_spec("__nexy__.Page", None) is not None


def test_the_importer_is_installed_once():
    import sys

    install_vfs_importer()
    install_vfs_importer()
    assert sum(isinstance(item, NexyVFSFinder) for item in sys.meta_path) == 1
