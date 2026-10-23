import ast

from nexy.core.config import Config
from nexy.core.models import ParserModel
from nexy.errors import NexyCompileError

from .logic import LogicParser
from .scanner import Scanner
from .template import TemplateParser
from .validator import ImportValidator


def _describe(error: Exception) -> str:
    line = getattr(error, "lineno", None) or getattr(error, "line", None)
    return f"line {line}: {error}" if line else str(error)


def _compile_error(current_file: str, errors: list[Exception]) -> NexyCompileError:
    """Normalize one or many phase failures into a single compile error.

    Several independent phases can fail on the same file (import validation,
    template parsing). Aggregating them means one save shows every mistake
    instead of one fix per run.
    """
    first = errors[0]
    line = getattr(first, "lineno", None) or getattr(first, "line", None)
    column = getattr(first, "offset", None) or getattr(first, "column", None)
    if len(errors) == 1:
        return NexyCompileError(
            source_path=current_file,
            message=str(first),
            line=line,
            column=column,
            hint="Fix the issue reported above, then save the file to recompile.",
        )
    details = "\n".join(f"  - {_describe(error)}" for error in errors)
    return NexyCompileError(
        source_path=current_file,
        message=f"{len(errors)} errors found:\n{details}",
        line=line,
        column=column,
        hint="Fix each error listed above, then save the file to recompile.",
    )


class Parser:
    def __init__(self) -> None:
        self.scanner = Scanner()
        self.logic_parser = LogicParser()
        self.template_parser = TemplateParser()
        self.config = Config()

    def process(self, source_code: str, current_file: str) -> ParserModel:
        blocks = self.scanner.scan(source_code)

        try:
            logic_result = self.logic_parser.process(blocks.logic_block, current_file=current_file)
        except Exception as e:
            # Template feedback is unreliable when the logic block is broken.
            raise _compile_error(current_file, [e]) from e

        known_components: set[str] = set()
        for imp in logic_result.nexy_imports:
            name = imp.alias if imp.alias else imp.symbol
            if name:
                known_components.add(name)

        errors: list[Exception] = []
        try:
            ImportValidator.validate_imports(logic_result.nexy_imports, current_file)
        except Exception as e:
            errors.append(e)

        if logic_result.python_code:
            try:
                tree = ast.parse(logic_result.python_code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            name = alias.asname or alias.name
                            if name and name[0].isupper():
                                known_components.add(name)
            except SyntaxError:
                pass

        try:
            template_block = blocks.template_block
            jinja_code = self.template_parser.parse(
                template_block, known_components=known_components
            )
        except Exception as e:
            errors.append(e)

        if errors:
            raise _compile_error(current_file, errors) from errors[0]

        return ParserModel(
            frontmatter=logic_result.python_code,
            template=jinja_code,
            props=logic_result.props,
            context=[],
            styles=logic_result.css_imports,
        )


__all__ = ["Parser"]
