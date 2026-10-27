"""Searches that climb from a route's folder stop where they must."""

from __future__ import annotations

from pathlib import Path

from nexy.helpers.fs.ancestors import walk_up


def test_the_walk_starts_at_the_folder_and_ends_at_the_stop(tmp_path):
    start = tmp_path / "a" / "b"
    start.mkdir(parents=True)
    assert list(walk_up(start, tmp_path)) == [start, tmp_path / "a", tmp_path]


def test_the_stop_itself_is_a_walk_of_one(tmp_path):
    assert list(walk_up(tmp_path, tmp_path)) == [tmp_path]


def test_a_start_outside_the_stop_yields_nothing(tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    inside = tmp_path / "inside"
    inside.mkdir()
    assert list(walk_up(other, inside)) == []


def test_a_sibling_with_a_longer_name_is_not_inside(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src2").mkdir()
    assert list(walk_up(tmp_path / "src2", tmp_path / "src")) == []


def test_the_walk_ends_at_the_filesystem_root():
    root = Path(Path.cwd().anchor)
    assert list(walk_up(Path.cwd(), root))[-1] == root
