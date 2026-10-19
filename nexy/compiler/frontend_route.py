import hashlib
import json as _json_mod
import re
from pathlib import Path
from typing import Any

from nexy.core.config import Config
from nexy.core.string import Pathname, StringTransform
from nexy.routers.fbrouter.layout import RouteLayout
from nexy.utils.fs.vfs import VFS

_EXT_TO_FW: dict[str, str] = {
    ".mdx": "react",
    ".tsx": "react",
    ".vue": "vue",
    ".svelte": "svelte",
}

_TSX_EXPORT_RE = re.compile(
    r"export\s+(?:default\s+)?(?:function|const|class|let|var)\s+([A-Za-z_$][\w$]*)"
)
_TSX_EXPORT_DEFAULT_RE = re.compile(r"export\s+default\s")

_MODULE_IMPORTS = (
    "from typing import *\n"
    "from fastapi import *\n"
    "import json as __json\n"
    "from pathlib import Path as __Path\n"
    "from nexy import Template as __Template\n"
    "from nexy.i18n.core import current_locale as __current_locale\n"
    "from nexy.i18n.core import trans as __trans\n"
    "from jinja2 import Template as __JinjaTemplate\n"
    "NexyElement = Union[callable, __JinjaTemplate]\n"
)


def _detect_mdx_framework(src: Path) -> str:
    """Auto-detect React vs Preact for an .mdx file by inspecting imports."""
    try:
        content = src.read_text(encoding="utf-8")
    except OSError:
        return "react"
    if "from 'preact'" in content or 'from "preact"' in content:
        return "preact"
    return "react"


def _resolve_tsx_export_symbol(src: Path, fallback_stem: str) -> str:
    """Resolve the actual TSX export symbol for a React/Preact route file.

    Priority:
      1. `export default X` -> "default"
      2. First `export function|const|class X` -> "X"
      3. Fallback: PascalCase of file stem (card.tsx -> Card), else "Default"
    """
    try:
        content = src.read_text(encoding="utf-8")
    except OSError:
        content = ""

    if _TSX_EXPORT_DEFAULT_RE.search(content):
        return "default"
    match = _TSX_EXPORT_RE.search(content)
    if match:
        return match.group(1)

    stem = fallback_stem.strip()
    if stem:
        cleaned = re.sub(r"[^a-zA-Z0-9_$]+", "", stem)
        if cleaned:
            first = cleaned[0].upper() if cleaned[0].isalpha() else cleaned[0]
            rest = cleaned[1:] if len(cleaned) > 1 else ""
            return f"{first}{rest}"
    return "Default"


def _resolve_symbol(src: Path, ext: str, stem: str) -> str:
    """Pick the client-side export symbol to hydrate for this route file."""
    if ext in (".vue", ".svelte"):
        return "default"
    if ext == ".mdx":
        return "default"
    return _resolve_tsx_export_symbol(src, stem)


def _glob_ref(src: Path, posix_src: str) -> tuple[str, str]:
    """(import.meta.glob path, md5 key) for one framework route source."""
    try:
        cwd = Path.cwd()
        rel_from_cwd = "/" + src.resolve().relative_to(cwd).as_posix().lstrip("/")
    except ValueError:
        rel_from_cwd = "/" + posix_src.lstrip("/")
    key_hash = hashlib.md5(rel_from_cwd.encode("utf-8")).hexdigest()
    return rel_from_cwd, key_hash


def _ssg_static_path(rel_glob: str, framework: str, symbol: str) -> str:
    """SSG HTML path: same convention as NexyClientComponent._get_static_content.

    Vue/Svelte: __nexy__/client/static/<path>.html  (default export)
    TSX (React):  __nexy__/client/static/<path-without-tsx>.Default.html
    """
    if framework in ("vue", "svelte"):
        rel_path_html = rel_glob + ".html"
    else:
        export_name = "Default" if symbol == "default" else symbol
        rel_path_html = rel_glob.replace(".tsx", "").replace(".mdx", "") + f".{export_name}.html"
    return f"__nexy__/client/static{rel_path_html}"


