"""What the dev server does for each change: recompile, refresh the browser, reload Python."""

from __future__ import annotations

import os
import time
from collections.abc import Callable, Iterable
from typing import Any

from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.helpers.common.pycheck import find_syntax_problem, report
from nexy.modules.cli.devtools.watch import notify
from nexy.modules.cli.devtools.watch.changes import FileChange
from nexy.modules.cli.devtools.watch.paths import (
    is_directory_of_pages,
    is_route_page,
    needs_restart,
)
from nexy.modules.i18n import t

_SYMBOLS = {"created": ("+", "green"), "deleted": ("-", "red")}


class ChangeReactor:
    """Applies the changes of one batch, one file at a time."""

    def __init__(
        self,
        compiler: Any,
        on_reload_api: Callable[[], None] | None = None,
        on_routes_changed: Callable[[str], None] | None = None,
    ) -> None:
        self.compiler = compiler
        self.on_reload_api = on_reload_api
        self.on_routes_changed = on_routes_changed
        self._restart_requested = False

    def react_all(self, changes: Iterable[FileChange]) -> None:
        """Apply a batch; the server is restarted at most once for all of it."""
        self._restart_requested = False
        for change in changes:
            self.react(change)

    def react(self, change: FileChange) -> None:
        if is_directory_of_pages(change.path):
            if change.kind != "modified":
                self._routes_changed(change.path, change.kind)
        elif change.kind == "deleted":
            self._deleted(change.path)
        elif change.kind == "created" and is_route_page(change.path):
            self._routes_changed(change.path, "created")
        else:
            self._edited(change.path)

    def _routes_changed(self, path: str, kind: str) -> None:
        """Tell the dev server that the set of routes changed, and say so."""
        symbol, colour = _SYMBOLS.get(kind, ("~", "yellow"))
        console.print(f"  [{colour}]{symbol}[/{colour}] [dim]{path}[/dim]")
        if self.on_routes_changed:
            self.on_routes_changed(path)

    def _deleted(self, path: str) -> None:
        if is_route_page(path):
            self._routes_changed(path, "deleted")
        elif needs_restart(path):
            self._refresh(path)

    def _edited(self, path: str) -> None:
        """A page is recompiled first; a failure is reported and nothing else happens."""
        if not os.path.exists(path):
            return
        started = time.perf_counter()
        if path.endswith(notify.PAGE_SUFFIXES) and not self._compile(path):
            return
        self._refresh(path, started)

    def _compile(self, path: str) -> bool:
        try:
            notify.compile_page(self.compiler, path)
        except Exception as error:
            notify.report_compile_error(path, error)
            return False
        return True

    def _refresh(self, path: str, started: float | None = None) -> None:
        if path.endswith((".nexy", ".md")):
            notify.broadcast_reload(path, started)
        elif self.on_reload_api and path.endswith(".py"):
            self._reload_python(path, self.on_reload_api)

    def _reload_python(self, path: str, reload_api: Callable[[], None]) -> None:
        """Restart the server for *path* unless it does not parse: then keep the running one."""
        problem = find_syntax_problem(path)
        if problem is not None:
            kept = t(
                "watch.error_kept",
                "Fix it and save: the server keeps its last working version.",
            )
            report(problem, kept)
            return
        if self._restart_requested:
            return
        self._restart_requested = True
        console.print(tagged("nexy", f"{t('watch.update', 'update')} [dim]{path}[/dim]"))
        try:
            reload_api()
        except Exception as error:
            reason = t("watch.restart_failed", "Failed to restart the server: {error}")
            console.print(tagged("hmr", f"[red]{reason.format(error=error)}[/red]", "red"))
