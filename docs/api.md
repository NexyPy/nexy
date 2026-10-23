# API

A `.py` file under `src/routes/` is an API handler. The file path is the URL, and each function
named after an HTTP method becomes an endpoint.

## Create an endpoint

```python filename="src/routes/api/items.py"
from fastapi import Request
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
a WebSocket at the same path - see [WebSocket](routing/fbr/websocket.md).

## Parameters

| Source | How it arrives |
|---|---|
| Path segment `[id]` | function argument `id`, converted to its annotation |
| Query string | `page: int = 1` |
| JSON body | Pydantic model argument |
| FastAPI primitives | `Depends`, `Header`, `Cookie`, `Form`, `UploadFile` - unchanged |

```python filename="src/routes/api/users/[id].py"
async def GET(request, id: int):
    return {"id": id}
```

The path segment is `{id}`, so FastAPI validates `id: int` and returns `422` when it is not an
integer.

## Responses

| Return | Response |
|---|---|
| `dict`, `list`, `BaseModel` | JSON |
| `JSONResponse`, `HTMLResponse`, any `Response` | exactly as declared |
| `None` | empty response - return a `Response` instead when the status matters |

For a custom status code or content type, return a response object:

```python filename="src/routes/api/items.py"
from fastapi.responses import JSONResponse


async def POST(request):
    return JSONResponse({"created": True}, status_code=201)
```

## Errors

Raise FastAPI exceptions for clients. `notfound.nexy` renders `404` and `errors.nexy` renders `500`,
each scoped to its directory, and each installed only when a copy exists at `src/routes/`.

> **Good to know**: the `500` handler catches every unhandled exception, including one raised in an
> API handler, and answers with HTML. Return `JSONResponse` when the caller expects JSON.

## OpenAPI

Every API route appears in the generated schema, because the routes are plain FastAPI routes. The
schema is served at `/openapi.json` and rendered by Scalar at `/docs`. Disable both with
`useDocs = False` in `nexyconfig.py`.

## Next steps

- [Routing](routing/README.md): file path to URL
- [Actions](actions.md): endpoints with generated paths
- [Config](config.md): middleware, CORS, sessions
