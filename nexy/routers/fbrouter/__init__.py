import importlib
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import HTMLResponse

from nexy.core.config import Config
from nexy.core.string import Pathname, StringTransform
from nexy.routers.fbrouter.discovery import RouteDiscovery
from nexy.utils.common.console import console

# Specialized classes
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
        return handler(**request.path_params)

    _locale_handler.__name__ = base_component.__name__
    _locale_handler.__doc__ = base_component.__doc__
    for attr in ("__nexy_guards__", "__nexy_middlewares__"):
        if hasattr(base_component, attr):
            setattr(_locale_handler, attr, getattr(base_component, attr))

    return _locale_handler


class FBRouter:
    def __init__(self) -> None:
        self.discovery = RouteDiscovery()
        self.router = APIRouter()
        self.string_transform = StringTransform()
        self.modules_meta: list[dict[str, Any]] = []
        self.error_handlers: list[dict[str, Any]] = []
        self.notfound_handlers: list[dict[str, Any]] = []

        self._load_and_register()

    def register_on(self, app: FastAPI) -> None:
        app.include_router(self.router)

    def _load_and_register(self) -> None:
        self._locale_variants: dict[str, dict[str, Callable[..., str]]] = {}
        self._scan_modules()
        self._register_all_routes()

    def _scan_modules(self) -> None:
        available_locales = Config().useLocales or []

        for app_path in self.discovery.scan():
            path_str = app_path.as_posix()

            # Detect locale variant from filename pattern: basename.locale.ext
            # Only active when useLocales has languages configured
            name = app_path.name.lower()
            locale = None
            if available_locales and name.count(".") > 1:
                parts = name.rsplit(".", 2)
                ext = "." + parts[2]
                if ext in Config.ROUTE_FILE_EXTENSIONS and parts[1] in available_locales:
                    locale = parts[1]

            # 1. Resolve Import Path
            if path_str.endswith((".nexy", ".mdx")):
                m_type = "component"
                mapped = self.string_transform.normalize_route_path_for_namespace(path_str)
                import_path = f"{Config.NAMESPACE}{mapped}".replace("/", ".").rsplit(".", 1)[0]
            else:
                m_type = "api"
                import_path = path_str.replace("/", ".").removesuffix(".py")
            try:
                module = importlib.import_module(import_path)
            except ImportError as imp_exc:
                console.print(
                    f"  [yellow]WARN[/yellow] {app_path.name} ({app_path}): {imp_exc}"
                )
                continue
            except Exception as exc:
                console.print(
                    f"  [red]ERROR[/red] {app_path.name} ({app_path}): {exc}"
                )
                continue

            # 2. Process Pathname
            clean = (
                path_str.replace(f"{Config.NAMESPACE}src/routes", "")
                .replace("src/routes", "")
                .split(".")[0]
            )
            pathname = Pathname(clean).process()

            # 3. Categorize (Error, NotFound, or Route)
            name = app_path.name.lower()
            if name in ("error.nexy", "notfound.nexy"):
                scope = Pathname(
                    app_path.parent.as_posix().replace("src/routes", "") or "/"
                ).process()
                entry = {
                    "scope": scope,
                    "module": module,
                    "comp": self.string_transform.get_component_name(name.split(".")[0]),
                }
                if "error" in name:
                    self.error_handlers.append(entry)
                else:
                    self.notfound_handlers.append(entry)
                continue

            if locale:
                # Locale variant — store separately for locale-aware routing
                # Component name comes from normalized VFS path (guide_fr -> Guide_fr)
                normalized_stem = mapped.split("/")[-1].rsplit(".", 1)[0]
                comp_name = self.string_transform.get_component_name(normalized_stem)
                component = getattr(module, comp_name, None)
                if component:
                    self._locale_variants.setdefault(pathname, {})[locale] = component
                else:
                    console.print(
                        f"  [yellow]WARN[/yellow] Locale variant '{locale}' for "
                        f"'{pathname}' — component '{comp_name}' not found in "
                        f"{app_path}"
                    )
                continue

            self.modules_meta.append(
                {
                    "module": module,
                    "type": m_type,
                    "pathname": pathname,
                    "comp_name": self.string_transform.get_component_name(clean),
                    "source": path_str,
                }
            )

    def _register_all_routes(self) -> None:
        registered_paths: set[str] = set()

        for meta in self.modules_meta:
            module = meta["module"]
            if module is None:
                console.print(
                    f"  [yellow]WARN[/yellow] Route skipped — "
                    f"module is None: {meta['source']}"
                )
                continue
            path, source = meta["pathname"], meta["source"]

            # Get folder-level dependencies
            folder_deps = [Depends(d) for d in RouteDependencies.collect(source)]

            if meta["type"] == "api":
                for method, _ in HTTP_METHODS_MAP.items():
                    if handler := getattr(module, method, None):
                        RouteValidator.validate_sig(handler, path, method)

                        # Merge guards, middlewares and folder deps
                        deps = RouteMiddleware.resolve(handler) + folder_deps

                        # Metadata extraction
                        resp_meta = getattr(handler, "__nexy_response_meta__", None)
                        self.router.add_api_route(
                            path=path,
                            endpoint=handler,
                            methods=[method],
                            dependencies=deps or None,
                            name=method,
                            tags=[path],
                            status_code=resp_meta.status_code if resp_meta else None,
                            # ... (other response_meta fields)
                        )

                if ws_handler := getattr(module, "SOCKET", None):
                    self.router.websocket(path)(ws_handler)

            else:  # Component (UI)
                component = getattr(module, meta["comp_name"], None)
                if component:
                    # Check for locale variants
                    locale_variants = self._locale_variants.get(path, {})
                    handler = (
                        _make_locale_handler(component, locale_variants)
                        if locale_variants
                        else component
                    )
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
                        f"  [yellow]WARN[/yellow] Route '{path}' skipped — "
                        f"component '{meta['comp_name']}' not found in "
                        f"{meta['source']}"
                    )

            registered_paths.add(path)

        # Register orphan locale variant routes (no base route file)
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
