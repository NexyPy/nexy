"""The ASGI entry point: ``uvicorn nexy.app:app``.

``app`` is a FastAPI app, wrapped by the Vite proxy during `nexy dev` so the app has a single
public origin. It is assembled from the project in the working directory the first time it is
read, not when this module is imported.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from starlette.types import ASGIApp

    app: ASGIApp


def __getattr__(name: str) -> Any:
    if name != "app":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from .modules.routers import app as assembly

    return assembly._server
