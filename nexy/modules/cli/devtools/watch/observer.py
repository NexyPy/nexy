"""The file watcher of `nx dev`: a thread that turns each batch of changes into reactions."""

from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import PurePath
from typing import Any

from watchfiles import Change, watch

from nexy.modules.cli.devtools.watch.changes import classify
from nexy.modules.cli.devtools.watch.paths import (
    is_directory_of_pages,
    is_generated_init,
    is_ignored_path,
    is_stray_markdown,
    normalize_path,
)
from nexy.modules.cli.devtools.watch.reactor import ChangeReactor
from nexy.modules.compiler import Compiler

# A save is often several writes: wait this long (ms) after the last one, at most DEBOUNCE.
STEP_MS = 50
DEBOUNCE_MS = 300


def make_filter(patterns: list[str]) -> Callable[[Change, str], bool]:
    """The `watch_filter` of a project: its extensions, minus what a rebuild must never see."""

    def accept(_change: Change, raw: str) -> bool:
        path = normalize_path(raw)
        if is_ignored_path(path) or is_generated_init(path) or is_stray_markdown(path):
            return False
        return is_directory_of_pages(path) or any(PurePath(path).match(p) for p in patterns)

    return accept


class ProjectWatcher:
    """Watches *root* on its own thread until `stop()`."""

    def __init__(self, root: str, accept: Callable[[Change, str], bool], reactor: ChangeReactor):
        self._root = root
        self._accept = accept
        self._reactor = reactor
        self._stopped = threading.Event()
        self._thread = threading.Thread(target=self._run, name="nexy-watch", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stopped.set()
        self._thread.join(timeout=2)

    def _run(self) -> None:
        batches = watch(
            self._root,
            watch_filter=self._accept,
            step=STEP_MS,
            debounce=DEBOUNCE_MS,
            stop_event=self._stopped,
            raise_interrupt=False,
        )
        for batch in batches:
            self._reactor.react_all(classify(batch))


def create_observer(
    path: str,
    patterns: list[str],
    ignore_patterns: list[str],
    on_reload_api: Callable[[], None],
    on_routes_changed: Callable[[str], None] | None = None,
) -> ProjectWatcher:
    """Start watching *path*; `ignore_patterns` are already covered by `is_ignored_path`."""
    del ignore_patterns
    reactor = ChangeReactor(Compiler(), on_reload_api, on_routes_changed)
    watcher = ProjectWatcher(path, make_filter(patterns), reactor)
    watcher.start()
    return watcher


def stop_observer(observer: Any) -> None:
    """Stop the watcher and wait for its thread."""
    if observer:
        observer.stop()
