# Exceptions and errors

A request can fail in four places, and Nexy answers each one differently. This page is the index:
find the status you see, then the line that produced it, then the file that decides the body.

> [!NOTE]
> Three things are separate and easy to mix up: the **HTTP answer** (a status and a body), the
> **error page** (`notfound.nexy`, `errors.nexy`), and the **log line** (what you read in the
> terminal). Changing the page does not change the status, and customising the page does not hide
> the log.

## The short version

| What happened | Status | Browser sees | API client sees |
|---|---|---|---|
| no route matches the URL | `404` | `notfound.nexy`, else the built-in page | `{"detail": "Not Found"}` |
| a path segment does not fit its annotation | `404` | the same page | `{"detail": "Not Found"}` |
| a query, header, cookie or body field is missing or invalid | `422` | FastAPI's JSON body | FastAPI's JSON body |
| `notFound()` | `404` | the page | `{"detail": ...}` |
| `unauthorized()` | `401` | the built-in page | `{"detail": ...}` |
| `forbidden()` | `403` | the built-in page | `{"detail": ...}` |
| `raise HTTPException(409, ...)` | `409` | the built-in page | `{"detail": ...}` |
| an exception nothing caught | `500` | `errors.nexy`, else the built-in page | `{"detail", "reference"}` |
| `redirect(url)` | `307` | the destination, no page | the destination, no body |
| `permanentRedirect(url)` | `308` | the destination, no page | the destination |

An API client is a request whose `Accept` header asks for JSON and not for a page:

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!WARNING]
> `curl` sends `Accept: */*` by default, which gets the HTML page. Add
> `-H "Accept: application/json"` when you test the JSON shape. Browsers keep getting pages.

## Where a failure comes from

```diagram filename="One request, four exits"
Browser ──► Middleware ──► Router ──► Page or handler
                 │            │             │
                 │            │             ├─ return ───────────► 200
                 │            │             ├─ HTTPException ────► its status
                 │            │             └─ other exception ───► 500
                 │            └─ no match ────────────────────────► 404
                 └─ raises ──────────────────────────────────────► 500
```

| Stage | What can fail | The answer |
|---|---|---|
| Middleware | your `middleware.py`, CORS, sessions | the exception's status, else `500` |
| Router | the URL matches no file | `404` |
| Validation | a path segment cannot be converted | `404` |
| Validation | a query, header, cookie or body field | `422` |
| Page, handler, action, guard | `HTTPException` | its status |
| Page, handler, action, guard | anything else | `500` |

## Leave from anywhere

`redirect`, `permanentRedirect`, `notFound`, `forbidden` and `unauthorized` raise an HTTP exception,
so the same call works in a `.nexy` page, an API handler, a modular controller, a guard, a
`dependencies.py` and an action.

```python filename="src/routes/posts/[slug].py"
from nexy import notFound, redirect

from src.posts import find


async def GET(slug: str):
    post = find(slug)
    if post is None:
        notFound("No such post")
    if post.moved_to:
        redirect(post.moved_to)
    return post
```

| Call | Answer | When |
|---|---|---|
| `notFound(detail=None)` | `404` | the resource does not exist |
| `unauthorized(detail=None, scheme=None)` | `401` | the visitor must sign in first |
| `forbidden(detail=None)` | `403` | the visitor is known but may not see this |
| `redirect(url, status=307)` | `307` | send them elsewhere, keeping the method |
| `redirect(url, status=303)` | `303` | after a form: the next request is a `GET` |
| `permanentRedirect(url)` | `308` | a moved page that search engines should remember |

Build the destination from values you trust. `redirect(request.query_params["next"])` sends visitors
wherever the link says; it is an open redirect. A destination that holds a line break is refused.

## Validation: 422, or 404

Handler parameters are validated by FastAPI against their annotations.

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| Problem | Status | Why |
|---|---|---|
| missing or invalid query, header, cookie or body field | `422` | the request reached the handler, the data is wrong |
| invalid path segment (`/api/users/abc` for `id: int`) | `404` | the folder has no route for a non-number, so the URL does not exist |

The `422` body is FastAPI's standard shape, so clients and generated SDKs keep working:

```json
{"detail": [{"loc": ["query", "q"], "msg": "Field required", "type": "missing"}]}
```

