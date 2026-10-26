import ast
from collections.abc import Callable

from nexy.core.config import Config
from nexy.core.models import LogicResult, ParserModel
from nexy.errors import NexyCompileError, error_position

from .logic import LogicParser
from .scanner import Scanner
from .template import TemplateParser
from .validator import ImportValidator


def _describe(error: Exception) -> str:
    line, _column = error_position(error)
    return f"line {line}: {error}" if line else str(error)


def _compile_error(current_file: str, errors: list[Exception]) -> NexyCompileError:
    """Normalize one or many phase failures into a single compile error.

    Several independent phases can fail on the same file (import validation, template parsing).
    Aggregating them means one save shows every mistake instead of one fix per run.
    """
    line, column = error_position(errors[0])
    if len(errors) == 1:
        message = str(errors[0])
        hint = "Fix the issue reported above, then save the file to recompile."
    else:
        details = "\n".join(f"  - {_describe(error)}" for error in errors)
        message = f"{len(errors)} errors found:\n{details}"
        hint = "Fix each error listed above, then save the file to recompile."
    return NexyCompileError(
        source_path=current_file, message=message, line=line, column=column, hint=hint
    )


def _attempt[T](action: Callable[[], T], failures: list[Exception]) -> T | None:
    """Run *action*; a failure is recorded and the next phase still runs."""
    try:
        return action()
    except Exception as failure:
        failures.append(failure)
        return None


def _names_of_nexy_imports(logic: LogicResult) -> set[str]:
    """The names the template can use as components: what the .nexy imports bring in."""
    names = ((imp.alias or imp.symbol) for imp in logic.nexy_imports)
    return {name for name in names if name}


def _capitalised_python_imports(python_code: str) -> set[str]:
    """Imported names that start with a capital: Python classes a template may use as tags."""
    try:
        tree = ast.parse(python_code)
    except SyntaxError:
        return set()
    names = {
        alias.asname or alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    return {name for name in names if name and name[0].isupper()}


class Parser:
    def __init__(self) -> None:
        self.scanner = Scanner()
        self.logic_parser = LogicParser()
        self.template_parser = TemplateParser()
        self.config = Config()

    def _parse_logic(self, block: str, current_file: str) -> LogicResult:
        try:
            return self.logic_parser.process(block, current_file=current_file)
        except Exception as error:
            # Template feedback is unreliable when the logic block is broken.
            raise _compile_error(current_file, [error]) from error

    def process(self, source_code: str, current_file: str) -> ParserModel:
        blocks = self.scanner.scan(source_code)
        logic = self._parse_logic(blocks.logic_block, current_file)
        failures: list[Exception] = []
        _attempt(
            lambda: ImportValidator.validate_imports(logic.nexy_imports, current_file), failures
        )
        template = self._parse_template(blocks.template_block, logic, failures)
        if failures:
            raise _compile_error(current_file, failures) from failures[0]
        return ParserModel(
            frontmatter=logic.python_code,
            template=template or "",
            props=logic.props,
            context=[],
            styles=logic.css_imports,
        )

    def _parse_template(
        self, block: str, logic: LogicResult, failures: list[Exception]
    ) -> str | None:
        components = _names_of_nexy_imports(logic)
        if logic.python_code:
            components |= _capitalised_python_imports(logic.python_code)
        parse = self.template_parser.parse
        return _attempt(lambda: parse(block, known_components=components), failures)


__all__ = ["Parser"]
