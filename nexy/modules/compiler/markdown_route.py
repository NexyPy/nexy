"""Compiles markdown content routes (.md) into Python wrapper modules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexy.core.config import Config
from nexy.helpers.fs.vfs import VFS
from nexy.helpers.fs.vfs_packages import write_package_inits
from nexy.modules.compiler.document_shell import layout_parts
from nexy.modules.compiler.route_paths import RoutePaths, route_paths
from nexy.modules.routers.fbrouter.layout import RouteLayout

_IMPORTS = (
    "from typing import *\n"
    "from pathlib import Path as __Path\n"
    "from nexy.modules.runtime.markdown import render_markdown as __render_markdown\n"
    "from nexy.modules.runtime.markdown import inject_heading_ids as __inject_heading_ids\n"
)
_SIGNATURE = "caller: Any = None, children: str = '', **kwargs: Any"
_BODY = (
    "    try:\n"
    "        __content = __Path(__src).read_text(encoding='utf-8')\n"
    "    except OSError:\n"
    "        __content = ''\n"
    "    rendered = __inject_heading_ids(__render_markdown(__content))\n"
    "    try:\n"
    "        from nexy.hooks import _toc_storage as __toc_store\n"
    "        __toc_store.set(rendered)\n"
    "    except Exception:\n"
    "        pass\n"
)


def module_source(component: str, layout_header: str, render_wrapper: str, source: str) -> str:
    """The Python module that renders the file *source* inside its layout."""
    return (
        f"{_IMPORTS}{layout_header}\n"
        f"def {component}({_SIGNATURE}) -> str:\n"
        f"    __src = {source!r}\n"
        f"{_BODY}"
        f"    return {render_wrapper}\n"
    )


def relative_to_project(src: Path) -> str:
    """*src* relative to the working directory; outside it, without the leading slash."""
    try:
        return src.resolve().relative_to(Path.cwd()).as_posix()
    except ValueError:
        return src.as_posix().lstrip("/")


class MarkdownRouteCompiler:
    """Compiles markdown content routes (.md) into Python wrapper modules.

    A .md route is pure content: it is rendered to HTML with cmarkgfm at request time, heading
    ids and a TOC are derived, then the body is wrapped by the nearest layout.* (layout.nexy,
    layout.tsx, ...).
    """

    def __init__(self) -> None:
        self.config = Config()
        self.vfs = VFS()

    def compile(self, *, input: str) -> None:
        src = Path(input)
        extension = src.suffix.lower()
        if extension != ".md":
            raise ValueError(
                f"MarkdownRouteCompiler: unsupported extension {extension!r} for {input}"
            )
        paths = route_paths(src.as_posix(), src.stem)
        layout = RouteLayout.get_closest_import(paths.source, is_layout=False)
        header, wrapper = layout_parts(layout, fallback_shell=True)
        project_path = relative_to_project(src)
        self.vfs.write(paths.py_path, module_source(paths.component, header, wrapper, project_path))
        write_package_inits(self.vfs, paths.package)
        self._write_meta(paths, extension, project_path)

    def _write_meta(self, paths: RoutePaths, extension: str, project_path: str) -> None:
        meta: dict[str, Any] = {
            "kind": "markdown",
            "ext": extension,
            "component_name": paths.component,
            "func_name": paths.component,
            "py_path": paths.py_path,
            "pathname": paths.pathname,
            "source": paths.source,
            "global_src": project_path,
        }
        self.vfs.write(paths.meta_path, json.dumps(meta, ensure_ascii=False))


__all__ = ["MarkdownRouteCompiler"]