For a form or an action, the client receives an `ActionError` with `status` and `detail`; a `422`
also fills `error.fields` with one message per field. See [Actions](../guides/actions.md#errors).

> [!TIP]
> Validate in the signature when the rule is about one field (`limit: int = 10`). Validate in the
> body when the rule needs the database or another field ("this email is already used"): raise
> `HTTPException(409)` and keep the message for the client.

## Custom error pages

```nexy filename="src/routes/notfound.nexy"
<h1>Page not found</h1>
<p>The link may be old. <a href="/">Start from the home page</a>.</p>
```

```nexy filename="src/routes/errors.nexy"
<h1>Something went wrong</h1>
<p>Try again in a moment.</p>
```

| File | Status | Scope |
|---|---|---|
| `src/routes/notfound.nexy` | `404` | every route of the project |
| `src/routes/errors.nexy` | `500` | every route of the project |
| `src/routes/forbidden.nexy` | `403` | every route of the project |
| `src/routes/unauthorized.nexy` | `401` | every route of the project |
| `src/routes/blog/notfound.nexy` | `404` | `/blog` and below |
| `src/routes/blog/errors.nexy` | `500` | `/blog` and below |
| `src/routes/loading.nexy` | - | reserved, no runtime effect yet |

One file somewhere in the routes installs the answer for its status: a copy at the root answers the
whole project, a copy in a folder answers that folder, and the deepest file that matches the URL
wins. A URL outside every copy, and a status with no file at all, get the built-in styled pages.
See [Error pages per folder](../routing/fbr/errors/folder-pages.md).

> [!IMPORTANT]
> An `errors.nexy` page replaces the `500` page; it does not catch the exception and it does not
> change the log line. If the handler that raised is the page itself, the page cannot show its own
> error details: keep `errors.nexy` simple and independent.

## Unhandled exceptions

An exception that nothing caught is logged once, with its reference, where it came from and the code
around it. The status is `500`, and the body depends on the environment.

| | `nexy dev` | `nexy build` then `nexy start` |
|---|---|---|
| Browser | the error, the lines of your code and the traceback | `errors.nexy`, else the built-in page, with a reference |
| API client | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Terminal | the exception and the lines of your code | the exception, the whole traceback and the reference |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

The reference is eight characters, new for each failure. A visitor can quote it, and you find the
traceback by searching the log for it. Neither the exception nor the code reaches the visitor in
production.

> [!CAUTION]
> Do not return the traceback to a visitor in production, and do not put secrets in an error
> message: the `detail` of an `HTTPException` is sent to the client, HTML-escaped. Put the secret in
> the log, not in the answer.

## Actions and forms

An action is a `POST` endpoint with a generated path. Its failures follow the same rules:

| Situation | Status | Client |
|---|---|---|
| a field is missing or invalid | `422` | `ActionError` with `fields` |
| `HTTPException(403)` raised in the action | `403` | `ActionError` with `status` and `detail` |
| an unhandled exception | `500` | `ActionError`; the reference is in the server log |
| the `Origin` header is another site | `403` | refused before the action runs |

A form without JavaScript posts to the action path; a success answers `303` back to the page, a
failure shows the error page. See [Actions](../guides/actions.md#forms-without-javascript).

## A checklist when a page answers the wrong thing

1. **Look at the status**, not the page. A custom `notfound.nexy` still answers `404`.
2. **Read the terminal.** A page that fails to import is not registered, so its URL answers `404`
   while the file exists. The import error is in the log.
3. **Check the extension.** With `useCSR = True`, `.nexy` pages belong to server mode; a page in the
   wrong mode is not a route.
4. **Check the depth.** A `notfound.nexy` or `errors.nexy` only works when the root copy exists.
5. **Ask for JSON** with `Accept: application/json` to see the shape your API client receives.
6. **Quote the reference** of a `500` when you open an issue or search the log.

## Next steps

- [Error pages](../routing/fbr/errors/README.md): the full page behaviour, with examples
- [Validation and errors](../routing/fbr/handlers/validation-and-errors.md): API handlers
- [Troubleshooting](../guides/troubleshooting.md): the errors people actually hit
- [Testing](../guides/testing.md): assert a status and a body
