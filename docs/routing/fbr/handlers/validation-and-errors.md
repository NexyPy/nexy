# Validation and errors

How an API handler reports a bad request.

## Validation

Handler parameters are validated by FastAPI against their annotations.

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| Problem | Status | Body |
|---|---|---|
| missing or invalid query, header, cookie or body field | `422` | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| invalid **path** segment (`/api/users/abc` for `id: int`) | `404` | the not-found page, or JSON for `Accept: application/json` |

A path segment that cannot be converted is a `404` rather than a `422`: a dynamic route captures any
URL, and a URL that cannot be converted does not exist.

The `422` body is FastAPI's standard shape, so existing clients and generated SDKs keep working.

## Raising errors

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    item = find(id)
    if item is None:
        raise HTTPException(status_code=404, detail="No such item")
    return item
```

| Client sends | Response |
|---|---|
| `Accept: application/json` | `{"detail": "No such item"}` with status `404` |
| `Accept: text/html` | the [error page](../errors/README.md) |
| `Accept: */*` | the error page |

Set `Accept: application/json` in API clients. Browsers keep getting pages.

## Unhandled exceptions

An exception that your handler does not catch answers `500`, with the same HTML or JSON choice.

## Custom responses

Return a response object when you control the body:

```python
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"error": "conflict"}, status_code=409)
```

## Next steps

- [API routes](README.md)
- [Error pages](../errors/README.md)
- [Testing](../../../guides/testing.md)
