"""A file watcher reports a batch; the dev server needs one verdict per file."""

from __future__ import annotations

from watchfiles import Change

from nexy.modules.cli.devtools.watch.changes import FileChange, classify


def _exists(*present: str):
    return lambda path: path in present


def test_a_file_that_appeared_is_created():
    batch = [(Change.added, "src/a.py")]
    assert classify(batch, _exists("src/a.py")) == [FileChange("created", "src/a.py")]


def test_a_file_that_changed_is_modified():
    batch = [(Change.modified, "src/a.py")]
    assert classify(batch, _exists("src/a.py")) == [FileChange("modified", "src/a.py")]


def test_a_file_that_is_gone_is_deleted():
    batch = [(Change.deleted, "src/a.py")]
    assert classify(batch, _exists()) == [FileChange("deleted", "src/a.py")]


def test_an_atomic_save_is_a_modification_not_a_creation():
    batch = [(Change.added, "src/a.py"), (Change.deleted, "src/a.py")]
    assert classify(batch, _exists("src/a.py")) == [FileChange("modified", "src/a.py")]


def test_a_file_created_and_removed_in_one_batch_is_deleted():
    batch = [(Change.added, "src/a.py"), (Change.deleted, "src/a.py")]
    assert classify(batch, _exists()) == [FileChange("deleted", "src/a.py")]


def test_a_rename_is_a_creation_and_a_deletion():
    batch = [(Change.added, "src/b.py"), (Change.deleted, "src/a.py")]
    kinds = {c.path: c.kind for c in classify(batch, _exists("src/b.py"))}
    assert kinds == {"src/b.py": "created", "src/a.py": "deleted"}


def test_the_changes_come_back_sorted_by_path():
    batch = [(Change.modified, "src/b.py"), (Change.modified, "src/a.py")]
    assert [c.path for c in classify(batch, _exists("src/a.py", "src/b.py"))] == [
        "src/a.py",
        "src/b.py",
    ]


def test_paths_are_made_relative_and_posix():
    batch = [(Change.modified, "src\\routes\\a.nexy")]
    assert classify(batch, _exists("src/routes/a.nexy"))[0].path == "src/routes/a.nexy"


def test_an_empty_batch_has_no_change():
    assert classify([], _exists()) == []
