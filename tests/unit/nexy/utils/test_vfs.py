"""The virtual file system of compiled files: memory first, disk behind it, one shared instance."""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.helpers.fs.vfs import VFS


@pytest.fixture
def vfs(tmp_path, monkeypatch):
    """The singleton, emptied, with the disk of a temporary project behind it."""
    monkeypatch.chdir(tmp_path)
    instance = VFS()
    saved = VFS.is_dev_mode()
    instance.clear()
    VFS.set_dev_mode(False)
    yield instance
    instance.clear()
    VFS.set_dev_mode(saved)


def test_there_is_one_instance():
    assert VFS() is VFS()


def test_the_files_belong_to_the_instance_not_the_class():
    assert "_files" not in vars(VFS) and "_disk_files" not in vars(VFS)


def test_written_content_is_read_back(vfs):
    vfs.write("__nexy__/a.py", "x = 1")
    assert vfs.read("__nexy__/a.py") == "x = 1"


def test_backslashes_are_the_same_path_as_slashes(vfs):
    vfs.write("__nexy__\\sub\\a.py", "x = 1")
    assert vfs.read("__nexy__/sub/a.py") == "x = 1"


def test_reading_a_missing_file_is_an_error(vfs):
    with pytest.raises(FileNotFoundError):
        vfs.read("__nexy__/none.py")


def test_a_file_is_persisted_under_the_nexy_folder(vfs, tmp_path):
    vfs.write("__nexy__/a.py", "x = 1")
    assert (tmp_path / "__nexy__" / "a.py").read_text(encoding="utf-8") == "x = 1"


def test_a_file_outside_the_nexy_folder_stays_in_memory(vfs, tmp_path):
    vfs.write("elsewhere/a.py", "x = 1")
    assert not (tmp_path / "elsewhere").exists() and vfs.read("elsewhere/a.py") == "x = 1"


def test_development_mode_never_writes_to_disk(vfs, tmp_path):
    VFS.set_dev_mode(True)
    vfs.write("__nexy__/a.py", "x = 1")
    assert not (tmp_path / "__nexy__").exists()


def test_a_file_on_disk_is_found_and_read_lazily(vfs, tmp_path):
    (tmp_path / "__nexy__").mkdir()
    (tmp_path / "__nexy__" / "b.py").write_text("y = 2", encoding="utf-8")
    assert vfs.exists("__nexy__/b.py") and vfs.read("__nexy__/b.py") == "y = 2"


def test_a_missing_file_does_not_exist(vfs):
    assert not vfs.exists("__nexy__/none.py")


def test_listing_has_memory_and_indexed_files(vfs):
    vfs.write("__nexy__/a.py", "")
    vfs.write("memory/b.py", "")
    assert set(vfs.list_files()) == {"__nexy__/a.py", "memory/b.py"}


def test_deleting_removes_memory_and_disk(vfs, tmp_path):
    vfs.write("__nexy__/a.py", "x = 1")
    vfs.delete("__nexy__/a.py")
    assert not vfs.exists("__nexy__/a.py") and not (tmp_path / "__nexy__" / "a.py").exists()


def test_deleting_an_unknown_file_is_harmless(vfs):
    vfs.delete("__nexy__/none.py")


def test_clearing_keeps_the_disk_unless_asked(vfs, tmp_path):
    vfs.write("__nexy__/a.py", "x = 1")
    vfs.clear()
    assert (tmp_path / "__nexy__" / "a.py").exists()


def test_clearing_the_disk_removes_the_folder(vfs, tmp_path):
    vfs.write("__nexy__/a.py", "x = 1")
    vfs.clear(clear_disk=True)
    assert not (tmp_path / "__nexy__").exists()


def test_flushing_writes_what_was_only_in_memory(vfs, tmp_path):
    VFS.set_dev_mode(True)
    vfs.write("__nexy__/a.py", "x = 1")
    VFS.set_dev_mode(False)
    vfs.flush_to_disk()
    assert Path(tmp_path / "__nexy__" / "a.py").read_text(encoding="utf-8") == "x = 1"
