from fastapi import FastAPI

from .modules.routers.app import _server

app: FastAPI = _server