def _ncc_template(framework: str, rel_glob: str, key_hash: str, symbol: str) -> str:
    """Build the <ncc> hydrating tag served as the route's HTML template."""
    return (
        "<ncc"
        ' id="{{ __nexy_mount_id }}"'
        f' data-nexy-fw="{framework}"'
        "{% if __nexy_is_prod is false %}"
        f' data-nexy-path="{rel_glob}"'
        "{% endif %}"
        f' data-nexy-key="{key_hash}"'
        ' style="display: contents;"'
        f' data-nexy-symbol="{symbol}"'
        ' data-nexy-props="{{ __nexy_props | e }}">'
        "{{ __nexy_ssr_content | safe }}"
        "</ncc>"
    )


def _module_signature(layout_header: str, func_name: str, py_path: str, symbol: str) -> str:
    return (
        f"{layout_header}\n"
        f"def {func_name}("
        "__locale_info: Any = None, "
        "trans: Any = None, "
        "caller: Any = None, "
        "children: str = '', "
        "**kwargs: Any"
        ") -> str:\n"
        "    t = __trans\n"
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


def _layout_wrapper(posix_src: str) -> tuple[str, str]:
    """(layout_header, render_wrapper) for the closest parent layout import."""
    is_layout_file = Path(posix_src).name.lower() in Config.LAYOUT_FILE_NAMES
    layout_import = RouteLayout.get_closest_import(posix_src, is_layout=is_layout_file)
    if not layout_import:
        return "", "rendered"
    layout_header = (
        f"try:\n"
        f"    from {layout_import} import Layout as __Layout\n"
        f"except ImportError:\n"
        f"    def __Layout(children: str = '', **kwargs) -> str:\n"
        f"        return '<div data-nexy-error=\"Layout not available\"></div>'\n"
    )
    return layout_header, "str(__Layout(children=rendered))"


def _reject_locale_suffix(src: Path, ext: str, locales: list[str]) -> None:
    """Block locale-suffixed framework route files (about.fr.tsx, guide.en.vue…).

    Only .nexy and .mdx files support locale variants through FBR's
    basename.locale.ext convention. For framework components, use
    nexy.i18n APIs inside the component instead. .mdx locale variants remain
    LEGACY-supported through the frontmatter i18n pipeline.
    """
    stem = src.stem
    if "." not in stem or not locales:
        return

    _base, maybe_locale = stem.rsplit(".", 1)
    if maybe_locale in locales and ext != ".mdx":
        from nexy.errors import NexyCompileError

        locales_hint = ", ".join(sorted(locales))
        raise NexyCompileError(
            source_path=str(src.resolve()),
            message=(
                f"Locale suffix '.{maybe_locale}' is not supported on "
                f"{ext!r} route files. For i18n pages, use "
                f"*.nexy or *.mdx locale variants "
                f"(e.g. page.{maybe_locale}.nexy) or handle locale "
                f"switching inside the component itself "
                f"(available locales: {locales_hint})."
            ),
        )


def _route_module_paths(posix_src: str, stem: str) -> dict[str, Any]:
    """Derive the generated module paths, component name and URL pathname."""
    mapped = StringTransform().normalize_route_path_for_namespace(posix_src)
    full_namespaced = f"{Config.NAMESPACE}{mapped}"

    component_name = StringTransform().get_component_name(stem) or "Index"

    router_path = Path(Config.ROUTER_PATH).as_posix()
    cleaned = (
        posix_src.replace(f"{Config.NAMESPACE}{router_path}", "")
        .replace(router_path, "")
        .split(".")[0]
    )
    return {
        "full_namespaced": full_namespaced,
        "py_path": Path(full_namespaced).with_suffix(".py").as_posix(),
        "html_path": Path(full_namespaced).with_suffix(".html").as_posix(),
        "component_name": component_name,
        "pathname": Pathname(cleaned).process(),
    }


class FrontendRouteCompiler:
    """Compiles framework route files (.tsx/.vue/.svelte) into Python wrapper modules.

    Each framework route generates two outputs in the VFS:
      - A .py module (same layout as a compiled .nexy) with a component function
        returning HTML (SSR static content when available, plus a self-mounting <ncc>
        hydration container).
      - A .html file containing the rendered Jinja2 template. Since framework routes
        have no Jinja2 content, the HTML is the <ncc> tag itself - rendered as-is.
    """

    def __init__(self) -> None:
        self.config = Config()
        self.string_transform = StringTransform()
        self.vfs = VFS()

    def _generate_init(self, directory: str) -> None:
        """Write empty __init__.py for every ancestor of a compiled module.

        Mirror of Generator._generate_init so framework routes in
        subdirectories (demo/[slug].tsx -> demo/slug_catch_all.py) are
        importable as Python packages.
        """
        parts = directory.replace("\\", "/").split("/")
        for i in range(1, len(parts) + 1):
            sub = "/".join(parts[:i])
            init_file = f"{sub}/__init__.py"
            if not self.vfs.exists(init_file):
                self.vfs.write(init_file, "")

    def _detect_framework(self, src: Path, label: str) -> tuple[str, str]:
        """(ext, framework) for a route source, rejecting unknown extensions."""
        ext = src.suffix.lower()
        if ext not in _EXT_TO_FW:
            raise ValueError(f"FrontendRouteCompiler: unsupported extension {ext!r} for {label}")
        framework = _EXT_TO_FW[ext]
        if ext == ".mdx":
            framework = _detect_mdx_framework(src)
        return ext, framework

    def compile(self, *, input: str) -> None:
        src = Path(input)
        ext, framework = self._detect_framework(src, input)
        _reject_locale_suffix(src, ext, self.config.useLocales or [])

        posix_src = src.as_posix()
        stem = src.stem
        paths = _route_module_paths(posix_src, stem)
        py_path = paths["py_path"]
        html_path = paths["html_path"]
        template_abs_ref = html_path

        layout_header, render_wrapper = _layout_wrapper(posix_src)
        rel_glob, key_hash = _glob_ref(src, posix_src)
        symbol = _resolve_symbol(src, ext, stem)
        ssg_static = _ssg_static_path(rel_glob, framework, symbol)

        module_body = _MODULE_IMPORTS + _module_signature(
            layout_header, paths["component_name"], py_path, symbol
        )
        module_body += "    __ext = " + repr(ext) + "\n"
        module_body += "    if __is_prod:\n"
        module_body += _ssg_module_lines(ssg_static)
        module_body += _render_module_tail(template_abs_ref, render_wrapper)

        template_html = _ncc_template(framework, rel_glob, key_hash, symbol)

        self.vfs.write(py_path, module_body)
        self.vfs.write(html_path, template_html)
        self._generate_init(Path(paths["full_namespaced"]).parent.as_posix())

        self._write_route_meta(paths, posix_src, symbol, rel_glob, key_hash, framework, ext)

    def _write_route_meta(
        self,
        paths: dict[str, Any],
        posix_src: str,
        symbol: str,
        rel_glob: str,
        key_hash: str,
        framework: str,
        ext: str,
    ) -> None:
        """Store a small metadata companion file for FBRouter to inspect if needed."""
        meta: dict[str, Any] = {
            "framework": framework,
            "ext": ext,
            "component_name": paths["component_name"],
            "func_name": paths["component_name"],
            "py_path": paths["py_path"],
            "html_path": paths["html_path"],
            "pathname": paths["pathname"],
            "symbol": symbol,
            "source": posix_src,
            "global_src": rel_glob,
            "key_hash": key_hash,
        }
        meta_path = Path(paths["full_namespaced"]).with_suffix(".meta.json").as_posix()
        self.vfs.write(meta_path, _json_mod.dumps(meta, ensure_ascii=False))


def _ssg_module_lines(ssg_static: str) -> str:
    return (
        f"        __ssg_file = __Path({ssg_static!r})\n"
        "        try:\n"
        "            __ssr = __ssg_file.read_text(encoding='utf-8')\n"
        "        except OSError:\n"
        "            __ssr = ''\n"
    )


def _render_module_tail(template_abs_ref: str, render_wrapper: str) -> str:
    return (
        "    context = {\n"
        "        '__nexy_mount_id': __mount_id,\n"
        "        '__nexy_ssr_content': __ssr,\n"
        "        '__nexy_is_prod': __is_prod,\n"
        "        '__nexy_props': __json.dumps(kwargs),\n"
        "        'Slot': Slot,\n"
        "        'children': children,\n"
        "        'trans': __trans,\n"
        "        '__locale': __current_locale.get(),\n"
        "    }\n"
        "    context.update(kwargs)\n"
        f"    rendered = str(__Template().render({template_abs_ref!r}, context))\n"
        f"    return {render_wrapper}\n"
    )


__all__ = ["FrontendRouteCompiler", "_EXT_TO_FW"]
