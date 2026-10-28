"""Turns the frontmatter and template of a .nexy file into the Python module that renders it."""

from __future__ import annotations

import ast
import re
import textwrap
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from nexy.core.config import Config
from nexy.core.models import NexyProp, ParserModel
from nexy.core.string import StringTransform
from nexy.helpers.fs.vfs import VFS
from nexy.modules.compiler.document_shell import is_route_file, layout_parts
from nexy.modules.routers.fbrouter.layout import RouteLayout

_LAYOUT_CHILDREN = "children = f\"<nslot  style='display:contents;'>{children}</nslot>\" "
_SLOT = (
    "Slot = caller if (locals().get('caller') and callable(caller)) else "
    "(lambda: children if locals().get('children') else '')"
)
_INJECTED_PROPS = {"caller": "caller: Any = None", "children": "children: str = ''"}

_MODULE = """from typing import *
from fastapi import *
from pathlib import Path as __Path
from nexy import Template as __Template
from nexy.helpers.imports.component_import import _Import as __Import
from nexy.modules.routers.actions.store import ACTIONS_STORE as __ACTIONS_STORE
from jinja2 import Template as __JinjaTemplate
NexyElement = Union[callable, __JinjaTemplate]
{layout_header}
{module_imports}
def {name}({props}) -> str:
    {slot}
{logic}
    {layout_children}
    context = {{{context_items}}}
    context.update(__ACTIONS_STORE.template_context())
    rendered = str(__Template().render("{template_path}", context))
    return {render_wrapper}
"""


@dataclass(frozen=True)
class Shell:
    """What surrounds a component: the import of its layout, how it is wrapped, its children."""

    header: str = ""
    wrapper: str = "rendered"
    children: str = ""


def split_imports(frontmatter: str) -> tuple[str, str]:
    """The imports of the frontmatter, and the rest; both empty-safe when it does not parse."""
    try:
        body = ast.parse(frontmatter).body
    except SyntaxError:
        return "", frontmatter
    imports = [node for node in body if isinstance(node, ast.Import | ast.ImportFrom)]
    if not imports:
        return "", frontmatter
    rest = [node for node in body if node not in imports]
    return _unparse(imports), _unparse(rest) if rest else ""


# Names a router reads from the module of a page, not from inside its component.
ROUTE_EXPORTS = ("revalidate", "metadata")


def _is_route_export(node: ast.stmt) -> bool:
    """A top-level `revalidate = 60` or `metadata = {...}`: only a literal value can be exported."""
    if not isinstance(node, ast.Assign) or len(node.targets) != 1:
        return False
    target = node.targets[0]
    if not isinstance(target, ast.Name) or target.id not in ROUTE_EXPORTS:
        return False
    try:
        ast.literal_eval(node.value)
    except ValueError:
        return False
    return True


def split_route_exports(frontmatter: str) -> tuple[str, str]:
    """The route exports of the frontmatter, and the rest.

    The frontmatter runs inside the component function, so `revalidate = 60` written there is a
    local variable no router can see. These literals are written at module level instead.
    """
    try:
        body = ast.parse(frontmatter).body
    except SyntaxError:
        return "", frontmatter
    exports = [node for node in body if _is_route_export(node)]
    if not exports:
        return "", frontmatter
    rest = [node for node in body if node not in exports]
    return _unparse(exports), _unparse(rest) if rest else ""


def split_frontmatter(frontmatter: str) -> tuple[str, str]:
    """What goes at module level (imports, route exports) and what runs in the component."""
    exports, rest = split_route_exports(frontmatter)
    imports, body = split_imports(rest)
    return "\n".join(part for part in (imports, exports) if part), body


def _unparse(nodes: Sequence[ast.stmt]) -> str:
    return ast.unparse(ast.Module(body=list(nodes), type_ignores=[]))


def _names_of(node: ast.stmt) -> list[str]:
    """The names a top-level statement makes available to the template."""
    if isinstance(node, ast.ImportFrom):
        return [alias.asname or alias.name for alias in node.names if alias.name != "*"]
    if isinstance(node, ast.Import):
        return [alias.asname or alias.name.split(".")[0] for alias in node.names]
    if isinstance(node, ast.Assign):
        return [target.id for target in node.targets if isinstance(target, ast.Name)]
    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
        return [node.name]
    return []


def template_names(frontmatter: str, props: list[NexyProp]) -> list[str]:
    """Names the template can use: those of the frontmatter, then the props; no private ones."""
    try:
        body = ast.parse(frontmatter).body
    except SyntaxError:
        body = []
    names = [name for node in body for name in _names_of(node)]
    names += [prop.name for prop in props]
    return [name for name in dict.fromkeys(names) if not name.startswith("_")]


def context_literal(names: list[str]) -> str:
    """The body of the context dict: each name, then the slot."""
    return ", ".join([*(f'"{name}": {name}' for name in names), "'Slot': Slot"])


def props_signature(props: list[NexyProp]) -> str:
    """The declared props, then `caller` and `children` unless the component declares them."""
    declared = [f"{p.name}: {p.type} = {p.default}" for p in props]
    names = {p.name for p in props}
    injected = [text for name, text in _INJECTED_PROPS.items() if name not in names]
    return ", ".join([*declared, *injected])


def layout_shell(source_path: str) -> Shell:
    """How the component at *source_path* is wrapped: by its layout, by the client shell, or not."""
    if Config.useRouter is not None:
        return Shell()
    is_layout = Path(source_path).name.lower() in Config.LAYOUT_FILE_NAMES
    layout = RouteLayout.get_closest_import(source_path, is_layout=is_layout)
    header, wrapper = layout_parts(
        layout, fallback_shell=not is_layout and is_route_file(source_path)
    )
    return Shell(header, wrapper, _LAYOUT_CHILDREN if is_layout else "")


def function_name(template_path: str) -> str:
    """A valid Python name for the component rendered from *template_path*."""
    raw = StringTransform().get_component_name(Path(template_path).stem)
    return re.sub(r"[^a-zA-Z0-9_]", "_", raw)


def module_path(template_path: str) -> str:
    """Where the module of the component at *template_path* is written."""
    return Path(template_path).with_suffix(".py").as_posix()


def render_module(template_path: str, source: ParserModel, source_path: str | None = None) -> str:
    """The Python module that renders the component: pure, nothing is written."""
    imports, body = split_frontmatter(source.frontmatter)
    shell = layout_shell(source_path or str(Config.PROJECT_ROOT))
    names = template_names(source.frontmatter, source.props)
    return _MODULE.format(
        layout_header=shell.header,
        module_imports=imports,
        name=function_name(template_path),
        props=props_signature(source.props),
        slot=_SLOT,
        logic=textwrap.indent(body, "    "),
        layout_children=shell.children,
        context_items=context_literal(names),
        template_path=Path(template_path).as_posix(),
        render_wrapper=shell.wrapper,
    )


class LogicGenerator:
    """Writes the Python module of one component into the virtual file system."""

    def __init__(self) -> None:
        self.vfs = VFS()

    def generate(
        self, template_path: str, source: ParserModel, source_path: str | None = None
    ) -> None:
        module = render_module(template_path, source, source_path)
        self.vfs.write(module_path(template_path), module)
