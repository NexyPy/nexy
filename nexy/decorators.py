"""The decorators of Nexy, in one place: ``from nexy.decorators import Controller, Module, Action``.

The work is done in `nexy.modules.di` (injection) and `nexy.modules.modular` (controllers and
modules); this module is the stable import path for them.
"""

from collections.abc import Callable
from typing import Any

from nexy.modules.di.container import Container, Injectable, Scope
from nexy.modules.modular.metadata import (
    Controller,
    Middleware,
    ResponseMeta,
    RouteMeta,
    UseGuard,
    UseResponse,
    UseRoute,
    useRoute,
)
from nexy.modules.modular.module import HTTP_METHODS, Module
from nexy.modules.routers.actions.revalidate import revalidate
from nexy.modules.routers.actions.store import ACTIONS_STORE


def Action(func: Callable[..., Any] | None = None) -> Any:
    """Turn a function into a POST endpoint the client can call; see `docs/guides/actions.md`."""

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        ACTIONS_STORE.register(f)
        return f

    return decorator if func is None else decorator(func)


__all__ = [
    "ACTIONS_STORE",
    "HTTP_METHODS",
    "Action",
    "Container",
    "Controller",
    "Injectable",
    "Middleware",
    "Module",
    "ResponseMeta",
    "RouteMeta",
    "Scope",
    "UseGuard",
    "UseResponse",
    "UseRoute",
    "revalidate",
    "useRoute",
]
