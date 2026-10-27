# Middleware files

A `middleware.py` in a routes directory wraps the requests handled by that directory. Like layouts and
`dependencies.py`, the files stack from the routes root down, outermost first.

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request
from nexy.http import JSONResponse


async def middleware(request: Request, call_next):
    if request.headers.get("authorization") != "Bearer secret":
        return JSONResponse({"detail": "login required"}, status_code=401)
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

The function is `async def middleware(request, call_next)`: the signature of FastAPI's
`@app.middleware("http")`. Call `await call_next(request)` to continue to the route, or return a
response to stop there. Code after the call runs on the way out and can change the response.

## What it wraps

A middleware applies to the **routes whose file is in its directory** or below, pages and API
handlers alike, route groups included:

```text
src/routes/
├─ middleware.py             every route
├─ open.py                   root only
├─ admin/
│  ├─ middleware.py          /admin and everything below
│  └─ users/
│     ├─ middleware.py       /admin/users and below
│     └─ index.py            root > admin > users
└─ (shop)/
   ├─ middleware.py          only the routes in this group
   └─ cart.py                root > shop     (URL: /cart)
```

For a request to `/admin/users` the order is `root`, `admin`, `users`, then the route. A group has no
URL of its own, so it is matched through the route that serves the request, not through the URL.

A URL that matches no route (a 404) only receives the middleware of directories that are not groups,
selected by URL prefix. `[slug]` matches one segment and `[...rest]` matches the remainder.

## What it does not wrap

- Framework and asset URLs: `/__nexy__/`, `/_nexy/`, `/public/`, `/assets/` and `/@...` (Vite).
- WebSocket handlers and the server lifespan: only HTTP requests.
- Files in directories starting with `_` or `.`.

## Middleware, dependencies or guards

| Use | When |
|---|---|
| `middleware.py` | you need the **response** too: headers, redirects, timing, short-circuiting for a whole area |
| [`dependencies.py`](../dependencies/README.md) | you need parsed parameters or to inject a value (current user, database session) |
| `@UseGuard` on a handler | one route needs an extra check |
| `useMiddlewares` in [config](../../../reference/config.md) | an ASGI middleware for the whole application (CORS, GZip, sessions) |

Middleware files run **before** dependencies: the request has passed every `middleware.py` of its
directories when the dependencies start.

## Rules

- The file must define `async def middleware(request, call_next)`. Otherwise Nexy stops at startup and
  names the file.
- It is a normal Python module: import what you need. It is loaded once, when the server starts.
- It is never a route: `/middleware` is a 404.
- Base path checks on `request.scope["path"]`, never on `request.url.path` or the `Host` header: since
  CVE-2026-48710 the URL object can disagree with the path the server received. See
  [Security](../../../reference/security.md).

## Cost

A project without any `middleware.py` pays nothing: the layer is not installed. With files, each
matching middleware adds a Starlette `BaseHTTPMiddleware`; keep them small.

## Next steps

- [Inheritance](../inheritance.md)
- [Dependencies](../dependencies/README.md)
- [Middleware and security](../../../guides/middleware-and-security.md)
