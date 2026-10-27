"""The file watcher: what it accepts, and that a real change reaches the reactor."""

from __future__ import annotations

import time

import pytest
from watchfiles import Change

from nexy.core.config import Config
from nexy.modules.cli.devtools.watch.observer import create_observer, make_filter, stop_observer

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


def test_a_save_that_writes_twice_restarts_once(tmp_path):
    hits: list[bool] = []
    observer = create_observer(
        path=str(tmp_path),
        patterns=Config.WATCH_EXTENSIONS_GLOB,
        ignore_patterns=[],
        on_reload_api=lambda: hits.append(True),
    )
    try:
        time.sleep(0.3)
        target = tmp_path / "api.py"
        for text in ("a = 1\n", "a = 2\n", "a = 3\n"):
            target.write_text(text, encoding="utf-8")
            time.sleep(0.02)
        assert _wait_for(lambda: bool(hits))
        time.sleep(0.6)
    finally:
        stop_observer(observer)
    assert len(hits) == 1


def test_stopping_twice_is_harmless(tmp_path):
    observer = create_observer(str(tmp_path), PATTERNS, [], lambda: None)
    stop_observer(observer)
    stop_observer(observer)


def test_stopping_nothing_is_harmless():
    stop_observer(None)
