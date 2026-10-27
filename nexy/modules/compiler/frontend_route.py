"""Compiles framework route files (.tsx/.vue/.svelte/.mdx) into Python wrapper modules."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nexy.core.config import Config
from nexy.core.framework_rules import as_list
from nexy.helpers.fs.vfs import VFS
from nexy.helpers.fs.vfs_packages import write_package_inits
from nexy.modules.compiler.document_shell import is_route_file, layout_parts
from nexy.modules.compiler.frontend_symbols import (
    detect_mdx_framework,
    glob_ref,
    resolve_symbol,
    ssg_static_path,
)
from nexy.modules.compiler.frontend_templates import (
    MODULE_IMPORTS,
    document_module,
    module_signature,
    ncc_template,
    render_module_tail,
    ssg_module_lines,
)
from nexy.modules.compiler.route_paths import RoutePaths, route_paths
from nexy.modules.frontend.layout_chain import framework_layout_chain
from nexy.modules.routers.fbrouter.layout import RouteLayout

_EXT_TO_FW: dict[str, str] = {
    ".mdx": "react",
    ".tsx": "react",
    ".vue": "vue",
    ".svelte": "svelte",
}

# Route and root-layout extensions of each framework whose root layout owns the document.
_DOCUMENT_EXTENSIONS = {
    "react": (".tsx", ".jsx"),
    "solid": (".tsx", ".jsx"),
    "preact": (".tsx", ".jsx"),
    "vue": (".vue",),
    "svelte": (".svelte",),
}


def _owns_document(ext: str, layouts: list[str]) -> bool:
    """True when the root layout of a client-routed project owns ``<html>`` (any framework)."""
    if not Config.useCSR or not layouts:
        return False
    use_ff = as_list(Config.useFF)
    name = getattr(use_ff[0], "name", "").lower() if use_ff else ""
    extensions = _DOCUMENT_EXTENSIONS.get(name, ())
    if ext not in extensions:
        return False
    root = f"/{Path(Config.ROUTER_PATH).as_posix().strip('/')}"
    return layouts[0] in tuple(f"{root}/layout{extension}" for extension in extensions)


@dataclass(frozen=True)
class RoutePlan:
    """Everything the generated files of one framework route are made from."""

    paths: RoutePaths
    ext: str
    framework: str
    layouts: list[str]
    rel_glob: str
    key_hash: str
    symbol: str

    @property
    def owns_document(self) -> bool:
        return _owns_document(self.ext, self.layouts)

    def template(self) -> str:
        return ncc_template(self.framework, self.rel_glob, self.key_hash, self.symbol, self.layouts)


def _layout_header(source: str, has_framework_layouts: bool) -> tuple[str, str]:
    """(header, render expression): the closest layout, else the document shell for a route.

    Every web view must be wrapped by a layout to own the HTML document
    (<!DOCTYPE html>/<html>/<head>/<body>). A user layout always wins; otherwise Nexy supplies
    the minimal document shell carrying Vite tags.
    """
    is_layout = Path(source).name.lower() in Config.LAYOUT_FILE_NAMES
    layout = RouteLayout.get_closest_import(
        source, is_layout=is_layout, nexy_only=has_framework_layouts
    )
    return layout_parts(layout, fallback_shell=is_route_file(source))


def _classic_module(plan: RoutePlan) -> str:
    """The module of a route that is wrapped by a Nexy layout and mounts its component."""
    header, wrapper = _layout_header(plan.paths.source, bool(plan.layouts))
    ssg = ssg_static_path(plan.rel_glob, plan.framework, plan.symbol)
    # The SSG snapshot has no layouts around the page; mounting client-side avoids a hydration
    # mismatch.
    prerendered = "        pass\n" if plan.layouts else ssg_module_lines(ssg)
    return (
        MODULE_IMPORTS
        + module_signature(header, plan.paths.component, plan.paths.py_path, plan.symbol)
        + f"    __ext = {plan.ext!r}\n"
        + "    if __is_prod:\n"
        + prerendered
        + render_module_tail(plan.paths.html_path, wrapper)
    )


def _document_source(plan: RoutePlan) -> str:
    return document_module(
        plan.paths.component,
        page_file=plan.rel_glob,
        layouts=plan.layouts,
        static_stem=plan.rel_glob[: -len(plan.ext)],
        dynamic="{" in plan.paths.pathname,
    )


class FrontendRouteCompiler:
    """Compiles framework route files (.tsx/.vue/.svelte) into Python wrapper modules.

    Each framework route generates two outputs in the VFS:
      - A .py module (same layout as a compiled .nexy) with a component function returning HTML
        (SSR static content when available, plus a self-mounting <ncc> hydration container).
      - A .html file containing the rendered Jinja2 template. Since framework routes have no
        Jinja2 content, the HTML is the <ncc> tag itself - rendered as-is.
    """

    def __init__(self) -> None:
        self.config = Config()
        self.vfs = VFS()

    @staticmethod
    def _detect_framework(src: Path, label: str) -> tuple[str, str]:
        """(ext, framework) for a route source, rejecting unknown extensions."""
        ext = src.suffix.lower()
        if ext not in _EXT_TO_FW:
            raise ValueError(f"FrontendRouteCompiler: unsupported extension {ext!r} for {label}")
        return ext, detect_mdx_framework(src) if ext == ".mdx" else _EXT_TO_FW[ext]

    def _plan(self, src: Path, label: str) -> RoutePlan:
        ext, framework = self._detect_framework(src, label)
        posix = src.as_posix()
        rel_glob, key_hash = glob_ref(src, posix)
        return RoutePlan(
            paths=route_paths(posix, src.stem),
            ext=ext,
            framework=framework,
            layouts=framework_layout_chain(src, Path(Config.ROUTER_PATH)),
            rel_glob=rel_glob,
            key_hash=key_hash,
            symbol=resolve_symbol(src, ext, src.stem),
        )

    def compile(self, *, input: str) -> None:
        plan = self._plan(Path(input), input)
        module = _document_source(plan) if plan.owns_document else _classic_module(plan)
        self.vfs.write(plan.paths.py_path, module)
        self.vfs.write(plan.paths.html_path, plan.template())
        write_package_inits(self.vfs, plan.paths.package)
        self._write_route_meta(plan)

    def _write_route_meta(self, plan: RoutePlan) -> None:
        """Store a small metadata companion file for FBRouter to inspect if needed."""
        paths = plan.paths
        meta: dict[str, Any] = {
            "framework": plan.framework,
            "ext": plan.ext,
            "component_name": paths.component,
            "func_name": paths.component,
            "py_path": paths.py_path,
            "html_path": paths.html_path,
            "pathname": paths.pathname,
            "symbol": plan.symbol,
            "source": paths.source,
            "global_src": plan.rel_glob,
            "key_hash": plan.key_hash,
        }
        self.vfs.write(paths.meta_path, json.dumps(meta, ensure_ascii=False))


__all__ = ["FrontendRouteCompiler", "_EXT_TO_FW"]
