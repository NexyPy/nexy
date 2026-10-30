# Custom Router

Nexy lets you include an existing FastAPI app as a router into your project. This is useful when you want to reuse backend logic from another service, integrate with third-party APIs, or build a composite application with multiple routing concerns.

Unlike file-based and modular routers, which are intrinsic to Nexy, a custom router is simply an `APIRouter` that you mount into your application.

## When to use a custom router

- **Third‑party services**: You have an existing FastAPI app that you want to expose through Nexy’s client.
- **Code reuse**: Extract backend logic from another project into a router and include it in a new one.
- **Multi‑tenant or micro‑frontend patterns**: Each tenant or module provides its own router.
- **Gradual migration**: Start with an `APIRouter` and evolve it into a full Nexy module later.

## How it works

```python
from fastapi import APIRouter
from nexy import useRouter

# An existing FastAPI router (from another service)
third_party = APIRouter()
@third_party.get("/info")
async def info():
    return {"name": "Foo"}

# In your nexyconfig.py:
useRouter = third_party
```

The router is mounted automatically by Nexy’s router resolver. Its routes are available under the same URL pattern as in the original app. No extra configuration is needed.

## Building a custom router

1. **Create the router**
   ```python
   from fastapi import APIRouter

   api = APIRouter()
   @api.get("/status")
   async def status():
       return {"status": "ok"}
   ```

2. **Reference it in `nexyconfig.py`**
   ```python
   from .my_backend import api

   useRouter = api
   ```

3. **Access routes**
   - File‑based pages (`.nexy`, `.md`) and modular handlers can reference `/status` as they would any other route.
   - The router runs in the same process, so dependencies, database connections, and authentication work exactly as in the original app.

## Integration with other routers

A Nexy project can combine:

- **File‑based routing** (`src/routes/`) for pages and simple endpoints
- **Modular routing** (`useRouter = AppModule`) for structured backends
- **Custom routing** (`useRouter = APIRouter`) for third‑party code

All three coexist; each route is registered only once. The file‑based router is always scanned when `src/routes/` exists.

## CLI access to the included app

The `nexy dev` and `nx` commands operate on the mounted router just like a built‑in router. You get:

- Hot reload for endpoints defined in the custom router (if it uses `nexy` or FastAPI’s usual dev server features)
- Validation in `nexyconfig.py` (any `APIRouter` works)
- Auto‑generated docs for the included routes (if you enable them)

## Security and isolation

Because the router is included, not mounted via `app.mount`, there is no extra ASGI layer. The router lives in the same application object as your file‑based and modular routes. This means:

- Middleware added by the custom router applies to all requests.
- Guards and dependency injection defined in the custom router can access the same container as your own code (if you use modular injection).
- There is no URL prefix other than what the router itself defines.

If you need isolation, wrap the router in a sub‑application before including it, or use standard FastAPI techniques.

## Example: Including an existing FastAPI project

Suppose you have `auth.py` in another package:

```python
from fastapi import FastAPI, APIRouter

auth = FastAPI(title="Auth service")
api = APIRouter()

@api.get("/login")
async def login():
    return {"msg": "Login"}

auth.include_router(api)
```

In `nexyconfig.py`:

```python
from other_package.auth import api

useRouter = api
```

The `/login` endpoint is now reachable from your Nexy site without moving a line of code.

## How to start

1. Create your `APIRouter` (or find one in an existing package).
2. Point `useRouter` at it in `nexyconfig.py`.
3. Access its routes through your pages, handlers, or client frameworks.
4. If you need more control, convert the custom router into a modular router using `AppModule`.

## Next steps

- [File‑based routing](fbr/README.md) – Build pages and simple handlers from files.
- [Modular routing](modular/README.md) – Structured backends with injection and guards.
- [Route handlers](fbr/handlers/README.md) – Define Python endpoints.

The custom router gives you the flexibility to reuse existing FastAPI code while keeping the simplicity of file‑based pages and modular structure.