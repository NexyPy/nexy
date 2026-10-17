import ast

from nexy.core.config import Config
from nexy.core.models import ParserModel

from .logic import LogicParser
from .scanner import Scanner
from .template import TemplateParser
from .validator import ImportValidator


class Parser:
    def __init__(self) -> None:
        self.scanner = Scanner()
        self.logic_parser = LogicParser()
        self.template_parser = TemplateParser()
        self.config = Config()

    def process(self, source_code: str, current_file: str) -> ParserModel:
        blocks = self.scanner.scan(source_code)

        logic_result = self.logic_parser.process(blocks.logic_block, current_file=current_file)

        ImportValidator.validate_imports(logic_result.nexy_imports, current_file)

        known_components: set[str] = set()
        for imp in logic_result.nexy_imports:
            name = imp.alias if imp.alias else imp.symbol
            if name:
                known_components.add(name)

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

        template_block = blocks.template_block
        jinja_code = self.template_parser.parse(template_block, known_components=known_components)

        return ParserModel(
            frontmatter=logic_result.python_code,
            template=jinja_code,
            props=logic_result.props,
            context=[],
            styles=logic_result.css_imports,
        )


__all__ = ["Parser"]
