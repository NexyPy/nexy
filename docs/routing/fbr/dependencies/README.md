# Dependencies and guards

Share authentication, database sessions and other setup across routes with FastAPI dependencies.
They work at two levels, and the directory level is inherited like layouts.

| Level | Where | Applies to |
|---|---|---|
| Directory | `dependencies.py` | every route in the directory and below, pages included |
| Handler | `Depends`, `@UseGuard`, `@Middleware` | one handler |

## Per directory: `dependencies.py`

A `dependencies.py` declares a `dependencies` list of plain functions. Nexy wraps each one in
`Depends`.

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

> **Good to know**: list the functions themselves. A `Depends(...)` object in the list is ignored.

Every route under `src/routes/admin/` now requires the header, `.py` handlers and `.nexy` pages
alike.

## Inheritance

Dependencies are collected from the routes root down to the route's directory, **outermost first**,
exactly like layouts, and the handler's own guards run last:

```text
src/routes/
├─ dependencies.py              1. root
└─ admin/
   ├─ dependencies.py           2. admin
   └─ users/
      ├─ dependencies.py        3. users
      └─ index.py               4. handler guards, then the handler
```

For `GET /admin/users` the order is `root`, `admin`, `users`, the handler's `@UseGuard` functions,
its `@Middleware` functions, then the handler. A route group (`(group)/`) is a directory like any
other, so its `dependencies.py` takes part.

## Per handler

Use `Depends` in the signature, like in any FastAPI app:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header, HTTPException


def current_user(authorization: str = Header(...)) -> str:
    if authorization != "Bearer secret":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "ada"


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## Guards and middleware on a handler

`@UseGuard` and `@Middleware` attach FastAPI dependencies to a handler without changing its
signature. Both are dependencies, not ASGI middleware:

```python filename="src/routes/admin/users/index.py"
from nexy.decorators import Middleware, UseGuard


def audit() -> None: ...


def must_be_staff(x_staff: str = Header(...)) -> None: ...


@UseGuard(must_be_staff)
@Middleware(audit)
async def GET():
    return {"ok": True}
```

For real ASGI middleware (CORS, GZip, sessions, your own) use `useMiddlewares` and the `use*`
options in [Middleware and security](../../../guides/middleware-and-security.md).

## Failing a dependency

A dependency rejects a request by raising. `HTTPException` answers with the status you raised, as
JSON for API clients (`Accept: application/json`) and as an error page for browsers. See
[Validation and errors](../handlers/validation-and-errors.md).

## Next steps

- [Inheritance](../inheritance.md)
- [Handlers](../handlers/README.md)
- [Middleware and security](../../../guides/middleware-and-security.md)
