"""Small public files are kept in memory: no thread pool hop, no disk read once they are known."""

from __future__ import annotations

import os

from starlette.responses import FileResponse

from nexy.modules.routers.small_files import SmallFiles


def _file(tmp_path, content: bytes = b"hello"):
    path = tmp_path / "a.txt"
    path.write_bytes(content)
    return path


def test_a_small_file_is_read_once(tmp_path):
    path = _file(tmp_path)
    cache = SmallFiles()
    assert cache.get(path, path.stat()) is cache.get(path, path.stat())


def test_the_body_is_the_file(tmp_path):
    path = _file(tmp_path)
    assert SmallFiles().get(path, path.stat()).body == b"hello"


def test_the_headers_are_those_of_a_file_response(tmp_path):
    path = _file(tmp_path)
    expected = FileResponse(path, stat_result=path.stat()).raw_headers
    assert SmallFiles().get(path, path.stat()).headers == expected


def test_a_changed_file_is_read_again(tmp_path):
    path = _file(tmp_path)
    cache = SmallFiles()
    cache.get(path, path.stat())
    path.write_bytes(b"changed")
    os.utime(path, ns=(1, 2_000_000_000))
    assert cache.get(path, path.stat()).body == b"changed"


def test_a_file_over_the_limit_is_not_kept(tmp_path):
    path = _file(tmp_path)
    assert SmallFiles(max_file=4).get(path, path.stat()) is None


def test_the_memory_kept_is_bounded(tmp_path):
    first, second = tmp_path / "a.txt", tmp_path / "b.txt"
    first.write_bytes(b"12345")
    second.write_bytes(b"67890")
    cache = SmallFiles(max_total=8)
    cache.get(first, first.stat())
    assert cache.get(second, second.stat()) is None
