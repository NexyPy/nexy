import ast
import re
import textwrap
from pathlib import Path
from typing import *  # noqa: F403

from nexy.core.config import Config
from nexy.core.models import ParserModel
from nexy.core.string import StringTransform
from nexy.helpers.fs.vfs import VFS
from nexy.modules.routers.fbrouter.layout import RouteLayout


class LogicGenerator:
    def __init__(self) -> None:
        self.func_name: str = ""
        self.source: ParserModel | None = None
        self.output: str = ""
        self.template_path: str = ""
        self.FRONTMATTER: str = ""
        self._string_transform = StringTransform()
        self.source_path: str | None = None
        self.vfs = VFS()

    def generate(
        self, template_path: str, source: ParserModel, source_path: str | None = None
    ) -> None:
        self.source = source
        self.source_path = source_path
        self.template_path = Path(template_path).as_posix()
        tp = Path(template_path)
        stem = tp.stem
        raw_name = self._string_transform.get_component_name(stem)

        self.func_name = re.sub(r"[^a-zA-Z0-9_]", "_", raw_name)

        self.output = tp.with_suffix(".py").as_posix()

        self.FRONTMATTER = self._component_model()
        self.vfs.write(self.output, self.FRONTMATTER)

    def _resolve_props(self) -> str:
        if self.source is None:
            raise RuntimeError("LogicGenerator.source is not set")
        if not self.source.props:
            return ""
        return ", ".join([f"{p.name}: {p.type} = {p.default}" for p in self.source.props])

    def _component_model(self) -> str:
        if self.source is None:
            raise RuntimeError("LogicGenerator.source is not set")

        module_imports = ""
        function_body = self.source.frontmatter
        try:
            tree = ast.parse(self.source.frontmatter)
            import_nodes: list[ast.stmt] = []
            body_nodes: list[ast.stmt] = []
            for node in tree.body:
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_nodes.append(node)
                else:
                    body_nodes.append(node)
            if import_nodes:
                module_imports = ast.unparse(ast.Module(body=import_nodes, type_ignores=[]))
                function_body = (
                    ast.unparse(ast.Module(body=body_nodes, type_ignores=[])) if body_nodes else ""
                )
        except SyntaxError:
            pass

        logic = textwrap.indent(function_body, "    ")

        use_layout = Config.useRouter is None
        source_path = self.source_path or str(Config.PROJECT_ROOT)
        is_layout_file = (
            Path(source_path).name.lower() in Config.LAYOUT_FILE_NAMES if use_layout else False
        )
        layout_import = (
            RouteLayout.get_closest_import(source_path, is_layout=is_layout_file)
            if use_layout
            else None
        )

        from nexy.modules.compiler.document_shell import (
            CSR_SHELL_HEADER,
            CSR_SHELL_RENDER,
            is_route_file,
        )

        layout_header = ""
        render_wrapper = "rendered"
        layout_children = ""

        if layout_import:
            layout_header = (
                f"try:\n"
                f"    from {layout_import} import Layout as __Layout\n"
                f"except ImportError:\n"
                f"    def __Layout(children: str = '', **kwargs) -> str:\n"
                f"        return '<div data-nexy-error=\"Layout not available\"></div>'\n"
            )
            render_wrapper = "str(__Layout(children=rendered))"
        elif use_layout and not is_layout_file and is_route_file(source_path):
            layout_header = CSR_SHELL_HEADER
            render_wrapper = CSR_SHELL_RENDER

        if is_layout_file:
            layout_children = (
                f"""children = f"<nslot  style='display:contents;'>{"{children}"}</nslot>" """
            )

        props = self._resolve_props()

        idents = set()
        try:
            tree = ast.parse(self.source.frontmatter)
            for node in tree.body:
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name != "*":
                            idents.add(alias.asname if alias.asname else alias.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        idents.add(alias.asname if alias.asname else alias.name.split(".")[0])
                elif isinstance(node, ast.Assign):
                    for t in node.targets:
                        if isinstance(t, ast.Name):
                            idents.add(t.id)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    idents.add(node.name)
        except SyntaxError:
            pass

        for p in self.source.props:
            idents.add(p.name)
        names = [n for n in idents if not n.startswith("_")]

        context_items = ", ".join([f'"{n}": {n}' for n in names])
        slot = (
            "Slot = caller if (locals().get('caller') and callable(caller)) else "
            "(lambda: children if locals().get('children') else '')"
        )

        extras = "'trans': __trans, '__locale': __current_locale.get()"
        if context_items != "":
            context_items += f", 'Slot': Slot, {extras}"
        else:
            context_items = f"'Slot': Slot, {extras}"

        t_local = "trans = __trans\n    t = __trans"

        existing_props = [p.name for p in self.source.props]

        extra_props = []
        if "caller" not in existing_props:
            extra_props.append("caller: Any = None")
        if "children" not in existing_props:
            extra_props.append("children: str = ''")

        if extra_props:
            if props != "":
                props += ", " + ", ".join(extra_props)
            else:
                props = ", ".join(extra_props)

        return f"""from typing import *
from fastapi import *
from pathlib import Path as __Path
from nexy import Template as __Template
from nexy.modules.i18n.core import current_locale as __current_locale
from nexy.modules.i18n.core import trans as __trans
from nexy.helpers.imports.component_import import _Import as __Import
from nexy.modules.routers.actions.store import ACTIONS_STORE as __ACTIONS_STORE
from jinja2 import Template as __JinjaTemplate
NexyElement = Union[callable, __JinjaTemplate]
{layout_header}
{module_imports}
def {self.func_name}({props}) -> str:
    {slot}
    {t_local}
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
    rendered = str(__Template().render("{self.template_path}", context))
    return {render_wrapper}
"""
