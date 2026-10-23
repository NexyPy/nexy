import asyncio
import functools
import importlib
import inspect
import re
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse

from nexy.core.config import Config
from nexy.core.string import Pathname, StringTransform
from nexy.helpers.common.console import console
from nexy.modules.routers.fbrouter.discovery import RouteDiscovery
from nexy.modules.runtime.cache import REVALIDATE_CACHE

from .dependencies import RouteDependencies
from .middleware import RouteMiddleware
from .validator import RouteValidator

HTTP_METHODS_MAP = {
    "GET": "get",
    "POST": "post",
    "PUT": "put",
    "DELETE": "delete",
    "PATCH": "patch",
    "OPTIONS": "options",
    "HEAD": "head",
}

_FRAMEWORK_ONLY_EXTS = (".tsx", ".vue", ".svelte")
_FRAMEWORK_ROUTE_EXTS = _FRAMEWORK_ONLY_EXTS + (".mdx",)
_UI_ROUTE_EXTS = (".nexy", ".mdx", ".md", ".tsx", ".vue", ".svelte")


def _route_clean_path(path_str: str, locale: str | None) -> str:
    """Strip the router prefix, the locale suffix and the file extension.

    Only the extension (and its locale marker) is removed: dots inside a
    dynamic segment such as ``[...path]`` are part of the route path and must
    survive, so splitting on the first ``.`` is wrong.
    """
    relative = path_str.replace(f"{Config.NAMESPACE}src/routes", "").replace("src/routes", "")
    if locale:
        relative = relative.removesuffix(f".{locale}")
    return relative.rsplit(".", 1)[0]


def _lazy_component(
    import_path: str, comp_name: str, original: Callable[..., str]
) -> Callable[..., str]:
    """Return a wrapper that re-imports the compiled module at call time.

    After the watcher purges the module from sys.modules, the next request
    re-imports fresh code from the VFS - no server restart required for
    .nexy/.md/.mdx edits.
    """

    @functools.wraps(original)
    def _wrapper(**kwargs: Any) -> str:
        module = importlib.import_module(import_path)
        component = getattr(module, comp_name, None) or original
        return component(**kwargs)

    return _wrapper


def _make_locale_handler(
    base_component: Callable[..., str], variants: dict[str, Callable[..., str]]
) -> Callable[..., Any]:
    """Create a locale-aware route handler that dispatches to variant components.

    Uses request.path_params instead of **kwargs to avoid FastAPI
    validation treating kwargs as a required query parameter.
    """

    async def _locale_handler(request: Request) -> str:
        locale: str = request.state.locale
        handler = variants.get(locale, base_component)
        params = _coerce_path_params(inspect.signature(handler), request.path_params)
        return handler(**params)

    _locale_handler.__name__ = base_component.__name__
    _locale_handler.__doc__ = base_component.__doc__
    for attr in ("__nexy_guards__", "__nexy_middlewares__"):
        if hasattr(base_component, attr):
            setattr(_locale_handler, attr, getattr(base_component, attr))

    return _locale_handler


def _coerce_path_params(sig: inspect.Signature, path_params: dict[str, str]) -> dict[str, Any]:
    """Cast dynamic path segments to the types declared in the component signature."""
    coerced: dict[str, Any] = {}
    for name, value in path_params.items():
        param = sig.parameters.get(name)
        ann = param.annotation if param else inspect.Parameter.empty
        if ann is int:
            try:
                coerced[name] = int(value)
            except (TypeError, ValueError):
                coerced[name] = value
        elif ann is float:
            try:
                coerced[name] = float(value)
            except (TypeError, ValueError):
                coerced[name] = value
        else:
            coerced[name] = value
    return coerced


def _stream_body(result: str | Any) -> Any:
    """Wrap a component result into a streaming iterable.

    A generator component yields its chunks as they are produced; a plain
    string is emitted as a single chunk so the response is streamed but the
    output is byte-identical to the previous buffered HTMLResponse.
    """
    if isinstance(result, str):
        return iter([result.encode("utf-8")])
    return (c.encode("utf-8") if isinstance(c, str) else c for c in result)


