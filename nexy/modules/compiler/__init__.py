import pathlib
import re

from nexy.core.config import Config
from nexy.core.models import ParserModel
from nexy.errors import NexyCompileError
from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.helpers.fs.vfs import VFS
from nexy.modules.compiler.frontend_route import FrontendRouteCompiler
from nexy.modules.compiler.generator import Generator
from nexy.modules.compiler.markdown_route import MarkdownRouteCompiler
from nexy.modules.compiler.parser import Parser


def is_nexy_file(file_path: str) -> bool:
    return file_path.endswith(".nexy")


def is_mdx_file(file_path: str) -> bool:
    return file_path.endswith(".mdx")


def is_md_file(file_path: str) -> bool:
    return file_path.endswith(".md")


def is_framework_route_file(file_path: str) -> bool:
    return file_path.endswith((".tsx", ".vue", ".svelte"))


_CODE_FENCE_RE = re.compile(
    r"^(?:```|~~~)\S*[ \t]*\n.*?^(?:```|~~~)[ \t]*$",
    re.MULTILINE | re.DOTALL,
)

_IMPORT_FROM_RE = re.compile(
    r'^\s*from\s+["\'](?P<path>[^"\']+)["\']\s+import',
    re.M,
)
_ALIAS_RE = re.compile(r"^[@~$]")


def _resolve_dep_path(current: str, import_path: str) -> str | None:
    cfg = Config()
    root = pathlib.Path(cfg.PROJECT_ROOT).resolve()
    cur = pathlib.Path(current).resolve()
    if _ALIAS_RE.match(import_path):
        for alias, replacement in cfg.ALIASES.items():
            if import_path.startswith(alias):
                resolved = root / import_path.replace(alias, replacement, 1)
                return resolved.relative_to(root).as_posix()
    if import_path.startswith(("./", "../")):
        try:
            return (cur.parent / import_path).resolve().relative_to(root).as_posix()
        except ValueError:
            return None
    return None


def _compile_with_deps(input_path: str, _compiling: set[str] | None = None) -> None:
    if _compiling is None:
        _compiling = set()
    abs_path = str(pathlib.Path(input_path).resolve())
    if abs_path in _compiling:
        return
    _compiling.add(abs_path)

    if is_framework_route_file(input_path) or is_md_file(input_path):
        return

    try:
        with open(input_path, encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        return
    clean = _CODE_FENCE_RE.sub("\n", source)
    for m in _IMPORT_FROM_RE.finditer(clean):
        dep = _resolve_dep_path(input_path, m.group("path"))
        if dep and dep.endswith(".nexy"):
            vfs = VFS()
            dep_output = f"{Config.NAMESPACE.strip('/')}/{dep}"
            dep_output = dep_output.replace(".nexy", ".html")
            dep_py = str(pathlib.Path(dep_output).with_suffix(".py"))
            if not vfs.exists(dep_py):
                _compile_with_deps(dep, _compiling)
                Compiler().compile(input=dep)


class Compiler:
    def __init__(self) -> None:
        self.input: str = ""
        self.output: str | None = None
        self.config = Config()
        self.parser = Parser()
        self.generator = Generator()
        self.frontend_route = FrontendRouteCompiler()
        self.markdown_route = MarkdownRouteCompiler()
        self.source_code: str = ""

    def _load_source(self) -> str:
        try:
            with open(self.input, encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File '{self.input}' not found.") from e

    def compile(self, input: str, output: str | None = None) -> None:
        self.input = input
        self.output = output

        if is_framework_route_file(self.input):
            self.frontend_route.compile(input=self.input)
            return

        if is_md_file(self.input):
            self.markdown_route.compile(input=self.input)
            return

        self.source_code = self._load_source()
        if is_nexy_file(self.input) or is_mdx_file(self.input):
            if self.output is None:
                from nexy.core.string import StringTransform

                mapped = StringTransform.normalize_route_path_for_namespace(self.input)
                namespace = self.config.NAMESPACE.strip("/")
                if is_mdx_file(self.input):
                    self.output = f"{namespace}/{mapped.replace('.mdx', '.mdx.html')}"
                else:
                    self.output = f"{namespace}/{mapped.replace('.nexy', '.html')}"

        else:
            msg = f"File '{self.input}' is not a nexy component"
            console.print(tagged("nsc", msg, "red"))
            raise NexyCompileError(
                source_path=self.input,
                message=msg,
                hint="Use a .nexy, .mdx, .md or framework route file (.tsx/.vue/.svelte).",
            )

        try:
            code_parsed: ParserModel = self.parser.process(
                source_code=self.source_code, current_file=self.input
            )
            self.generator.generate(self.output, code_parsed, source_path=self.input)
        except NexyCompileError:
            raise
        except Exception as e:
            line = getattr(e, "lineno", None) or getattr(e, "line", None)
            col = getattr(e, "offset", None) or getattr(e, "column", None)
            msg = str(e)
            raise NexyCompileError(
                source_path=self.input,
                message=msg,
                line=line,
                column=col,
                hint="Fix the syntax at the reported location, then save the file to recompile.",
            ) from e

    def compile_with_deps(self, input: str, output: str | None = None) -> None:
        _compile_with_deps(input)
        self.compile(input=input, output=output)


__all__ = ["Compiler"]
