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
| `notFound()`, `forbidden()`, `unauthorized()` | `404`, `403`, `401`, from anywhere in a request |
| `redirect()`, `permanentRedirect()` | a real redirect with no error page |

Without a custom file, Nexy serves its built-in styled `404` and `500` pages.

## Leave a page or answer from code

`redirect`, `permanentRedirect`, `notFound`, `forbidden` and `unauthorized` raise an HTTP exception,
so the same call works in a `.nexy` page, an API handler, a modular controller, a guard and a
`dependencies.py`. They have the same names on the client (`@nexy/client`).

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound, redirect

from src.posts import find

slug: prop[str]
post = find(slug)
if post is None:
    notFound()
if post.moved_to:
    redirect(post.moved_to)
---
<h1>{{ post.title }}</h1>
```

| Call | Answer |
|---|---|
| `redirect(url)` | `307`; `redirect(url, status=303)` turns a POST into a GET after a form |
| `permanentRedirect(url)` | `308`; browsers and search engines remember it |
| `notFound(detail=None)` | `404`: the `notfound` page, or JSON for an API client |
| `forbidden(detail=None)` | `403`: the visitor is known but may not see this |
| `unauthorized(detail=None, scheme=None)` | `401`; `scheme="Bearer"` adds `WWW-Authenticate` |

A redirect answers with the `Location` header and no page, also to an API client. Build the
destination from values you trust: a `redirect(request.query_params["next"])` sends visitors
wherever the link says. A destination with a line break is refused.

A guard protects a whole folder:

```python filename="src/routes/private/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

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

## Unhandled exceptions

An exception that nothing handled is logged once, with the exception, where it came from and the
code around it, and answered according to the mode.

| | `nx dev` | `nx start` |
|---|---|---|
| Browser | a page with the error, the lines of your code that raised it and the full traceback | the built-in `500` page (or your `errors.nexy`) with a reference |
| JSON client | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Server log | the exception and the lines of your code | the exception and the whole traceback, with the same reference |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

The reference is eight characters, new for each failure. A visitor can quote it, and you find the
traceback by searching the log for it. Neither the exception nor the code reaches the visitor in
production. A custom `errors.nexy` replaces the page only; the log line stays.

## Validation errors

A missing header, query parameter or body field answers `422` with FastAPI's JSON body, for every
client. See [Validation and errors](../handlers/validation-and-errors.md).

## Next steps

- [Dynamic routes](../pages/dynamic-routes.md)
- [API routes](../handlers/README.md)
- [Testing](../../../guides/testing.md)
