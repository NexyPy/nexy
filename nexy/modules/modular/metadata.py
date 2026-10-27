"""The decorators that attach information to a controller or to one of its handlers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from collections.abc import Set as AbstractSet
from dataclasses import dataclass, fields
from typing import Any

from fastapi.responses import Response

Handler = Callable[..., Any]


@dataclass(frozen=True)
class RouteMeta:
    """What `@UseRoute` says about a route: its name and what OpenAPI shows."""

    name: str | None = None
    tags: list[str] | None = None
    summary: str | None = None
    description: str | None = None
    deprecated: bool | None = None
    include_in_schema: bool | None = None
    operation_id: str | None = None
    openapi_extra: dict[str, Any] | None = None


@dataclass(frozen=True)
class ResponseMeta:
    """What `@UseResponse` says about the answer of a route."""

    status_code: int | None = None
    response_class: type[Response] | None = None
    response_model: type[Any] | None = None
    responses: dict[int | str, Any] | None = None
    response_description: str | None = None
    response_model_include: AbstractSet[str] | Mapping[str, Any] | None = None
    response_model_exclude: AbstractSet[str] | Mapping[str, Any] | None = None
    response_model_by_alias: bool | None = None
    response_model_exclude_unset: bool | None = None
    response_model_exclude_defaults: bool | None = None
    response_model_exclude_none: bool | None = None


def route_options(
    meta: RouteMeta | ResponseMeta | None, skip: tuple[str, ...] = ()
) -> dict[str, Any]:
    """The fields of *meta* that were set, named as the router expects them."""
    if meta is None:
        return {}
    values = {field.name: getattr(meta, field.name) for field in fields(meta)}
    return {name: value for name, value in values.items() if value is not None and name not in skip}


def Controller(prefix: str = "", tags: list[str] | None = None) -> Callable[[type[Any]], type[Any]]:
    def wrapper(cls: type[Any]) -> type[Any]:
        cls.__is_controller__ = True
        cls.__controller_prefix__ = prefix
        cls.__controller_tags__ = tags or [cls.__name__]
        return cls

    return wrapper


def _collect(attribute: str, items: tuple[Callable[..., Any], ...]) -> Callable[[Any], Any]:
    """A decorator that adds *items* to the tuple kept in *attribute* of its target."""

    def wrapper(target: Any) -> Any:
        setattr(target, attribute, (*getattr(target, attribute, ()), *items))
        return target

    return wrapper


def UseGuard(*guards: Callable[..., Any]) -> Callable[[Any], Any]:
    return _collect("__nexy_guards__", guards)


def Middleware(*middlewares: Callable[..., Any]) -> Callable[[Any], Any]:
    return _collect("__nexy_middlewares__", middlewares)


def _attach(attribute: str, meta: RouteMeta | ResponseMeta) -> Callable[[Handler], Handler]:
    def wrapper(handler: Handler) -> Handler:
        setattr(handler, attribute, meta)
        return handler

    return wrapper


def UseRoute(
    name: str | None = None,
    tags: list[str] | None = None,
    summary: str | None = None,
    description: str | None = None,
    deprecated: bool | None = None,
    include_in_schema: bool | None = None,
    operation_id: str | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[Handler], Handler]:
    meta = RouteMeta(
        name, tags, summary, description, deprecated, include_in_schema, operation_id, openapi_extra
    )
    return _attach("__nexy_route_meta__", meta)


useRoute = UseRoute


def UseResponse(
    status_code: int | None = None,
    response_class: type[Response] | None = None,
    response_model: type[Any] | None = None,
    responses: dict[int | str, Any] | None = None,
    response_description: str | None = None,
    response_model_include: AbstractSet[str] | Mapping[str, Any] | None = None,
    response_model_exclude: AbstractSet[str] | Mapping[str, Any] | None = None,
    response_model_by_alias: bool | None = None,
    response_model_exclude_unset: bool | None = None,
    response_model_exclude_defaults: bool | None = None,
    response_model_exclude_none: bool | None = None,
) -> Callable[[Handler], Handler]:
    meta = ResponseMeta(
        status_code,
        response_class,
        response_model,
        responses,
        response_description,
        response_model_include,
        response_model_exclude,
        response_model_by_alias,
        response_model_exclude_unset,
        response_model_exclude_defaults,
        response_model_exclude_none,
    )
    return _attach("__nexy_response_meta__", meta)
