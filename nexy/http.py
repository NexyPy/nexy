"""The HTTP vocabulary of a Nexy handler.

Import request, response, errors and parameter sources from here rather than from the engine that
serves them. Application code then depends on Nexy's contract, and the engine underneath can change
without touching your handlers.

Example:
    >>> from nexy.http import Header, HTTPException, JSONResponse, Request
"""

from fastapi import (
    BackgroundTasks,
    Body,
    Cookie,
    Depends,
    File,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    StreamingResponse,
)

from nexy.navigation import forbidden, notFound, permanentRedirect, redirect, unauthorized

__all__ = [
    "BackgroundTasks",
    "Body",
    "Cookie",
    "Depends",
    "File",
    "FileResponse",
    "Form",
    "HTMLResponse",
    "HTTPException",
    "Header",
    "JSONResponse",
    "Path",
    "PlainTextResponse",
    "Query",
    "RedirectResponse",
    "Request",
    "Response",
    "StreamingResponse",
    "UploadFile",
    "forbidden",
    "notFound",
    "permanentRedirect",
    "redirect",
    "status",
    "unauthorized",
]
