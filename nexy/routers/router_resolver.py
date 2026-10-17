from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI

from nexy.core.config import Config
from nexy.routers.actions.engine import ACTION_ENGINE
from nexy.routers.fbrouter import FBRouter


def resolve_router(
    server: FastAPI,
    config: Config,
    scalar_html: Callable[..., Any],
    docs_url: str | None,
) -> FBRouter | None:
    """SOLID: Decoupled router resolution logic."""
    if docs_url:
        server.get(docs_url, include_in_schema=False)(scalar_html)

    ACTION_ENGINE.include_router(server)

    router_source = config.useRouter
    if isinstance(router_source, (APIRouter, type)) and (
        isinstance(router_source, APIRouter) or issubclass(router_source, APIRouter)
    ):
        server.include_router(router_source)

    if Path("src/routes").exists():
        fb_router = FBRouter()
        fb_router.register_on(server)
        return fb_router
    return None
