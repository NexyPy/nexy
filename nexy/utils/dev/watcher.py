import asyncio
import os
import sys
import time
from collections.abc import Callable
from typing import Any

from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

from nexy.compiler import Compiler
from nexy.core.config import Config
from nexy.core.string import StringTransform
from nexy.runtime.hmr import HMR_MANAGER
from nexy.utils.common.console import console


def normalize_path(p: str | bytes) -> str:
    """POSIX-style path relative to the current working directory."""
    s = (p.decode() if isinstance(p, bytes) else p).replace("\\", "/")
    try:
        from pathlib import Path as _Path

        cwd = _Path.cwd().as_posix()
        if s.startswith(cwd):
            s = s[len(cwd) + 1 :]
    except Exception:
        pass
    return s.lstrip("./")


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
    return any(seg in path for seg in ignored)


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
        self.compiler = Compiler()

    def _should_trigger(self, path: str) -> bool:
        current_time = time.time()
        if path == self._last_path and (current_time - self._last_event_time) < self._min_interval:
            return False
        self._last_event_time = current_time
        self._last_path = path
        return True

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
        if throttle and not self._should_trigger(path):
            return
        if is_ignored_path(path):
            return

        event_start = time.perf_counter()

        if path.endswith((".nexy", ".mdx", ".md")):
            try:
                self._compile_and_log(path)
            except Exception as e:
                self._broadcast_compile_error(path, e)
                return

        self._trigger_reload(path, event_start)

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


def stop_observer(observer: Observer | None) -> None:
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
):
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