def _make_request_handler(component: Callable[..., str]) -> Callable[..., Any]:
    """Wrap a UI component with a fixed (request) signature.

    Compiled components expose **kwargs (from locale/props injection);
    FastAPI would otherwise treat `kwargs` as a required query parameter
    and reject the request with 422. Delegating through request.path_params
    keeps the route free of signature validation while still forwarding
    dynamic path segments ([slug] -> {slug}).

    The response is streamed (shell first for generator components) while
    sync `-> str` components keep byte-identical output.
    """

    _sig = inspect.signature(component)

    async def _request_handler(request: Request) -> StreamingResponse:
        params = _coerce_path_params(_sig, request.path_params)
        result = component(**params)
        return StreamingResponse(_stream_body(result), media_type="text/html")

    _request_handler.__name__ = component.__name__
    _request_handler.__doc__ = component.__doc__
    for attr in ("__nexy_guards__", "__nexy_middlewares__"):
        if hasattr(component, attr):
            setattr(_request_handler, attr, getattr(component, attr))

    return _request_handler


def _make_isr_handler(
    component: Callable[..., str], pathname: str, revalidate: int
) -> Callable[..., Any]:
    """Wrap a component with ISR stale-while-revalidate caching.

    Fresh cache serves immediately; a stale (but present) entry serves the
    stale HTML while regeneration runs in the background; a cold miss
    renders once and stores the result.
    """

    _sig = inspect.signature(component)

    def _render() -> str:
        params = _coerce_path_params(_sig, {})
        result = component(**params)
        return result if isinstance(result, str) else "".join(result)

    def _cached_response(body: str | None) -> HTMLResponse:
        header = {
            "cache-control": (f"public, s-maxage={revalidate}, stale-while-revalidate={revalidate}")
        }
        return HTMLResponse(body, headers=header)

    async def _request_handler(request: Request) -> HTMLResponse:  # noqa: ARG001
        cached = REVALIDATE_CACHE.get(pathname)
        stale = cached is not None and REVALIDATE_CACHE.is_stale(pathname)
        if cached is not None and not stale:
            return _cached_response(cached)

        if stale:

            async def _regen() -> None:
                fresh = _render()
                REVALIDATE_CACHE.set(pathname, fresh, revalidate)

            asyncio.create_task(_regen())
            return _cached_response(cached)

        fresh = _render()
        REVALIDATE_CACHE.set(pathname, fresh, revalidate)
        return _cached_response(fresh)

    _request_handler.__name__ = component.__name__
    _request_handler.__doc__ = component.__doc__
    return _request_handler


