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
    # Add actions to context (both function and path)
    __actions_dict = {{}}
    __actions_path_dict = {{}}
    for __func_id, __handler in __ACTIONS_STORE.registry.items():
        __name = __func_id.split('.')[-1]
        __actions_dict[__name] = __handler
        __actions_path_dict[__name] = __ACTIONS_STORE.path_map.get(__func_id, '')
    context = {{{context_items}}}
    context.update(__actions_dict)
    context['__actions'] = __actions_dict
    context['__actions_path'] = __actions_path_dict
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


class LogicGenerator:
    """Writes the Python module of one component into the virtual file system."""

    def __init__(self) -> None:
        self.func_name: str = ""
        self.source: ParserModel | None = None
        self.output: str = ""
        self.template_path: str = ""
        self.FRONTMATTER: str = ""
        self.source_path: str | None = None
        self.vfs = VFS()

    def generate(
        self, template_path: str, source: ParserModel, source_path: str | None = None
    ) -> None:
        self.source = source
        self.source_path = source_path
        self.template_path = Path(template_path).as_posix()
        self.func_name = function_name(template_path)
        self.output = Path(template_path).with_suffix(".py").as_posix()
        self.FRONTMATTER = self._component_model()
        self.vfs.write(self.output, self.FRONTMATTER)

    def _resolve_props(self) -> str:
        if self.source is None:
            raise RuntimeError("LogicGenerator.source is not set")
        return props_signature(self.source.props)

    def _component_model(self) -> str:
        if self.source is None:
            raise RuntimeError("LogicGenerator.source is not set")
        imports, body = split_imports(self.source.frontmatter)
        shell = layout_shell(self.source_path or str(Config.PROJECT_ROOT))
        names = template_names(self.source.frontmatter, self.source.props)
        return _MODULE.format(
            layout_header=shell.header,
            module_imports=imports,
            name=self.func_name,
            props=props_signature(self.source.props),
            slot=_SLOT,
            logic=textwrap.indent(body, "    "),
            layout_children=shell.children,
            context_items=context_literal(names),
            template_path=self.template_path,
            render_wrapper=shell.wrapper,
        )
