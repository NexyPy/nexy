import time
from collections.abc import Callable
from typing import Any

from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

from nexy.compiler import Compiler
from nexy.utils.common.console import console


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

    def _normalize(self, p: str | bytes) -> str:
        s = (p.decode() if isinstance(p, bytes) else p).replace("\\", "/")
        try:
            from pathlib import Path as _Path
            cwd = _Path.cwd().as_posix()
            if s.startswith(cwd):
                s = s[len(cwd) + 1:]
        except Exception:
            pass
        return s.lstrip("./")

    def _skip(self, path: str) -> bool:
        ignored = (".git/", "venv", "/venv", ".venv/", "/.venv", "__nexy__/", "/__nexy__", "__pycache__/", "node_modules/")
        return any(seg in path for seg in ignored)

    def _compile_and_log(self, path: str) -> None:
        start = time.perf_counter()
        self.compiler.compile(path)
        elapsed = time.perf_counter() - start
        console.print(
            f"[green]nsc[/green] » [green]compile[/green]"
            f" [dim]{path}[/dim] in [dim]{elapsed:.2f}s[/dim]"
        )

    def _needs_restart(self, path: str) -> bool:
        return path.endswith((".nexy", ".mdx", ".py")) and not self._skip(path)

    def _trigger_reload(self, path: str) -> None:
        if self.on_reload_api:
            try:
                self.on_reload_api()
            except Exception as e:
                console.print(f"[red]hmr[/red] » [red]error[/red] failed to restart server: {str(e)}")

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = self._normalize(event.src_path)
        if not self._should_trigger(path) or self._skip(path):
            return

        if path.endswith((".nexy", ".mdx")):
            try:
                self._compile_and_log(path)
            except Exception as e:
                console.print(
                    f"[red]nsc[/red] » [red]error[/red] while compiling [dim]{path}[/dim]"
                )
                console.print(f"[red]│[/red] [bold]{type(e).__name__}:[/bold] {str(e)}")
                return

        self._trigger_reload(path)

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = self._normalize(event.src_path)
        if self._skip(path):
            return

        if path.endswith((".nexy", ".mdx")):
            try:
                self._compile_and_log(path)
            except Exception as e:
                console.print(
                    f"[red]nsc[/red] » [red]error[/red] while creating [dim]{path}[/dim]"
                )
                console.print(f"[red]│[/red] [bold]{type(e).__name__}:[/bold] {str(e)}")
                return

        self._trigger_reload(path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = self._normalize(event.src_path)
        if self._skip(path):
            return
        if self._needs_restart(path):
            self._trigger_reload(path)

    def on_moved(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        src = self._normalize(event.src_path)
        dest = self._normalize(event.dest_path)

        src_event = FileSystemEvent(src)
        src_event.is_directory = False
        self.on_deleted(src_event)

        dest_event = FileSystemEvent(dest)
        dest_event.is_directory = False
        self.on_created(dest_event)


def create_observer(
    path: str, patterns: list[str], ignore_patterns: list[str], on_reload_api: Callable[[], None]
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
