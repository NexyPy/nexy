"""Dispatch-level tests: watchdog calls ``dispatch()``, which applies the
``patterns``/``ignore_patterns`` glob BEFORE any handler method runs.

The existing suite exercises ``on_modified()`` directly and therefore never
passes through that filter.
"""

import time

from watchdog.events import FileModifiedEvent

from nexy.core.config import Config
from nexy.utils.dev.watcher import WatchHandler, create_observer, stop_observer


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


def test_dispatch_fires_for_nexy_route() -> None:
    compiled: list[str] = []
    handler = _observer_handler(lambda: None)
    handler._compile_and_log = compiled.append

    handler.dispatch(_event("src/routes/index.nexy"))

    assert compiled == ["src/routes/index.nexy"]


def test_dispatch_fires_for_py_file() -> None:
    reloaded: list[bool] = []
    handler = _observer_handler(lambda: reloaded.append(True))

    handler.dispatch(_event("src/routes/api.py"))

    assert len(reloaded) == 1


def test_dispatch_fires_for_markdown_page() -> None:
    compiled: list[str] = []
    handler = _observer_handler(lambda: None)
    handler._compile_and_log = compiled.append

    handler.dispatch(_event("src/routes/blog/post.md"))

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
    """End-to-end: real watchdog Observer -> dispatch -> reload callback."""
    hits: list[bool] = []
    observer = create_observer(
        path=str(tmp_path),
        patterns=Config.WATCH_EXTENSIONS_GLOB,
        ignore_patterns=Config.WATCH_EXCLUDE_PATTERNS,
        on_reload_api=lambda: hits.append(True),
    )
    try:
        (tmp_path / "api.py").write_text("value = 1\n", encoding="utf-8")
        deadline = time.time() + 5
        while time.time() < deadline and not hits:
            time.sleep(0.05)
    finally:
        stop_observer(observer)

    assert len(hits) == 1
