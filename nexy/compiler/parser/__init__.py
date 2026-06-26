import ast
import re

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

    def _clean_jinja_wrapping(self, html_content: str) -> str:
        # Clean {% ... %}
        content = re.sub(r"<([a-zA-Z0-9]+)>\s*({%.*?%})\s*</\1>", r"\2", html_content)
        # Clean {{ ... }}
        content = re.sub(r"<([a-zA-Z0-9]+)>\s*({{.*?}})\s*</\1>", r"\2", content)
        return content

    def process(self, source_code: str, current_file: str) -> ParserModel:
        # 1. Split into blocks
        blocks = self.scanner.scan(source_code)

        # 2. Parse logic (Python)
        logic_result = self.logic_parser.process(blocks.logic_block, current_file=current_file)

        # 2.5. Validate imports
        ImportValidator.validate_imports(logic_result.nexy_imports, current_file)

        # 3. Collect known components for template
        # Extract aliases or symbol names from Nexy imports
        known_components: set[str] = set()
        for imp in logic_result.nexy_imports:
            # If 'import X as Y', look for 'Y' in template
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
        is_mdx = current_file.endswith(".mdx")
        mdx_code_blocks: list[str] = []

        if is_mdx:
            fence_re = re.compile(
                r"^(?:```|~~~)\S*[ \t]*\n.*?(?:```|~~~)[ \t]*$",
                re.MULTILINE | re.DOTALL,
            )
            inline_backtick_re = re.compile(r"`([^`]*)`")

            def save_fence(m):
                mdx_code_blocks.append(m.group(0))
                return f"NXCMD{len(mdx_code_blocks) - 1}Z"

            template_block = fence_re.sub(save_fence, template_block)

            replace_jinja_re = re.compile(r"\{\{|\}\}|\{%|%\}")

            def escape_inline(m):
                content = m.group(1)
                content = content.replace("<", "&lt;").replace(">", "&gt;")

                def repl(m2):
                    return {
                        "{{": "{{ '{{' }}",
                        "}}": "{{ '}}' }}",
                        "{%": "{{ '{%' }}",
                        "%}": "{{ '%}' }}",
                    }[m2.group(0)]

                content = replace_jinja_re.sub(repl, content)
                return f"`{content}`"

            template_block = inline_backtick_re.sub(escape_inline, template_block)

        jinja_code = self.template_parser.parse(template_block, known_components=known_components)

        if mdx_code_blocks:
            endraw_re = re.compile(r"(\{%-?\s*endraw\s*-?%\})")

            for i, block in enumerate(mdx_code_blocks):
                parts = endraw_re.split(block)
                safe_parts = []
                for j, part in enumerate(parts):
                    if j % 2 == 0:
                        safe_parts.append(f"{{% raw %}}{part}{{% endraw %}}")
                    else:
                        escaped = part.replace("{%", "{{ '{%' }}")
                        escaped = escaped.replace("%}", "{{ '%}' }}")
                        safe_parts.append(escaped)
                safe_block = "".join(safe_parts)
                jinja_code = jinja_code.replace(f"NXCMD{i}Z", safe_block)

        if is_mdx:
            jinja_code = self._clean_jinja_wrapping(jinja_code)

        return ParserModel(
            frontmatter=logic_result.python_code,
            template=jinja_code,
            props=logic_result.props,
            context=[],
            styles=logic_result.css_imports,
        )


__all__ = ["Parser"]
