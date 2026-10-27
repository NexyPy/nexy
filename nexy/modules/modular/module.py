"""`@Module`: a router made of controllers, with the providers and imports they need."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Iterator
from typing import Any

from fastapi import APIRouter, Depends

from nexy.core.http_methods import HTTP_METHODS
from nexy.modules.di.container import Container
from nexy.modules.modular.metadata import ResponseMeta, RouteMeta, route_options

_META_ROUTE = "__nexy_route_meta__"
_META_RESPONSE = "__nexy_response_meta__"


def _resolve_exports(imports: list[Any]) -> None:
    """Build the injectable classes the imported modules export."""
    for sub_router in imports:
        for exported in getattr(sub_router, "__module_exports__", []):
            if hasattr(exported, "__injectable__"):
                Container.resolve(exported)


def _resolve_providers(providers: list[type[Any]]) -> None:
    for provider in providers:
        if not hasattr(provider, "__injectable__"):
            raise ValueError(f"{provider.__name__} must be @Injectable()")
        Container.resolve(provider)


def Module(prefix: str = "") -> Callable[[type[Any]], APIRouter]:
    def wrapper(cls: type[Any]) -> APIRouter:
        controllers = getattr(cls, "controllers", [])
        imports = getattr(cls, "imports", [])
        if not controllers:
            raise ValueError(f"Module {cls.__name__} must have at least one controller")
        router = APIRouter(prefix=prefix)
        setattr(router, "__module_exports__", getattr(cls, "exports", []))
        _resolve_exports(imports)
        _resolve_providers(getattr(cls, "providers", []))
        for sub_router in imports:
            router.include_router(sub_router)
        for controller in controllers:
            register_controller(controller, router)
        return router

    return wrapper


def _handlers(ctrl_cls: type[Any], instance: Any) -> Iterator[tuple[str, str, Callable[..., Any]]]:
    """(HTTP verb or SOCKET, method name, bound method) of each handler; a verb is used once."""
    seen: set[str] = set()
    for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
        verb = name.upper()
        if verb in HTTP_METHODS and verb in seen:
            raise ValueError(
                f"Controller {ctrl_cls.__name__} has multiple handlers for HTTP method {verb}"
            )
        if verb in HTTP_METHODS or verb == "SOCKET":
            seen.add(verb)
            yield verb, name, method


def _dependencies(ctrl_cls: type[Any], method: Callable[..., Any]) -> list[Any]:
    """The guards and middlewares of the controller, then of the method, as FastAPI dependencies."""
    declared = (
        *getattr(ctrl_cls, "__nexy_guards__", ()),
        *getattr(ctrl_cls, "__nexy_middlewares__", ()),
        *getattr(method, "__nexy_guards__", ()),
        *getattr(method, "__nexy_middlewares__", ()),
    )
    return [Depends(dependency) for dependency in declared]


def _route_arguments(
    ctrl_cls: type[Any], verb: str, name: str, method: Callable[..., Any]
) -> dict[str, Any]:
    route: RouteMeta | None = getattr(method, _META_ROUTE, None)
    response: ResponseMeta | None = getattr(method, _META_RESPONSE, None)
    return {
        "path": "/",
        "endpoint": method,
        "methods": [verb],
        "name": (route.name if route and route.name else f"{ctrl_cls.__name__}.{name}"),
        "dependencies": _dependencies(ctrl_cls, method) or None,
        **route_options(route, skip=("name",)),
        **route_options(response),
    }


def register_controller(ctrl_cls: type[Any], parent_router: APIRouter) -> None:
    """Add the handlers of *ctrl_cls* to *parent_router*, under the controller's prefix."""
    prefix = getattr(ctrl_cls, "__controller_prefix__", "")
    tag = parent_router.prefix + prefix if (parent_router.prefix or prefix) else "/"
    router = APIRouter(prefix=prefix, tags=[tag])
    instance = Container.resolve(ctrl_cls)
    for verb, name, method in _handlers(ctrl_cls, instance):
        if verb == "SOCKET":
            router.add_api_websocket_route(path="/", endpoint=method)
        else:
            router.add_api_route(**_route_arguments(ctrl_cls, verb, name, method))
    parent_router.include_router(router)
