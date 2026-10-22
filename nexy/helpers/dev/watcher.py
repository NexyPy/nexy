import asyncio
import os
import sys
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

from nexy.compiler import Compiler
from nexy.core.config import Config
from nexy.core.string import StringTransform
from nexy.helpers.common.console import console
from nexy.runtime.hmr import HMR_MANAGER


def normalize_path(p: str | bytes) -> str:
    """POSIX-style path relative to the current working directory."""
    s = (p.decode() if isinstance(p, bytes) else p).replace("\\", "/")
    try:
        from pathlib import Path as _Path

        cwd = _Path.cwd().as_posix()
        if s.startswith(cwd):
            s = s[len(cwd) + 1 :]
    except (OSError, ValueError):
        pass
    # Strip only the literal "./" prefix: lstrip("./") would also eat the
    # leading "/" of absolute paths outside cwd (e.g. pytest tmp_path on Linux)
    # and the leading dot of dotfiles, breaking os.path.exists downstream.
    return s.removeprefix("./")


def is_ignored_path(path: str) -> bool:
    """True for paths a rebuild should never react to."""
    ignored = (
        ".git/",
        "venv",
        "/venv",
        ".venv/",
        "/.venv",
        "__nexy__/",
        "/__nexy__",
        ".nexy-virt/",
        "/.nexy-virt",
        "__pycache__/",
        "node_modules/",
    )
    if any(seg in path for seg in ignored):
        return True
    # excludeDirs (docs, templates, ...) must be checked here: the watchdog
    # exclusion globs ("**/docs/**") do not match with PurePath.match, so the
    # watchdog-level ignore_patterns never filter root-level directories.
    posix = f"/{path}"
    return any(f"/{dir_name}/" in posix for dir_name in Config().excludeDirs)


def needs_restart(path: str) -> bool:
    """True for server-side files whose change requires a reload."""
    return path.endswith((".nexy", ".mdx", ".md", ".py")) and not is_ignored_path(path)


