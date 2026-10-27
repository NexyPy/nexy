import re
from html.parser import HTMLParser

from nexy.modules.compiler.parser.nodes import ElementNode, Node, TextNode

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


def _tag_attributes(raw_tag: str, start: int) -> dict[str, str]:
    """The attributes written in a start tag, as the source spelled them (case included)."""
    attributes = {}
    for found in _ATTR_PATTERN_RE.finditer(raw_tag, start):
        value = found.group("v1") or found.group("v2") or found.group("v3") or ""
        attributes[found.group("name")] = value
    return attributes


def _read_start_tag(
    tag: str, attrs: list[tuple[str, str | None]], raw_tag: str | None
) -> tuple[str, dict[str, str], bool]:
    """(tag name, attributes, written as ``<tag />``) of a start tag.

    HTMLParser lowercases names, but ``<UserCard />`` is a component: the raw text of the tag
    has the real spelling, so it is read first and HTMLParser's own result is the fallback.
    """
    name, attributes, self_closing = tag, {}, False
    if raw_tag:
        found = _TAG_NAME_RE.search(raw_tag)
        name = found.group(1) if found else tag
        attributes = _tag_attributes(raw_tag, found.end() if found else 0)
        self_closing = raw_tag.strip().endswith("/>")
    if not attributes and attrs:
        attributes = {key: (value if value is not None else "") for key, value in attrs}
    return name, attributes, self_closing


class NexyHTMLParser(HTMLParser):
    """Parses Nexy template HTML into an AST."""

    def __init__(self) -> None:
        super().__init__()
        self.root: list[Node] = []
        self.stack: list[ElementNode] = []

    def _append(self, node: Node) -> None:
        """Add *node* to the element being read, or to the root."""
        (self.stack[-1].children if self.stack else self.root).append(node)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Handles the start of a tag, preserving case for Nexy components."""
        name, attributes, self_closing = _read_start_tag(tag, attrs, self.get_starttag_text())
        node = ElementNode(tag_name=name, attributes=attributes, is_self_closing=self_closing)
        self._append(node)
        is_component = bool(name) and name[0].isupper()
        if self_closing or (name.lower() in _VOID_ELEMENTS and not is_component):
            node.is_self_closing = True
        else:
            self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i].tag_name.lower() == tag_lower:
                del self.stack[i:]
                break

    def handle_decl(self, decl: str) -> None:
        """Keep ``<!DOCTYPE html>``; dropping it puts the page in quirks mode."""
        self.handle_data(f"<!{decl}>")

    def handle_data(self, data: str) -> None:
        if data:
            self._append(TextNode(content=data))

    def parse(self, html: str) -> list[Node]:
        self.root = []
        self.stack = []
        self.feed(html)
        self.close()
        return self.root
