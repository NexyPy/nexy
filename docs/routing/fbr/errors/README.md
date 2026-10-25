# Error pages

Nexy answers errors with a page for browsers and with JSON for API clients.

## Files

| File | Answers |
|---|---|
| `notfound.nexy` | `404` for its directory |
| `errors.nexy` | `500` for its directory |
| `loading.nexy` | reserved; no runtime effect yet |

A handler is installed only when a copy exists at the routes root. A copy in a subdirectory then
refines the page for that prefix.

```nexy filename="src/routes/notfound.nexy"
<h1>Page not found</h1>
<a href="/">Back home</a>
```

## What triggers them

| Situation | Answer |
|---|---|
| No route matches | `404` |
| A dynamic segment cannot be converted to its annotation | `404` |
| An unhandled exception, in a page or an API handler | `500` |
| `raise HTTPException(status_code=403)` | the status you raised, as HTML or JSON |

Without a custom file, Nexy serves its built-in styled `404` and `500` pages.

## HTML or JSON

The same exception answers differently depending on who asks:

- A browser (`Accept: text/html`) gets an HTML page. The detail is HTML-escaped, so a message built
  from user input cannot inject markup.
- A client that asks for JSON and not for a page (`Accept: application/json`) gets
  `{"detail": "..."}` with the same status code.

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=403, detail="Out of range")
    return {"id": id}
```

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> **Good to know**: a client that sends `Accept: */*` (the default of `curl` and many HTTP
> libraries) receives the HTML page. Set `Accept: application/json` for JSON errors.

## Validation errors

A missing header, query parameter or body field answers `422` with FastAPI's JSON body, for every
client. See [Validation and errors](../handlers/validation-and-errors.md).

## Next steps

- [Dynamic routes](../pages/dynamic-routes.md)
- [API routes](../handlers/README.md)
- [Testing](../../../guides/testing.md)
