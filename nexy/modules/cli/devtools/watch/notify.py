"""What the dev server tells the developer and the browser after a page changed."""

from __future__ import annotations

import asyncio
import os
import sys
import time
from typing import Any

from rich.markup import escape

from nexy.core.config import Config
from nexy.core.string import StringTransform
from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.helpers.server.access_log import format_duration
from nexy.modules.i18n import t
from nexy.modules.runtime.hmr import HMR_MANAGER

PAGE_SUFFIXES = (".nexy", ".mdx", ".md")


def forget_compiled_page(path: str) -> None:
    """Drop a page's compiled module so the next request imports the fresh one."""
    if not path.endswith(PAGE_SUFFIXES):
        return
    mapped = StringTransform.normalize_route_path_for_namespace(path)
    module = f"{Config.NAMESPACE}{mapped}".replace("/", ".").rsplit(".", 1)[0]
    for name in list(sys.modules):
        if name == module or name.startswith(module + "."):
            del sys.modules[name]


def compile_page(compiler: Any, path: str) -> None:
    """Compile a page, say how long it took, and make the next request use the result."""
    started = time.perf_counter()
    compiler.compile(path)
    forget_compiled_page(path)
    took = format_duration(time.perf_counter() - started)
    done = t("watch.compiled", "Compiled {path} in {time}")
    line = done.format(path=f"[dim]{path}[/dim]", time=f"[dim]{took}[/dim]")
    console.print(f"  [green]✓[/green] {line}")


def _run_on_hmr_loop(coroutine: Any) -> None:
    asyncio.run_coroutine_threadsafe(coroutine, HMR_MANAGER.loop)  # type: ignore[arg-type]


def broadcast_reload(path: str, started: float | None = None) -> None:
    """Ask the open browser pages to refresh *path*; nothing happens with no page open."""
    if not HMR_MANAGER.loop:
        return
    _run_on_hmr_loop(HMR_MANAGER.broadcast_reload(path))
    _log_hmr_timing(path, started)


def _log_hmr_timing(path: str, started: float | None) -> None:
    if started is None or os.getenv("NEXY_HMR_DEBUG", "").strip() not in ("1", "true", "TRUE"):
        return
    took = f"[dim]{(time.perf_counter() - started) * 1000:.1f}ms[/dim]"
    message = f"[green]hmr[/green] [dim]{path}[/dim] → broadcast in {took}"
    console.print(tagged("nsc", message, "green"))


def report_compile_error(path: str, error: Exception) -> None:
    """Print a compile error and send it to the browser overlay."""
    failed = t("watch.compile_failed", "Failed to compile {path}")
    console.print(f"  [red]x[/red] {failed.format(path=f'[dim]{path}[/dim]')}")
    console.print(f"    [bold]{type(error).__name__}:[/bold] {escape(str(error))}")
    if HMR_MANAGER.loop:
        _run_on_hmr_loop(HMR_MANAGER.broadcast_error([_overlay_entry(path, error)]))


def _overlay_entry(path: str, error: Exception) -> dict[str, Any]:
    hint = getattr(error, "hint", None)
    message = str(error)
    if hint:
        # __str__ already appends the hint; the overlay renders it once.
        message = message.removesuffix(f"\n  Fix: {hint}")
    return {"file": path, "message": f"{type(error).__name__}: {message}", "hint": hint}