class WatchHandler(PatternMatchingEventHandler):
    def __init__(
        self,
        on_reload_api: Callable[[], None] | None = None,
        min_interval: float = 0.5,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.on_reload_api = on_reload_api
        self._last_event_time: float = 0.0
        self._last_path: str = ""
        self._min_interval = min_interval
        self._pending: dict[str, threading.Timer] = {}
        self._signatures: dict[str, tuple[int, int]] = {}
        self.compiler = Compiler()

    def _should_trigger(self, path: str) -> bool:
        current_time = time.time()
        if path == self._last_path and (current_time - self._last_event_time) < self._min_interval:
            return False
        self._mark_processed(path)
        return True

    def _mark_processed(self, path: str) -> None:
        """Records the throttle bookkeeping for a path (leading edge)."""
        self._last_event_time = time.time()
        self._last_path = path

    def _purge_route_modules(self, path: str) -> None:
        """Remove compiled route modules from sys.modules so the next request
        re-imports fresh code from the VFS (no server restart needed)."""
        if not path.endswith((".nexy", ".md", ".mdx")):
            return
        mapped = StringTransform.normalize_route_path_for_namespace(path)
        module_name = f"{Config.NAMESPACE}{mapped}".replace("/", ".").rsplit(".", 1)[0]
        for name in list(sys.modules):
            if name == module_name or name.startswith(module_name + "."):
                del sys.modules[name]

    def _compile_and_log(self, path: str) -> None:
        start = time.perf_counter()
        self.compiler.compile(path)
        self._purge_route_modules(path)
        elapsed = time.perf_counter() - start
        console.print(
            f"[green]nsc[/green] » [green]compile[/green]"
            f" [dim]{path}[/dim] in [dim]{elapsed:.2f}s[/dim]"
        )

    def _broadcast_compile_error(self, path: str, error: Exception) -> None:
        console.print(f"[red]nsc[/red] » [red]error[/red] while compiling [dim]{path}[/dim]")
        console.print(f"[red]│[/red] [bold]{type(error).__name__}:[/bold] {str(error)}")
        if HMR_MANAGER.loop:
            asyncio.run_coroutine_threadsafe(
                HMR_MANAGER.broadcast_error(
                    [{"file": path, "message": f"{type(error).__name__}: {error}"}]
                ),
                HMR_MANAGER.loop,
            )

    def _trigger_reload(self, path: str, start_time: float | None = None) -> None:
        if path.endswith((".nexy", ".md")):
            if HMR_MANAGER.loop:
                asyncio.run_coroutine_threadsafe(
                    HMR_MANAGER.broadcast_reload(path), HMR_MANAGER.loop
                )
                self._log_hmr_timing(path, start_time)
        elif self.on_reload_api and path.endswith(".py"):
            try:
                self.on_reload_api()
            except Exception as e:
                console.print(
                    f"[red]hmr[/red] » [red]error[/red] failed to restart server: {str(e)}"
                )

    def _log_hmr_timing(self, path: str, start_time: float | None) -> None:
        if start_time is None:
            return
        if os.getenv("NEXY_HMR_DEBUG", "").strip() not in ("1", "true", "TRUE"):
            return
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        console.print(
            f"[green]nsc[/green] » [green]hmr[/green]"
            f" [dim]{path}[/dim] → broadcast in [dim]{elapsed_ms:.1f}ms[/dim]"
        )

    def on_modified(self, event: FileSystemEvent) -> None:
        self._handle_event(event, throttle=True)

    def on_created(self, event: FileSystemEvent) -> None:
        self._handle_event(event, throttle=False)

    def _handle_event(self, event: FileSystemEvent, throttle: bool) -> None:
        """Compile server pages and bounce HMR after one filesystem change."""
        if event.is_directory:
            return
        path = normalize_path(event.src_path)
        if is_ignored_path(path):
            return
        if throttle and not self._should_trigger(path):
            # Save bursts (truncate + write on Windows) hit the leading edge
            # mid-save: re-process once the path has gone quiet, but only if
            # the content actually changed since the leading edge.
            self._schedule_trailing(path)
            return
        if not throttle:
            # on_created bypasses the throttle: record it so the modified
            # events of the same save burst do not process a second time.
            self._mark_processed(path)
        self._process_path(path)

    def _schedule_trailing(self, path: str) -> None:
        timer = self._pending.pop(path, None)
        if timer is not None:
            timer.cancel()
        timer = threading.Timer(self._min_interval, self._run_trailing, args=(path,))
        timer.daemon = True
        self._pending[path] = timer
        timer.start()

    def _run_trailing(self, path: str) -> None:
        self._pending.pop(path, None)
        self._last_event_time = time.time()
        if not self._content_changed(path):
            # Same content as the leading edge: one save must produce exactly
            # one compile / reload / HMR broadcast.
            return
        self._process_path(path)

    def _process_path(self, path: str) -> None:
        if not os.path.exists(path):
            # Atomic saves briefly remove the file; a create/moved event follows.
            return
        event_start = time.perf_counter()
        if path.endswith((".nexy", ".mdx", ".md")):
            try:
                self._compile_and_log(path)
            except Exception as e:
                # Forget the signature so the trailing edge retries after a
                # transient mid-save parse error.
                self._signatures.pop(path, None)
                self._broadcast_compile_error(path, e)
                return
        sig = self._signature(path)
        if sig is not None:
            self._signatures[path] = sig
        self._trigger_reload(path, event_start)

    @staticmethod
    def _signature(path: str) -> tuple[int, int] | None:
        """Cheap content identity for a file: (mtime_ns, size)."""
        try:
            st = os.stat(path)
        except OSError:
            return None
        return (st.st_mtime_ns, st.st_size)

    def _content_changed(self, path: str) -> bool:
        sig = self._signature(path)
        if sig is None:
            return False
        return self._signatures.get(path) != sig

    def cancel_trailing(self) -> None:
        """Cancel scheduled trailing reprocessing (used on shutdown)."""
        for timer in self._pending.values():
            timer.cancel()
        self._pending.clear()

    def on_deleted(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = normalize_path(event.src_path)
        if is_ignored_path(path):
            return
        if needs_restart(path):
            self._trigger_reload(path)

    def on_moved(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        src = normalize_path(event.src_path)
        dest = normalize_path(event.dest_path)

        src_event = FileSystemEvent(src)
        src_event.is_directory = False
        self.on_deleted(src_event)

        dest_event = FileSystemEvent(dest)
        dest_event.is_directory = False
        self.on_created(dest_event)


def purge_project_modules(root: Path | None = None) -> list[str]:
    """Drop project-local modules so the dev restart re-imports fresh code.

    Framework modules (``nexy`` / ``nexy.*``) and environment directories
    (``.venv``, ``site-packages``, ``node_modules``) are never dropped:
    re-importing them mid-run would leave already-imported modules holding a
    stale ``Config`` class.

    Args:
        root: Project root to purge from. Defaults to the current directory.

    Returns:
        The names removed from ``sys.modules``.
    """
    base = (root or Path.cwd()).resolve().as_posix()
    skip_markers = ("/.venv/", "/venv/", "/site-packages/", "/node_modules/")
    purged: list[str] = []
    for name, module in list(sys.modules.items()):
        if name == "nexy" or name.startswith(("nexy.", "__nexy__")):
            continue
        module_file = getattr(module, "__file__", None)
        if not module_file:
            continue
        file_posix = Path(module_file).resolve().as_posix()
        if not file_posix.startswith(base + "/"):
            continue
        if any(marker in file_posix for marker in skip_markers):
            continue
        del sys.modules[name]
        purged.append(name)
    return purged


def stop_observer(observer: Any) -> None:
    """Stop the watchdog observer cleanly and wait for its thread."""
    if not observer:
        return
    try:
        observer.stop()
        observer.join(timeout=2)
    except Exception as e:
        console.print(f"  [dim]Warning: Could not stop watcher cleanly: {e}[/dim]")


def create_observer(
    path: str,
    patterns: list[str],
    ignore_patterns: list[str],
    on_reload_api: Callable[[], None],
) -> Any:
    event_handler = WatchHandler(
        patterns=patterns,
        ignore_patterns=ignore_patterns,
        on_reload_api=on_reload_api,
        ignore_directories=True,
    )
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    return observer
