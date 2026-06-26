import os
import traceback as _tb
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from nexy.builder.discovery import Discovery
from nexy.compiler import Compiler
from nexy.core.config import Config
from nexy.utils.common.console import console
from nexy.utils.fs.vfs import VFS


@dataclass
class BuildResult:
    success: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)


class Builder:
    def __init__(self) -> None:
        self.config = Config()
        self.discovery = Discovery()

        exclude_dirs = self.config.excludeDirs
        for name in exclude_dirs:
            self.discovery.add_excluded_dir(name)

    def build(self, showlog: bool = False) -> BuildResult:
        VFS().clear()
        files = self.discovery.scan(self.config.PROJECT_ROOT)
        result = BuildResult()
        max_workers = min(os.cpu_count() or 1, len(files) or 1)

        def compile_file(file_path) -> tuple[str, str | None]:
            input_path = file_path.as_posix()
            try:
                compiler = Compiler()
                compiler.compile_with_deps(input=input_path)
                return input_path, None
            except Exception as e:
                return input_path, str(e)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(compile_file, f): f for f in files}
            for future in as_completed(futures):
                input_path, error = future.result()
                if error is None:
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

        return result


__all__ = ["Builder"]
