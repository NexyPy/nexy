from pathlib import Path
from typing import Any

from nexy.core.config import Config
from nexy.core.string import Pathname, StringTransform
from nexy.routers.fbrouter.layout import RouteLayout
from nexy.utils.fs.vfs import VFS


class MarkdownRouteCompiler:
    """Compiles markdown content routes (.md) into Python wrapper modules.

    A .md route is pure content: it is rendered to HTML with cmarkgfm at
    request time, heading ids and a TOC are derived, then the body is
    wrapped by the nearest layout.* (layout.nexy, layout.tsx, ...).
    """

    def __init__(self) -> None:
        self.config = Config()
        self.string_transform = StringTransform()
        self.vfs = VFS()

    def _generate_init(self, directory: str) -> None:
        """Write empty __init__.py for every ancestor of a compiled module.

        Mirror of Generator._generate_init so markdown routes in
        subdirectories are importable as Python packages.
        """
        parts = directory.replace("\\", "/").split("/")
        for i in range(1, len(parts) + 1):
            sub = "/".join(parts[:i])
            init_file = f"{sub}/__init__.py"
            if not self.vfs.exists(init_file):
                self.vfs.write(init_file, "")

    def compile(self, *, input: str) -> None:  # noqa: A002 - match existing Compiler API
        src = Path(input)
        ext = src.suffix.lower()
        if ext != ".md":
            raise ValueError(f"MarkdownRouteCompiler: unsupported extension {ext!r} for {input}")

        posix_src = src.as_posix()
        mapped = self.string_transform.normalize_route_path_for_namespace(posix_src)
        full_namespaced = f"{Config.NAMESPACE}{mapped}"

        py_path = Path(full_namespaced).with_suffix(".py").as_posix()

        # Component name = matches FBRouter._scan_modules lookup convention
        # (get_component_name), so [slug].md -> Slug_catch_all.
        stem = src.stem
        # Strip locale suffix (.fr / .en / …) if present and matched by useLocales
        locale: str | None = None
        locales = self.config.useLocales or []
        if "." in stem and locales:
            base, maybe_locale = stem.rsplit(".", 1)
            if maybe_locale in locales:
                locale = maybe_locale
                stem = base
        component_name = self.string_transform.get_component_name(stem) or "Index"
        func_name = component_name

        # Resolve URL path for the route (same rules as FBR)
        router_path = Path(Config.ROUTER_PATH).as_posix()
        cleaned = (
            posix_src.replace(f"{Config.NAMESPACE}{router_path}", "")
            .replace(router_path, "")
            .split(".")[0]
        )
        _pathname = Pathname(cleaned).process()

        # Layout - same discovery mechanism as .nexy / framework routes
        layout_import = RouteLayout.get_closest_import(posix_src, is_layout=False)

        layout_header = ""
        render_wrapper = "rendered"
        if layout_import:
            layout_header = (
                f"try:\n"
                f"    from {layout_import} import Layout as __Layout\n"
                f"except ImportError:\n"
                f"    def __Layout(children: str = '', **kwargs) -> str:\n"
                f"        return '<div data-nexy-error=\"Layout not available\"></div>'\n"
            )
            render_wrapper = "str(__Layout(children=rendered))"

        src_abs = src.resolve()
        try:
            cwd = Path.cwd()
            rel_from_cwd = src_abs.relative_to(cwd).as_posix()
        except ValueError:
            rel_from_cwd = src.as_posix().lstrip("/")

        # --- Python wrapper module
        # The wrapper reads the markdown source at request time, renders via
        # cmarkgfm, injects heading ids, publishes the TOC for useToc(), and
        # wraps the body in the nearest layout.
        module_body = (
            "from typing import *\n"
            "from pathlib import Path as __Path\n"
            "from nexy.runtime.markdown import render_markdown as __render_markdown\n"
            "from nexy.runtime.markdown import inject_heading_ids as __inject_heading_ids\n"
            f"{layout_header}\n"
            f"def {func_name}("
            "__locale_info: Any = None, "
            "trans: Any = None, "
            "caller: Any = None, "
            "children: str = '', "
            "**kwargs: Any"
            ") -> str:\n"
            f"    __src = {rel_from_cwd!r}\n"
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
            f"    return {render_wrapper}\n"
        )

        self.vfs.write(py_path, module_body)
        self._generate_init(Path(full_namespaced).parent.as_posix())

        # Tag for downstream users (locale handling)
        meta: dict[str, Any] = {
            "kind": "markdown",
            "ext": ext,
            "component_name": component_name,
            "func_name": func_name,
            "py_path": py_path,
            "pathname": _pathname,
            "source": posix_src,
            "global_src": rel_from_cwd,
        }
        if locale:
            meta["locale"] = locale

        meta_path = Path(full_namespaced).with_suffix(".meta.json").as_posix()
        import json as _json

        self.vfs.write(meta_path, _json.dumps(meta, ensure_ascii=False))
        return None


__all__ = ["MarkdownRouteCompiler"]
