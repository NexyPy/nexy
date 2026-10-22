import re
from html.parser import HTMLParser

from nexy.compiler.parser.nodes import ElementNode, Node, TextNode

_TAG_NAME_RE = re.compile(r"<([a-zA-Z0-9_:.-]+)")
_ATTR_PATTERN_RE = re.compile(
    r"(?P<name>[a-zA-Z0-9_:.-]+)"
    r"(?:\s*=\s*"
    r'(?:"(?P<v1>[^"]*)"|'
    r"'(?P<v2>[^']*)'|"
    r"(?P<v3>[^\s/>]+)))?",
    re.IGNORECASE,
)

_VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class NexyHTMLParser(HTMLParser):
    """Parses Nexy template HTML into an AST."""

    def __init__(self) -> None:
        super().__init__()
        self.root: list[Node] = []
        self.stack: list[ElementNode] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Handles the start of a tag, preserving case for Nexy components."""
        raw_tag_text = self.get_starttag_text()
        is_self_closing = False
        attr_dict = {}

        if raw_tag_text:
            tag_match = _TAG_NAME_RE.search(raw_tag_text)
            if tag_match:
                tag = tag_match.group(1)

            search_pos = tag_match.end() if tag_match else 0
            for m in _ATTR_PATTERN_RE.finditer(raw_tag_text, search_pos):
                attr_name = m.group("name")
                attr_value = m.group("v1") or m.group("v2") or m.group("v3") or ""
                attr_dict[attr_name] = attr_value

            if raw_tag_text.strip().endswith("/>"):
                is_self_closing = True

        if not attr_dict and attrs:
            attr_dict = {k: (v if v is not None else "") for k, v in attrs}

        node = ElementNode(tag_name=tag, attributes=attr_dict, is_self_closing=is_self_closing)

        if self.stack:
            self.stack[-1].children.append(node)
        else:
            self.root.append(node)

        is_component = tag and tag[0].isupper()
        is_void_html = tag.lower() in _VOID_ELEMENTS

        is_void = is_void_html and not is_component

        if not is_self_closing and not is_void:
            self.stack.append(node)
        else:
            node.is_self_closing = True

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i].tag_name.lower() == tag_lower:
                while len(self.stack) > i:
                    self.stack.pop()
                break

    def handle_data(self, data: str) -> None:
        if not data:
            return

        node = TextNode(content=data)
        if self.stack:
            self.stack[-1].children.append(node)
        else:
            self.root.append(node)

    def parse(self, html: str) -> list[Node]:
        self.root = []
        self.stack = []
        self.feed(html)
        self.close()
        return self.root
