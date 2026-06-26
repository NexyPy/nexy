import os
import tempfile
from pathlib import Path

from nexy.utils.fs.vfs import VFS


def setup_function() -> None:
    VFS().clear()


def test_vfs_dev_mode_prevents_flush() -> None:
    vfs = VFS()
    vfs.write("__nexy__/test.txt", "hello")
    vfs.set_dev_mode(True)
    vfs.flush_to_disk()
    target = Path("__nexy__/test.txt")
    assert not target.exists()


def test_vfs_dev_mode_off_allows_flush() -> None:
    vfs = VFS()
    vfs.write("__nexy__/test.txt", "hello")
    vfs.set_dev_mode(False)
    with tempfile.TemporaryDirectory() as tmp:
        orig = Path.cwd()
        try:
            os.chdir(tmp)
            vfs.flush_to_disk()
            target = Path(tmp) / "__nexy__" / "test.txt"
            assert target.read_text(encoding="utf-8") == "hello"
        finally:
            os.chdir(str(orig))


def test_vfs_set_dev_mode_default_is_false() -> None:
    vfs = VFS()
    assert not vfs._dev_mode
