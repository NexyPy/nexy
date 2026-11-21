"""The literal props each island gets in the .nexy files, so the build snapshots each set (#554).

A page that writes ``<Spike label="clicks" />`` serves ``Spike`` rendered with ``label="clicks"``
before hydration. Props computed at request time (``{{ }}``), spread props and islands with
children keep the default snapshot: their values are not known at build.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

from jinja2 import Environment, TemplateSyntaxError

from nexy.core.models import ComponentType
from nexy.helpers.imports.ncc import NexyClientComponent, snapshot_key
from nexy.modules.compiler.parser.html_parser import NexyHTMLParser
from nexy.modules.compiler.parser.logic import LogicParser
from nexy.modules.compiler.parser.nodes import ElementNode, Node
from nexy.modules.compiler.parser.scanner import Scanner
from nexy.modules.compiler.parser.template import TemplateFormatter

MANIFEST = Path("__nexy__/client/island-props.json")
Manifest = dict[str, dict[str, dict[str, dict[str, Any]]]]

_ISLANDS = {
    ComponentType.REACT,
    ComponentType.PREACT,
    ComponentType.SOLID,
    ComponentType.VUE,
    ComponentType.SVELTE,
}
_JINJA_BLOCK = re.compile(r"\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\}", re.DOTALL)
_COMPUTED = "NXYPJ0Z"
_NOT_PROPS = ("directive", "media")
_JINJA = Environment(autoescape=True)


def write_manifest(files: Iterable[Path]) -> None:
    """Write the manifest the client build reads to render each island once per set of props."""
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(collect(files), indent=2), encoding="utf-8")


def collect(files: Iterable[Path]) -> Manifest:
    """For each island file, symbol and snapshot key, the props to render it with."""
    manifest: Manifest = {}
    for file in files:
        for url, symbol, props in _usages(file):
            by_key = manifest.setdefault(url.lstrip("/"), {}).setdefault(symbol, {})
            by_key[snapshot_key(json.dumps(props))] = props
    return manifest


def _usages(file: Path) -> Iterator[tuple[str, str, dict[str, Any]]]:
    scan = Scanner().process(file.read_text(encoding="utf-8"))
    islands = _islands(scan.logic_block, file)
    for tag, props in literal_props(scan.template_block):
        if tag in islands:
            path, symbol = islands[tag]
            yield NexyClientComponent(path, "", symbol).resolve_path(), symbol, props


def _islands(logic: str, file: Path) -> dict[str, tuple[str, str]]:
    imports = LogicParser().process(logic, str(file)).nexy_imports
    return {
        i.alias: (i.path, i.symbol)
        for i in imports
        if i.alias and i.symbol and i.comp_type in _ISLANDS
    }


def literal_props(template: str) -> Iterator[tuple[str, dict[str, Any]]]:
    """The tag and props of each self-closing component tag whose attributes are all literal."""
    for node in _elements(NexyHTMLParser().parse(_JINJA_BLOCK.sub(_COMPUTED, template))):
        props = _props_of(node)
        if props:
            yield node.tag_name, props


def _elements(nodes: list[Node]) -> Iterator[ElementNode]:
    for node in nodes:
        if isinstance(node, ElementNode):
            yield node
            yield from _elements(node.children)


def _props_of(node: ElementNode) -> dict[str, Any]:
    """The props of an island as the page passes them, or none when they are not all literal."""
    attrs = node.attributes
    if not (node.is_component() and node.is_self_closing and not node.children):
        return {}
    if any(_COMPUTED in key or _COMPUTED in value for key, value in attrs.items()):
        return {}
    try:
        props = _JINJA.compile_expression(f"dict({TemplateFormatter.format_dict(attrs)})")()
    except TemplateSyntaxError:
        return {}
    return {key: value for key, value in props.items() if key not in _NOT_PROPS}
