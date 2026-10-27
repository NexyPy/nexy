from nexy.core.config import Config
from nexy.core.models import ParserModel
from nexy.core.string import StringTransform
from nexy.errors import NexyCompileError, error_position
from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.modules.compiler.dependencies import compile_dependencies
from nexy.modules.compiler.frontend_route import FrontendRouteCompiler
from nexy.modules.compiler.generator import Generator
from nexy.modules.compiler.markdown_route import MarkdownRouteCompiler
from nexy.modules.compiler.parser import Parser

_FIX_SYNTAX = "Fix the syntax at the reported location, then save the file to recompile."
_UNSUPPORTED = "Use a .nexy, .md or framework route file (.tsx/.vue/.svelte/.mdx)."


def is_nexy_file(file_path: str) -> bool:
    return file_path.endswith(".nexy")


def is_md_file(file_path: str) -> bool:
    return file_path.endswith(".md")


def is_framework_route_file(file_path: str) -> bool:
    """Files Vite compiles: Python only writes the thin wrapper that serves them (MDX included)."""
    return file_path.endswith((".tsx", ".vue", ".svelte", ".mdx"))


def default_output(input_path: str) -> str:
    """Where a component's compiled HTML goes: its namespaced path with an ``.html`` extension."""
    mapped = StringTransform.normalize_route_path_for_namespace(input_path)
    namespace = Config.NAMESPACE.strip("/")
    return f"{namespace}/{mapped.replace('.nexy', '.html')}"


def _compile_error(path: str, failure: Exception) -> NexyCompileError:
    """A compile error with the position the failure carries (a syntax error has both)."""
    line, column = error_position(failure)
    return NexyCompileError(
        source_path=path, message=str(failure), line=line, column=column, hint=_FIX_SYNTAX
    )


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
        if is_framework_route_file(input):
            self.frontend_route.compile(input=input)
        elif is_md_file(input):
            self.markdown_route.compile(input=input)
        else:
            self._compile_component()

    def _compile_component(self) -> None:
        """Compile a .nexy file: parse it, then generate its Python and HTML."""
        self.source_code = self._load_source()
        if not is_nexy_file(self.input):
            raise self._unsupported()
        if self.output is None:
            self.output = default_output(self.input)
        try:
            parsed: ParserModel = self.parser.process(
                source_code=self.source_code, current_file=self.input
            )
            self.generator.generate(self.output, parsed, source_path=self.input)
        except NexyCompileError:
            raise
        except Exception as failure:
            raise _compile_error(self.input, failure) from failure

    def _unsupported(self) -> NexyCompileError:
        message = f"File '{self.input}' is not a nexy component"
        console.print(tagged("nsc", message, "red"))
        return NexyCompileError(source_path=self.input, message=message, hint=_UNSUPPORTED)

    def compile_with_deps(self, input: str, output: str | None = None) -> None:
        compile_dependencies(input, lambda dependency: Compiler().compile(input=dependency))
        self.compile(input=input, output=output)


__all__ = ["Compiler"]
