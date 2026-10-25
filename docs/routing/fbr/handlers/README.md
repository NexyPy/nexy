# API

A `.py` file under `src/routes/` is an API handler. The file path is the URL, and each function
named after an HTTP method becomes an endpoint.

## Create an endpoint

```python filename="src/routes/api/items.py"
from nexy.http import Request
from pydantic import BaseModel


class Item(BaseModel):
    name: str


async def GET(request: Request):
    return {"items": []}


async def POST(request: Request, body: Item):
    return {"created": body.name}
```

This file answers `GET /api/items` and `POST /api/items`.

Supported function names: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `HEAD`. `SOCKET` opens
a WebSocket at the same path - see [WebSocket](../realtime/websocket.md).

## The HTTP vocabulary

Import what a handler needs from `nexy.http`:

```python
from nexy.http import Depends, Header, HTTPException, JSONResponse, Request, status
```

It exposes the request and response classes (`Request`, `Response`, `JSONResponse`, `HTMLResponse`,
`PlainTextResponse`, `RedirectResponse`, `StreamingResponse`, `FileResponse`), the parameter sources
(`Header`, `Query`, `Cookie`, `Path`, `Body`), `Depends`, `BackgroundTasks`, `HTTPException` and
`status`. Handlers written against this module depend on Nexy's contract, not on the engine that
serves them. Pydantic models describe bodies and responses as usual.

## Parameters

| Source | How it arrives |
|---|---|
| Path segment `[id]` | function argument `id`, converted to its annotation |
| Query string | `page: int = 1` |
| JSON body | Pydantic model argument |
| FastAPI primitives | `Depends`, `Header`, `Cookie`, `Form`, `UploadFile` - unchanged |

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

The path segment is `{id}`, so FastAPI validates `id: int`. A value that is not an integer answers
`404`, because a dynamic route captures any URL and a URL that cannot be converted does not exist.
See [Validation and errors](validation-and-errors.md).

## Responses

| Return | Response |
|---|---|
| `dict`, `list`, `BaseModel` | JSON |
| `JSONResponse`, `HTMLResponse`, any `Response` | exactly as declared |
| `None` | empty response - return a `Response` instead when the status matters |

For a custom status code or content type, return a response object:

```python filename="src/routes/api/items.py"
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"created": True}, status_code=201)
```

## Errors

Raise FastAPI exceptions for clients. A client that sends `Accept: application/json` receives
`{"detail": "..."}` with the status you raised; a browser receives the error page. `notfound.nexy`
renders `404` and `errors.nexy` renders `500`, each scoped to its directory. See
[Validation and errors](validation-and-errors.md) and [Error pages](../errors/README.md).

## OpenAPI

Every API route appears in the generated schema, because the routes are plain FastAPI routes. The
schema is served at `/openapi.json` and rendered by Scalar at `/docs`. Disable both with
`useDocs = False` in `nexyconfig.py`.

## Next steps

- [Dependencies](../dependencies/README.md): shared auth and setup per handler or per directory
- [Validation and errors](validation-and-errors.md): `422`, `404` and JSON errors
- [Routing](../../README.md): file path to URL
- [Actions](../../../guides/actions.md): endpoints with generated paths
- [Config](../../../reference/config.md): middleware, CORS, sessions
