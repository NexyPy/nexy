"""The file watcher: what it accepts, and that a real change reaches the reactor."""

from __future__ import annotations

import time

import pytest
from watchfiles import Change

from nexy.core.config import Config
from nexy.modules.cli.devtools.watch.changes import classify
from nexy.modules.cli.devtools.watch.observer import create_observer, make_filter, stop_observer
from nexy.modules.cli.devtools.watch.reactor import ChangeReactor
from nexy.modules.compiler import Compiler

PATTERNS = ["*.py", "*.nexy", "*.md"]


@pytest.fixture
def accept():
    return make_filter(PATTERNS)


class TestFilter:
    @pytest.mark.parametrize("path", ["src/routes/a.py", "src/routes/a.nexy", "src/routes/p.md"])
    def test_a_source_file_is_accepted(self, accept, path):
        assert accept(Change.modified, path)

    @pytest.mark.parametrize(
        "path",
        ["src/a.txt", "node_modules/x/a.py", ".venv/lib/a.py", "__nexy__/a.py", "README.md"],
    )
    def test_other_files_are_not(self, accept, path):
        assert not accept(Change.modified, path)

    def test_a_folder_of_pages_is_accepted(self, accept):
        assert accept(Change.deleted, "src/routes/blog")

    def test_a_folder_elsewhere_is_not(self, accept):
        assert not accept(Change.deleted, "src/components/ui")

    def test_an_empty_init_file_is_not_a_change(self, accept, tmp_path):
        init = tmp_path / "__init__.py"
        init.write_text("")
        assert not accept(Change.added, str(init))


def _wait_for(condition, seconds: float = 5.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if condition():
            return True
        time.sleep(0.05)
    return False


def test_a_real_file_change_reaches_the_reload_callback(tmp_path):
    hits: list[bool] = []
    observer = create_observer(
        path=str(tmp_path),
        patterns=Config.WATCH_EXTENSIONS_GLOB,
        ignore_patterns=Config.WATCH_EXCLUDE_PATTERNS,
        on_reload_api=lambda: hits.append(True),
    )
    try:
        time.sleep(0.3)
        (tmp_path / "api.py").write_text("value = 1\n", encoding="utf-8")
        assert _wait_for(lambda: bool(hits))
    finally:
        stop_observer(observer)


def test_one_batch_that_names_a_file_twice_restarts_once(tmp_path):
    """One save is one batch: the server restarts once however many writes it holds.

    The batch is handed to the reactor directly rather than produced by a real save. A real
    save is a burst of writes, and whether the watcher sees one batch or two depends on how
    long the machine takes between two `write` calls: the old version of this test failed
    with `assert 2 == 1` whenever a loaded CI runner stretched the burst past the quiet
    period. What belongs to Nexy is what it does with the batch, and that is what this asserts.
    """
    target = tmp_path / "api.py"
    target.write_text("a = 3\n", encoding="utf-8")
    hits: list[bool] = []
    reactor = ChangeReactor(Compiler(), lambda: hits.append(True))
    # An atomic save: the editor writes a temporary file over the old one, so one batch
    # carries an add, a delete and a modification of the same path.
    batch = {
        (Change.added, str(target)),
        (Change.deleted, str(target)),
        (Change.modified, str(target)),
    }
    reactor.react_all(classify(batch))
    assert hits == [True]


def test_two_batches_restart_twice(tmp_path):
    """Two saves, two batches: the guard is per batch, not for the lifetime of the watcher."""
    target = tmp_path / "api.py"
    target.write_text("a = 1\n", encoding="utf-8")
    hits: list[bool] = []
    reactor = ChangeReactor(Compiler(), lambda: hits.append(True))
    reactor.react_all(classify({(Change.modified, str(target))}))
    target.write_text("a = 2\n", encoding="utf-8")
    reactor.react_all(classify({(Change.modified, str(target))}))
    assert hits == [True, True]


def test_stopping_twice_is_harmless(tmp_path):
    observer = create_observer(str(tmp_path), PATTERNS, [], lambda: None)
    stop_observer(observer)
    stop_observer(observer)


def test_stopping_nothing_is_harmless():
    stop_observer(None)
