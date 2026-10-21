import json
import os
import threading
import traceback as _tb
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from nexy.builder.discovery import Discovery
from nexy.compiler import Compiler
from nexy.core.config import Config
from nexy.errors import NexyCompileError
from nexy.utils.common.console import console
from nexy.utils.fs.fingerprint import first_stat_fingerprint, stat_fingerprint
from nexy.utils.fs.vfs import VFS


@dataclass
class BuildError:
    path: str
    message: str
    line: int | None = None
    column: int | None = None
    type: str = "Exception"

    def format(self) -> str:
        if self.line is not None:
            col = self.column if self.column is not None else 0
            return f"{self.path}:{self.line}:{col} - [{self.type}] {self.message}"
        return f"{self.path} - [{self.type}] {self.message}"


@dataclass
class BuildResult:
    success: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: dict[str, BuildError] = field(default_factory=dict)


_THREAD_LOCAL = threading.local()
_layout_chain_cache: dict[str, str] = {}

_LAYOUT_ROOT: Path | None = None
_LAYOUT_LIMIT: Path | None = None


def _layout_bounds() -> tuple[Path, Path]:
    global _LAYOUT_ROOT, _LAYOUT_LIMIT
    if _LAYOUT_ROOT is None:
        root = Path(Config.ROUTER_PATH).resolve()
        _LAYOUT_ROOT = root
        _LAYOUT_LIMIT = root.parent
    return _LAYOUT_ROOT, _LAYOUT_LIMIT or _LAYOUT_ROOT


def _get_thread_compiler() -> Compiler:
    """Return a thread-local Compiler instance to avoid per-file construction cost."""
    compiler = getattr(_THREAD_LOCAL, "compiler", None)
    if compiler is None:
        compiler = Compiler()
        _THREAD_LOCAL.compiler = compiler
    return compiler


def _get_layout_chain(directory: Path) -> str:
    """Fingerprint of every layout.* wrapping this directory, cached per dir."""
    key = directory.as_posix()
    if key in _layout_chain_cache:
        return _layout_chain_cache[key]
    root, limit = _layout_bounds()
    parts: list[str] = []
    current = directory
    while str(current).startswith(str(limit)):
        for name in Config.LAYOUT_FILE_NAMES:
            layout_file = current / name
            if layout_file.is_file():
                lst = layout_file.stat()
                parts.append(f"L{layout_file.as_posix()}:{lst.st_mtime_ns}:{lst.st_size}")
        if current in (root, limit):
            break
        current = current.parent
    chain = "|".join(parts)
    _layout_chain_cache[key] = chain
    return chain


def _get_file_fingerprint(file_path: Path) -> str:
    """Change fingerprint of a route file: stat plus its layout chain."""
    base = stat_fingerprint(file_path)
    if not base:
        return ""
    chain = _get_layout_chain(file_path.parent.resolve())
    return base + (f"|{chain}" if chain else "")


def _get_config_fingerprint() -> str:
    """Config drives compile behaviour (layouts, aliases, FF) - any change
    must invalidate the whole build cache."""
    return first_stat_fingerprint(
        ("nexyconfig.py", "nexyconfig.example.py", "nexyconfig.toml", "pyproject.toml")
    )


class Builder:
    def __init__(self) -> None:
        self.config = Config()
        self.discovery = Discovery()
        self.cache_file = Path("__nexy__") / "build-cache.json"
        self.cache: dict[str, str] = {}

        exclude_dirs = self.config.excludeDirs
        for name in exclude_dirs:
            self.discovery.add_excluded_dir(name)

        self._dev_mode = VFS.is_dev_mode()
        self._load_cache()

    def _load_cache(self) -> None:
        """Load build cache from disk.

        The cache persists across `nx build` runs (incremental rebuilds).
        In dev mode the compiled output lives only in memory, so a stale
        disk cache would skip compilation entirely and leave the VFS empty.
        """
        if self._dev_mode:
            self.cache = {}
            return
        if self.cache_file.exists():
            try:
                self.cache = json.loads(self.cache_file.read_text(encoding="utf-8"))
            except Exception:
                self.cache = {}

    def _save_cache(self) -> None:
        """Save build cache to disk (skipped in dev mode: memory-only)."""
        if self._dev_mode:
            return
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_text(json.dumps(self.cache, ensure_ascii=False), encoding="utf-8")

    def build(self, showlog: bool = False, incremental: bool = True) -> BuildResult:
        cfg_fp = _get_config_fingerprint()
        if incremental and self.cache.get("__config__") != cfg_fp:
            self.cache = {}
        self.cache["__config__"] = cfg_fp
        scan_root = Path("src")
        if not scan_root.is_dir():
            scan_root = Path(self.config.PROJECT_ROOT)
        files = self.discovery.scan(scan_root)
        result = BuildResult()
        max_workers = min(os.cpu_count() or 1, len(files) or 1)

        def compile_file(file_path: Path) -> tuple[str, BuildError | None, bool]:
            rel = file_path.resolve().relative_to(Path.cwd())
            input_path = rel.as_posix()
            file_hash = _get_file_fingerprint(file_path)

            if incremental and input_path in self.cache and self.cache[input_path] == file_hash:
                return input_path, None, True

            try:
                compiler = _get_thread_compiler()
                compiler.compile_with_deps(input=input_path)
                self.cache[input_path] = file_hash
                return input_path, None, False
            except NexyCompileError as e:
                return (
                    input_path,
                    BuildError(
                        path=e.source_path,
                        message=e.message,
                        line=e.line,
                        column=e.column,
                        type="NexyCompileError",
                    ),
                    False,
                )
            except Exception as e:
                return (
                    input_path,
                    BuildError(
                        path=input_path,
                        message=str(e),
                        line=None,
                        column=None,
                        type=type(e).__name__,
                    ),
                    False,
                )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(compile_file, f): f for f in files}
            for future in as_completed(futures):
                input_path, error, skipped = future.result()
                if skipped:
                    result.skipped.append(input_path)
                    if showlog:
                        console.print(f"[dim]nsc[/dim] » cached [reset][dim]{input_path}[/dim]")
                elif error is None:
                    result.success.append(input_path)
                    if showlog:
                        console.print(
                            f"[green]nsc[/green] » compiled [reset][dim]{input_path}[/dim]"
                        )
                else:
                    result.failed.append(input_path)
                    result.errors[input_path] = error
                    console.print(f"[red]nsc[/red] » {error.format()}")
                    if showlog:
                        _tb.print_exc()

        self._save_cache()
        return result


__all__ = ["Builder"]
