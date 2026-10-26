"""The text of the Python and HTML a framework route compiles to."""

from __future__ import annotations

from nexy.modules.frontend.layout_chain import layout_key

MODULE_IMPORTS = (
    "from typing import *\n"
    "from fastapi import *\n"
    "import json as __json\n"
    "from pathlib import Path as __Path\n"
    "from nexy import Template as __Template\n"
    "from jinja2 import Template as __JinjaTemplate\n"
    "NexyElement = Union[callable, __JinjaTemplate]\n"
)


def ncc_template(
    framework: str, rel_glob: str, key_hash: str, symbol: str, layouts: list[str] | None = None
) -> str:
    """Build the <ncc> hydrating tag served as the route's HTML template."""
    layouts_attr = ""
    if layouts:
        layouts_attr = f' data-nexy-layouts="{",".join(layout_key(p) for p in layouts)}"'
    return (
        "<ncc"
        ' id="{{ __nexy_mount_id }}"'
        f' data-nexy-fw="{framework}"'
        "{% if __nexy_is_prod is false %}"
        f' data-nexy-path="{rel_glob}"'
        "{% endif %}"
        f' data-nexy-key="{key_hash}"'
        f"{layouts_attr}"
        ' style="display: contents;"'
        f' data-nexy-symbol="{symbol}"'
        ' data-nexy-props="{{ __nexy_props | e }}">'
        "{{ __nexy_ssr_content | safe }}"
        "</ncc>"
    )


def module_signature(layout_header: str, func_name: str, py_path: str, symbol: str) -> str:
    return (
        f"{layout_header}\n"
        f"def {func_name}("
        "caller: Any = None, "
        "children: str = '', "
        "**kwargs: Any"
        ") -> str:\n"
        "    if caller is not None and callable(caller):\n"
        "        Slot = caller\n"
        "    else:\n"
        "        Slot = lambda: children if children else ''\n"
        "    __is_prod = __Path('__nexy__/nexy.prod').is_file()\n"
        "    __mount_id = 'nexy-' + __import__('hashlib').md5("
        f"(__Path({py_path!r}).as_posix() + '|{symbol}|1').encode()).hexdigest()[:10]\n"
        "    # SSR static HTML: populated by SSG build, empty in dev\n"
        "    __ssr = ''\n"
    )


_DOCUMENT_MODULE = """\
from typing import Any
from nexy.modules.runtime.csr_document import render_document as __render_document


def {func_name}(
    caller: Any = None,
    children: str = "",
    **kwargs: Any,
) -> str:
    return __render_document(
        page_file={page_file!r},
        page_key={page_key!r},
        layouts={layouts!r},
        layout_keys={layout_keys!r},
        props=kwargs,
        static_stem={static_stem!r},
        dynamic={dynamic!r},
    )


{func_name}.__nexy_blocking__ = True  # waits on Node: rendered off the event loop
"""


def document_module(
    func_name: str,
    *,
    page_file: str,
    layouts: list[str],
    static_stem: str,
    dynamic: bool,
) -> str:
    """Python module whose component returns the full document rendered by Node."""
    layout_keys = [layout_key(layout) for layout in layouts]
    return _DOCUMENT_MODULE.format(
        func_name=func_name,
        page_file=page_file,
        page_key=layout_key(page_file),
        layouts=layouts,
        layout_keys=layout_keys,
        static_stem=static_stem,
        dynamic=dynamic,
    )


def ssg_module_lines(ssg_static: str) -> str:
    return (
        f"        __ssg_file = __Path({ssg_static!r})\n"
        "        try:\n"
        "            __ssr = __ssg_file.read_text(encoding='utf-8')\n"
        "        except OSError:\n"
        "            __ssr = ''\n"
    )


def render_module_tail(template_abs_ref: str, render_wrapper: str) -> str:
    return (
        "    context = {\n"
        "        '__nexy_mount_id': __mount_id,\n"
        "        '__nexy_ssr_content': __ssr,\n"
        "        '__nexy_is_prod': __is_prod,\n"
        "        '__nexy_props': __json.dumps(kwargs),\n"
        "        'Slot': Slot,\n"
        "        'children': children,\n"
        "    }\n"
        "    context.update(kwargs)\n"
        f"    rendered = str(__Template().render({template_abs_ref!r}, context))\n"
        f"    return {render_wrapper}\n"
    )
