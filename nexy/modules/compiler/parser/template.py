import re

from nexy.modules.compiler.parser.html_parser import NexyHTMLParser
from nexy.modules.compiler.parser.nodes import ElementNode, Node, TextNode


class NexyParserError(Exception):
    """Custom exception for Nexy template parsing errors."""

    pass


class TemplateFormatter:
    """Helper class to format HTML-style attributes into Python/Jinja arguments."""

    _EXPRESSION = re.compile(r"\{\{\s*(.*?)\s*\}\}")
    _ATTR_REGEX = re.compile(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+))')

    @classmethod
    def format_attributes(cls, raw: str) -> str:
        """Takes a raw attribute string and normalizes it.

        Input:  foo = "bar" baz = "qux"
        Output: foo="bar", baz="qux"
        """
        matches = cls._ATTR_REGEX.finditer(raw)
        formatted = [
            f'{m.group(1)}="{m.group(2) or m.group(3) or m.group(4) or ""}"' for m in matches
        ]
        return ", ".join(formatted)

    @classmethod
    def format_dict(cls, attrs: dict[str, str]) -> str:
        """The attributes of a component tag as the arguments of a Jinja call."""
        return ", ".join(cls._format_pair(key, value) for key, value in attrs.items())

    @classmethod
    def _format_pair(cls, key: str, value: str) -> str:
        if "{{" in key and not value:
            argument = cls._argument_from_key(key)
            if argument is not None:
                return argument
        if "{{" in value:
            return f"{key}={cls._expression_of(value)}"
        if cls._is_unquoted_value(value):
            return f"{key}={value}"
        return f'{key}="{value}"'

    @classmethod
    def _argument_from_key(cls, key: str) -> str | None:
        """``{{ ...props }}`` spreads a mapping, ``{{ name }}`` passes ``name=name``."""
        found = cls._EXPRESSION.search(key)
        if not found:
            return None
        inner = found.group(1).strip()
        if inner.startswith(("...", "**")):
            return f"**{inner.lstrip('.*').strip()}"
        if " " not in inner and "(" not in inner:
            return f"{inner}={inner}"
        return None

    @classmethod
    def _expression_of(cls, value: str) -> str:
        """A value with ``{{ }}`` in it: the expression itself, or a ``~`` concatenation."""
        text = value.strip()
        found = cls._EXPRESSION.search(value)
        if text.startswith("{{") and text.endswith("}}") and value.count("{{") == 1 and found:
            return f"({found.group(1).strip()})"
        joined = cls._EXPRESSION.sub(r'" ~ (\1) ~ "', value)
        return f'"{joined}"'.replace('"" ~ ', "").replace(' ~ ""', "")

    @classmethod
    def _is_unquoted_value(cls, value: str) -> bool:
        """Determines if a value should be rendered without quotes in Jinja2."""
        if not value:
            return False

        if value.lower() in ("true", "false", "none"):
            return True

        try:
            float(value)
            return True
        except ValueError:
            pass

        return False


class TemplateParser:
    """
    Parses Nexy templates using an AST-based approach with a protection layer for Jinja2 blocks.
    1. Protects Jinja2 blocks to prevent HTMLParser from mangling them.
    2. Removes ALL comments.
    3. Converts PascalCase tags (<User />) to Jinja2 syntax.
    """

    _HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
    _JINJA_COMMENT_RE = re.compile(r"\{#.*?#\}", re.DOTALL)

    _JINJA_BLOCK_RE = re.compile(r"\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\}", re.DOTALL)

    def __init__(self) -> None:
        self.known_components: set[str] = set()
        self.parser = NexyHTMLParser()
        self.placeholders: list[str] = []
        self.standalone_placeholders: list[str] = []

    _STANDALONE_JINJA_RE = re.compile(r"\{\{|\{%")

    def _protect_jinja(self, html: str) -> str:
        self.placeholders = []

        def replace(match: re.Match[str]) -> str:
            placeholder = f"NXYPJ{len(self.placeholders)}Z"
            self.placeholders.append(match.group(0))
            return placeholder

        result = self._JINJA_BLOCK_RE.sub(replace, html)

        self.standalone_placeholders = []

        def replace_standalone(match: re.Match[str]) -> str:
            placeholder = f"NXPSA{len(self.standalone_placeholders)}Z"
            self.standalone_placeholders.append(match.group(0))
            return placeholder

        return self._STANDALONE_JINJA_RE.sub(replace_standalone, result)

    def _unprotect_jinja(self, html: str) -> str:
        for i, original in enumerate(self.placeholders):
            html = html.replace(f"NXYPJ{i}Z", original)
        for i, original in enumerate(self.standalone_placeholders):
            html = html.replace(f"NXPSA{i}Z", f"{{% raw %}}{original}{{% endraw %}}")
        return html

    def parse(self, html: str, known_components: set[str] | None = None) -> str:
        content = self._HTML_COMMENT_RE.sub("", html)
        content = self._JINJA_COMMENT_RE.sub("", content).strip()

        content = self._protect_jinja(content)

        if known_components:
            self.known_components.update(known_components)

        nodes = self.parser.parse(content)

        self._validate_components(nodes)

        jinja_template = self._render_nodes(nodes)

        return self._unprotect_jinja(jinja_template)

    def _validate_components(self, nodes: list[Node]) -> None:
        for node in nodes:
            if isinstance(node, ElementNode):
                if node.is_component():
                    tag_name = self._unprotect_jinja(node.tag_name)
                    if tag_name not in self.known_components and tag_name != "Slot":
                        raise NexyParserError(
                            f"Missing Import: <{tag_name}> used but not declared."
                        )
                self._validate_components(node.children)

    def _render_nodes(self, nodes: list[Node]) -> str:
        return "".join(self._render_node(node) for node in nodes)

    def _render_node(self, node: Node) -> str:
        if isinstance(node, TextNode):
            return node.content

        if isinstance(node, ElementNode):
            if node.is_component():
                return self._render_component(node)
            else:
                return self._render_element(node)

        return ""

    def _render_component(self, node: ElementNode) -> str:
        unprotected_attrs = {
            self._unprotect_jinja(k): self._unprotect_jinja(v) for k, v in node.attributes.items()
        }
        formatted_attrs = TemplateFormatter.format_dict(unprotected_attrs)

        tag_name = self._unprotect_jinja(node.tag_name)

        if node.is_self_closing and not node.children:
            return f"{{{{ {tag_name}({formatted_attrs}) }}}}"
        else:
            children_content = self._render_nodes(node.children)
            return f"{{% call {tag_name}({formatted_attrs}) %}}{children_content}{{% endcall %}}"

    def _html_attributes(self, node: ElementNode) -> str:
        """The attributes of a plain tag, with a leading space; none gives an empty string."""
        pairs = []
        for key, value in node.attributes.items():
            if "{{" in key and not value:
                pairs.append(self._unprotect_jinja(key))
            elif value:
                pairs.append(f'{key}="{value.replace(chr(34), "&quot;")}"')
            else:
                pairs.append(key)
        return " " + " ".join(pairs) if pairs else ""

    def _render_element(self, node: ElementNode) -> str:
        attributes = self._html_attributes(node)
        if node.is_self_closing:
            return f"<{node.tag_name}{attributes} />"
        children = self._render_nodes(node.children)
        return f"<{node.tag_name}{attributes}>{children}</{node.tag_name}>"