class FBRouter:
    def __init__(self) -> None:
        self.discovery = RouteDiscovery()
        self.router = APIRouter()
        self.string_transform = StringTransform()
        self.modules_meta: list[dict[str, Any]] = []
        self.error_handlers: list[dict[str, Any]] = []
        self.notfound_handlers: list[dict[str, Any]] = []
        self.loading_handlers: list[dict[str, Any]] = []

        self._load_and_register()

    def register_on(self, app: FastAPI) -> None:
        app.include_router(self.router)
        self._register_error_handlers(app)

    def _register_error_handlers(self, app: FastAPI) -> None:
        """Register notfound/error handlers as scoped exception handlers.

        A handler placed at the routes root (scope "/") handles every
        request; handlers in deeper folders (scope "/blog") only handle
        requests under that prefix. `errors.nexy` maps to 500, `notfound.nexy`
        to 404. The most specific scope wins for each status code.
        """

        def _render(entry: dict[str, Any], status_code: int, exc: Exception) -> HTMLResponse:
            component = getattr(entry["module"], entry["comp"], None)
            if component is None:
                return HTMLResponse(f"<h1>{status_code}</h1>", status_code=status_code)
            from nexy.modules.runtime.importer import install_vfs_importer

            install_vfs_importer()
            try:
                body = component()
            except Exception:
                body = str(exc) or f"<h1>{status_code}</h1>"
            return HTMLResponse(body, status_code=status_code)

        def _pick(handlers: list[dict[str, Any]], scope_prefix: str) -> dict[str, Any] | None:
            candidates = [h for h in handlers if scope_prefix.startswith(h["scope"])]
            if not candidates:
                return None
            return max(candidates, key=lambda h: len(h["scope"]))

        root_handler = next((h for h in self.notfound_handlers if h["scope"] == "/"), None)
        root_error = next((h for h in self.error_handlers if h["scope"] == "/"), None)

        if root_handler:

            @app.exception_handler(status.HTTP_404_NOT_FOUND)
            async def _handle_notfound(request: Request, exc: HTTPException) -> HTMLResponse:
                handler = _pick(self.notfound_handlers, str(request.url.path))
                return _render(handler or root_handler, status.HTTP_404_NOT_FOUND, exc)

        if root_error:

            @app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
            async def _handle_error(request: Request, exc: Exception) -> HTMLResponse:
                handler = _pick(self.error_handlers, str(request.url.path))
                return _render(handler or root_error, status.HTTP_500_INTERNAL_SERVER_ERROR, exc)

    def _load_and_register(self) -> None:
        from nexy.modules.runtime.importer import install_vfs_importer

        install_vfs_importer()
        self._locale_variants: dict[str, dict[str, Callable[..., str]]] = {}
        self._scan_modules()
        self._register_all_routes()

    def _scan_modules(self) -> None:
        available_locales = Config().useLocales or []

        for app_path in self.discovery.scan():
            path_str = app_path.as_posix()
            ext = app_path.suffix.lower()

            name = app_path.name.lower()
            if ext in _FRAMEWORK_ONLY_EXTS and name.count(".") > 1:
                parts = name.rsplit(".", 2)
                pext = "." + parts[2]
                if pext in _FRAMEWORK_ONLY_EXTS and parts[1] in available_locales:
                    console.print(
                        f"  [yellow]WARN[/yellow] {app_path.name}: locale suffix "
                        f"'.{parts[1]}' is not supported on framework route files "
                        f"({', '.join(_FRAMEWORK_ROUTE_EXTS)}). Skipped - use "
                        f".nexy or .mdx locale variants instead, or implement locale "
                        f"logic inside the component via useLocales()."
                    )
                    continue

            locale = None
            if available_locales and name.count(".") > 1:
                parts = name.rsplit(".", 2)
                pext = "." + parts[2]
                if (
                    pext in Config.ROUTE_FILE_EXTENSIONS
                    and parts[1] in available_locales
                    and pext not in _FRAMEWORK_ROUTE_EXTS
                ):
                    locale = parts[1]

            if path_str.endswith(_UI_ROUTE_EXTS):
                m_type = "component"
                mapped = self.string_transform.normalize_route_path_for_namespace(path_str)
                import_path = f"{Config.NAMESPACE}{mapped}".replace("/", ".").rsplit(".", 1)[0]
                try:
                    from nexy.modules.compiler import Compiler

                    Compiler().compile(input=str(app_path))
                except Exception as compile_exc:
                    console.print(
                        f"  [red]ERROR[/red] {app_path.name} ({app_path}): "
                        f"compile failed - {compile_exc}"
                    )
                    continue
            else:
                m_type = "api"
                import_path = path_str.replace("/", ".").removesuffix(".py")
            try:
                module = importlib.import_module(import_path)
            except ImportError as imp_exc:
                console.print(f"  [yellow]WARN[/yellow] {app_path.name} ({app_path}): {imp_exc}")
                continue
            except Exception as exc:
                console.print(f"  [red]ERROR[/red] {app_path.name} ({app_path}): {exc}")
                continue

            clean = _route_clean_path(path_str, locale)
            pathname = Pathname(clean).process()

            name = app_path.name.lower()
            if (
                name in Config.NOTFOUND_FILE_NAMES
                or name in Config.ERROR_FILE_NAMES
                or name in Config.LOADING_FILE_NAMES
            ):
                scope = Pathname(
                    app_path.parent.as_posix().replace("src/routes", "") or "/"
                ).process()
                entry = {
                    "scope": scope,
                    "module": module,
                    "comp": self.string_transform.get_component_name(name.split(".")[0]),
                }
                if name in Config.ERROR_FILE_NAMES:
                    self.error_handlers.append(entry)
                elif name in Config.NOTFOUND_FILE_NAMES:
                    self.notfound_handlers.append(entry)
                else:
                    self.loading_handlers.append(entry)
                continue

            stem_for_comp = clean.split("/")[-1] if clean else ""
            if locale:
                if ext in _FRAMEWORK_ROUTE_EXTS:
                    raw_stem = app_path.stem
                    base_stem = raw_stem.rsplit(".", 1)[0] if "." in raw_stem else raw_stem
                    comp_name = self.string_transform.get_component_name(base_stem)
                else:
                    normalized_stem = mapped.split("/")[-1].rsplit(".", 1)[0]
                    comp_name = self.string_transform.get_component_name(normalized_stem)
            else:
                comp_name = self.string_transform.get_component_name(stem_for_comp)

            component = getattr(module, comp_name, None)
            if component is None and ext in _FRAMEWORK_ROUTE_EXTS:
                for attr_name in dir(module):
                    if attr_name.startswith("_"):
                        continue
                    val = getattr(module, attr_name, None)
                    if callable(val) and val.__class__.__name__ == "function":
                        mod = getattr(val, "__module__", "")
                        if mod == module.__name__:
                            component = val
                            comp_name = attr_name
                            break

            if locale:
                if component:
                    self._locale_variants.setdefault(pathname, {})[locale] = component
                else:
                    console.print(
                        f"  [yellow]WARN[/yellow] Locale variant '{locale}' for "
                        f"'{pathname}' - component '{comp_name}' not found in "
                        f"{app_path}"
                    )
                continue

            self.modules_meta.append(
                {
                    "module": module,
                    "type": m_type,
                    "pathname": pathname,
                    "comp_name": comp_name,
                    "import_path": import_path,
                    "source": path_str,
                }
            )

    def _register_all_routes(self) -> None:
        registered_paths: set[str] = set()

        def _path_sort_key(path: str) -> tuple[int, int]:
            if "{slug:path}" in path or re.search(r"\{[^}]+:path\}", path):
                return 2, 0
            if "{" in path:
                literals = sum(1 for seg in path.split("/") if seg and not seg.startswith("{"))
                return 1, -literals
            return 0, 0

        self.modules_meta.sort(key=lambda m: _path_sort_key(m["pathname"]))

        for meta in self.modules_meta:
            module = meta["module"]
            if module is None:
                console.print(
                    f"  [yellow]WARN[/yellow] Route skipped - module is None: {meta['source']}"
                )
                continue
            path, source = meta["pathname"], meta["source"]

            folder_deps = [Depends(d) for d in RouteDependencies.collect(source)]

            if meta["type"] == "api":
                for method, _ in HTTP_METHODS_MAP.items():
                    if handler := getattr(module, method, None):
                        RouteValidator.validate_sig(handler, path, method)

                        deps = RouteMiddleware.resolve(handler) + folder_deps

                        resp_meta = getattr(handler, "__nexy_response_meta__", None)
                        self.router.add_api_route(
                            path=path,
                            endpoint=handler,
                            methods=[method],
                            dependencies=deps or None,
                            name=method,
                            tags=[path],
                            status_code=resp_meta.status_code if resp_meta else None,
                        )

                if ws_handler := getattr(module, "SOCKET", None):
                    self.router.websocket(path)(ws_handler)

            else:
                component = getattr(module, meta["comp_name"], None)
                if component:
                    component = _lazy_component(meta["import_path"], meta["comp_name"], component)
                    locale_variants = self._locale_variants.get(path, {})
                    revalidate = self._get_revalidate(module)
                    if revalidate is not None:
                        handler = _make_isr_handler(component, path, revalidate)
                    elif locale_variants:
                        handler = _make_locale_handler(component, locale_variants)
                    else:
                        handler = _make_request_handler(component)
                    deps = RouteMiddleware.resolve(component) + folder_deps
                    self.router.get(
                        path,
                        response_class=HTMLResponse,
                        dependencies=deps or None,
                        name=handler.__name__,
                        description=component.__doc__ or "",
                        tags=[path],
                    )(handler)
                else:
                    console.print(
                        f"  [yellow]WARN[/yellow] Route '{path}' skipped - "
                        f"component '{meta['comp_name']}' not found in "
                        f"{meta['source']}"
                    )

            registered_paths.add(path)

        for path, variants in self._locale_variants.items():
            if path in registered_paths:
                continue
            components = list(variants.values())
            handler = _make_locale_handler(components[0], variants)
            self.router.get(
                path,
                response_class=HTMLResponse,
                name=handler.__name__,
                description="",
                tags=[path],
            )(handler)

    @staticmethod
    def _get_revalidate(module: Any) -> int | None:
        """Read the per-route ISR window from the module's frontmatter."""
        value = getattr(module, "revalidate", None)
        if isinstance(value, int) and value > 0:
            return value
        return None
