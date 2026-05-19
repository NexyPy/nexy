from dataclasses import dataclass, field

from nexy.builder.cache import BuildCache
from nexy.builder.discovery import Discovery
from nexy.compiler import Compiler
from nexy.core.config import Config
from nexy.core.string import StringTransform
from nexy.utils.common.console import console
from nexy.utils.fs.vfs import VFS


@dataclass
class BuildResult:
    success: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)


class Builder:
    def __init__(self) -> None:
        self.discovery = Discovery()
        self.compiler = Compiler()
        self.config = Config()
        self.vfs = VFS()

        exclude_dirs = self.config.excludeDirs
        for name in exclude_dirs:
            self.discovery.add_excluded_dir(name)

    def _vfs_has_output(self, input_path: str) -> bool:
        """Check if VFS has the compiled output for a given input file."""
        if not input_path.endswith((".nexy", ".mdx")):
            return True
        mapped = StringTransform.normalize_route_path_for_namespace(input_path)
        ns = self.config.NAMESPACE.strip("/")
        ext = ".html" if input_path.endswith(".nexy") else ".md"
        html_path = f"{ns}/{mapped.replace('.nexy', ext).replace('.mdx', ext)}"
        py_path = html_path.replace(ext, ".py")
        exists = self.vfs.exists(py_path)
        if not exists:
            pass
        return exists

    def build(self, showlog: bool = False) -> BuildResult:
        files = self.discovery.scan(self.config.PROJECT_ROOT)
        result = BuildResult()
        cache = BuildCache()
        for file in files:
            input_path = file.as_posix()
            if cache.is_cached(file) and self._vfs_has_output(input_path):
                result.success.append(input_path)
                continue
            try:
                self.compiler.compile(input=input_path)
                result.success.append(input_path)
                cache.mark_cached(file)
                if showlog:
                    console.print(
                        f"[green]nsc[/green] » compiled [reset][dim]{input_path}[/dim]"
                    )
            except Exception as e:
                result.failed.append(input_path)
                msg = f"error compiling {input_path}: {e}"
                console.print(f"[red]nsc[/red] » {msg}")
                if showlog:
                    import traceback as _tb
                    _tb.print_exc()
        cache.flush()
        return result


__all__ = ["Builder"]
