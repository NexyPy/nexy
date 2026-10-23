from starlette.types import ASGIApp

from .modules.routers.app import _server

# ASGI application entry point. It is a FastAPI app except during `nexy dev`,
# where it is wrapped by the Vite proxy so the app has a single public origin.
app: ASGIApp = _server
