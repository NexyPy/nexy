import os
import hashlib
import json
import traceback as _tb
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from nexy.builder.discovery import Discovery
from nexy.compiler import Compiler
from nexy.core.config import Config
from nexy.utils.common.console import console
from nexy.utils.fs.vfs import VFS


@dataclass
class BuildResult:
    success: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


class Builder:
    def __init__(self) -> None:
        self.config = Config()
        self.discovery = Discovery()
        self.cache_file = Path("__nexy__") / "build-cache.json"
        self.cache: dict[str, str] = {}
        
        exclude_dirs = self.config.excludeDirs
        for name in exclude_dirs:
            self.discovery.add_excluded_dir(name)
        
        self._load_cache()

    def _get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file content for change detection."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _load_cache(self) -> None:
        """Load build cache from disk."""
        if self.cache_file.exists():
            try:
                self.cache = json.loads(self.cache_file.read_text(encoding="utf-8"))
            except Exception:
                self.cache = {}

    def _save_cache(self) -> None:
        """Save build cache to disk."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_text(json.dumps(self.cache, ensure_ascii=False), encoding="utf-8")

    def build(self, showlog: bool = False, incremental: bool = True) -> BuildResult:
        files = self.discovery.scan(self.config.PROJECT_ROOT)
        result = BuildResult()
        max_workers = min(os.cpu_count() or 1, len(files) or 1)

        def compile_file(file_path) -> tuple[str, str | None, bool]:
            input_path = file_path.as_posix()
            file_hash = self._get_file_hash(file_path)
            
            # Check if file is already cached and hasn't changed
            if incremental and input_path in self.cache and self.cache[input_path] == file_hash:
                return input_path, None, True  # skipped (cached)
            
            try:
                compiler = Compiler()
                compiler.compile_with_deps(input=input_path)
                self.cache[input_path] = file_hash
                return input_path, None, False  # compiled
            except Exception as e:
                return input_path, str(e), False  # failed

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(compile_file, f): f for f in files}
            for future in as_completed(futures):
                input_path, error, skipped = future.result()
                if skipped:
                    result.skipped.append(input_path)
                    if showlog:
                        console.print(
                            f"[dim]nsc[/dim] » cached [reset][dim]{input_path}[/dim]"
                        )
                elif error is None:
                    result.success.append(input_path)
                    if showlog:
                        console.print(
                            f"[green]nsc[/green] » compiled [reset][dim]{input_path}[/dim]"
                        )
                else:
                    result.failed.append(input_path)
                    msg = f"error compiling {input_path}: {error}"
                    console.print(f"[red]nsc[/red] » {msg}")
                    if showlog:
                        _tb.print_exc()

        self._save_cache()
        return result


__all__ = ["Builder"]
