"""Dispatch-level tests: watchdog calls ``dispatch()``, which applies the
``patterns``/``ignore_patterns`` glob BEFORE any handler method runs.

The existing suite exercises ``on_modified()`` directly and therefore never
passes through that filter.
"""

import time

from watchdog.events import FileModifiedEvent

from nexy.core.config import Config
from nexy.modules.cli.devtools.watcher import WatchHandler, create_observer, stop_observer


def _event(path: str) -> FileModifiedEvent:
    event = FileModifiedEvent(path)
    event.is_directory = False
    return event


def _observer_handler(on_reload_api) -> WatchHandler:
    """Builds the handler exactly as ``create_observer()`` does."""
    return WatchHandler(
        patterns=Config.WATCH_EXTENSIONS_GLOB,
        ignore_patterns=Config.WATCH_EXCLUDE_PATTERNS,
        on_reload_api=on_reload_api,
        ignore_directories=True,
    )


def _touch(tmp_path, rel: str, content: str = "# page") -> str:
    """Creates the file on disk and returns the relative POSIX path.

    ``_process_path`` skips files that do not exist (atomic-save window), so
    dispatch-level tests must use real files.
    """
    file = tmp_path / rel
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content, encoding="utf-8")
    return file.relative_to(tmp_path).as_posix()


def test_dispatch_fires_for_nexy_route(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    rel = _touch(tmp_path, "src/routes/index.nexy")
    compiled: list[str] = []
    handler = _observer_handler(lambda: None)
    handler._compile_and_log = compiled.append

    handler.dispatch(_event(rel))

    assert compiled == ["src/routes/index.nexy"]


def test_dispatch_fires_for_py_file(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    rel = _touch(tmp_path, "src/routes/api.py", "print('hello')")
    reloaded: list[bool] = []
    handler = _observer_handler(lambda: reloaded.append(True))

    handler.dispatch(_event(rel))

    assert len(reloaded) == 1


def test_dispatch_fires_for_markdown_page(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    rel = _touch(tmp_path, "src/routes/blog/post.md")
    compiled: list[str] = []
    handler = _observer_handler(lambda: None)
    handler._compile_and_log = compiled.append

    handler.dispatch(_event(rel))

    assert compiled == ["src/routes/blog/post.md"]


def test_dispatch_ignores_excluded_dir() -> None:
    compiled: list[str] = []
    reloaded: list[bool] = []
    handler = _observer_handler(lambda: reloaded.append(True))
    handler._compile_and_log = compiled.append

    handler.dispatch(_event("docs/page.md"))

    assert compiled == []
    assert reloaded == []


def test_dispatch_ignores_venv_file() -> None:
    reloaded: list[bool] = []
    handler = _observer_handler(lambda: reloaded.append(True))

    handler.dispatch(_event(".venv/lib/site-packages/pkg/mod.py"))

    assert reloaded == []


def test_create_observer_delivers_real_file_change(tmp_path) -> None:
    """End-to-end: real watchdog Observer -> dispatch -> reload callback.

    The contract under test is delivery: a real filesystem change observed by
    a real watchdog Observer reaches the reload callback at least once, even
    when the watched path lies outside the current working directory.
    Collapse-to-once dedup is asserted deterministically in test_watcher.py
    (TestEdgeCases); asserting it here would depend on observer-thread timing.
    """
    hits: list[bool] = []
    observer = create_observer(
        path=str(tmp_path),
        patterns=Config.WATCH_EXTENSIONS_GLOB,
        ignore_patterns=Config.WATCH_EXCLUDE_PATTERNS,
        on_reload_api=lambda: hits.append(True),
    )
    try:
        (tmp_path / "api.py").write_text("value = 1\n", encoding="utf-8")
        # Wait past the debounce window so a trailing double-fire would show up.
        debounce = WatchHandler()._min_interval
        deadline = time.time() + debounce + 2
        while time.time() < deadline and not hits:
            time.sleep(0.05)
        settle_until = time.time() + debounce
        while time.time() < settle_until:
            time.sleep(0.05)
    finally:
        stop_observer(observer)

    assert len(hits) >= 1
