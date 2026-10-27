"""Compiles every route file of the project, in parallel, skipping the ones that did not change."""

from __future__ import annotations

import os
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from nexy.core.config import Config
from nexy.errors import NexyCompileError
from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.helpers.fs.vfs import VFS
from nexy.modules.builder.cache import BuildCache
from nexy.modules.builder.discovery import Discovery
from nexy.modules.builder.fingerprints import (
    _layout_chain_cache,
    config_fingerprint,
    file_fingerprint,
    layout_chain_fingerprint,
)
from nexy.modules.builder.model import BuildError, BuildResult
from nexy.modules.compiler import Compiler

_THREAD_LOCAL = threading.local()

# The name the tests of the layout fingerprint cache import.
_get_layout_chain = layout_chain_fingerprint


@dataclass(frozen=True)
class Outcome:
    """What happened to one file: compiled (no error), skipped as unchanged, or failed."""

    path: str
    error: BuildError | None = None
    skipped: bool = False


def _thread_compiler() -> Compiler:
    """A compiler per thread, to avoid constructing one per file."""
    compiler = getattr(_THREAD_LOCAL, "compiler", None)
    if compiler is None:
        compiler = _THREAD_LOCAL.compiler = Compiler()
    return compiler


def _error_of(path: str, failure: Exception) -> BuildError:
    if isinstance(failure, NexyCompileError):
        return BuildError(
            path=failure.source_path,
            message=failure.message,
            line=failure.line,
            column=failure.column,
            type="NexyCompileError",
            hint=failure.hint,
        )
    return BuildError(path=path, message=str(failure), type=type(failure).__name__)


def _compile(file: Path, cache: BuildCache, incremental: bool) -> Outcome:
    path = file.resolve().relative_to(Path.cwd()).as_posix()
    fingerprint = file_fingerprint(file)
    if incremental and cache.is_current(path, fingerprint):
        return Outcome(path, skipped=True)
    try:
        _thread_compiler().compile_with_deps(input=path)
    except Exception as failure:
        return Outcome(path, error=_error_of(path, failure))
    cache.remember(path, fingerprint)
    return Outcome(path)


def _record(outcome: Outcome, result: BuildResult, showlog: bool) -> None:
    """Add an outcome to the result, and say what happened to the file."""
    if outcome.skipped:
        result.skipped.append(outcome.path)
        if showlog:
            console.print(tagged("nsc", f"cached [dim]{outcome.path}[/dim]"))
    elif outcome.error is None:
        result.success.append(outcome.path)
        if showlog:
            console.print(tagged("nsc", f"compiled [dim]{outcome.path}[/dim]", "green"))
    else:
        result.failed.append(outcome.path)
        result.errors[outcome.path] = outcome.error
        console.print(tagged("nsc", outcome.error.format(), "red"))


class Builder:
    def __init__(self) -> None:
        self.config = Config()
        self.discovery = Discovery()
        self.cache_file = Path("__nexy__") / "build-cache.json"
        for name in self.config.excludeDirs:
            self.discovery.add_excluded_dir(name)
        self.cache = BuildCache(self.cache_file, persistent=not VFS.is_dev_mode())

    def _files(self) -> list[Path]:
        root = Path("src")
        return self.discovery.scan(root if root.is_dir() else Path(self.config.PROJECT_ROOT))

    def build(self, showlog: bool = False, incremental: bool = True) -> BuildResult:
        self.cache.start(config_fingerprint(), incremental)
        files = self._files()
        result = BuildResult()
        with ThreadPoolExecutor(max_workers=min(os.cpu_count() or 1, len(files) or 1)) as pool:
            for outcome in pool.map(lambda file: _compile(file, self.cache, incremental), files):
                _record(outcome, result, showlog)
        self.cache.save()
        return result


__all__ = ["BuildError", "BuildResult", "Builder", "_get_layout_chain", "_layout_chain_cache"]
