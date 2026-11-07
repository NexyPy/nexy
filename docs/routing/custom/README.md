# Include an existing FastAPI router in Nexy

To include an existing FastAPI router in Nexy, set `useRouter` to that `APIRouter` in the
`NexyConfig` class of `nexyconfig.py`: its routes are served as they are, next to the files of
`src/routes/`.

## When to use a custom router

- **Gradual migration**: a FastAPI app moves to Nexy route by route, and its old routes keep
  answering meanwhile.
- **Code reuse**: a package already exposes an `APIRouter`, for authentication or billing.
- **A backend you keep**: the API stays plain FastAPI, and Nexy adds the pages.

## Set `useRouter` in `nexyconfig.py`

The router is any FastAPI `APIRouter`, written the way you already write one:

```python filename="src/legacy/api.py"
from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/status")
async def status():
    return {"status": "ok"}


@router.get("/users/{id}")
async def user(id: int):
    return {"id": id}
```

`useRouter` is a field of the `NexyConfig` class, like every setting of the project:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

`nx dev` then answers `GET /api/status` and `GET /api/users/{id}`, and `/docs` lists them.

> [!NOTE]
> `useRouter` in `nexyconfig.py` is a setting. `from nexy import useRouter` is another thing: the
> hook a `.nexy` page uses to read the current route. Do not import it to configure the router.

## Several routers

`useRouter` takes one router. Gather several under one parent with `include_router`:

```python filename="src/legacy/__init__.py"
from fastapi import APIRouter

from .api import router as api
from .auth import router as auth

router = APIRouter()
router.include_router(api)
router.include_router(auth, prefix="/auth")
```

```python filename="src/legacy/auth.py"
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    return {"token": "demo"}
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

## Pages and route files next to it

`src/routes/` is still read while `useRouter` is set: a `.nexy` page or a `.py` route file answers
next to the included routes.

```nexy filename="src/routes/index.nexy"
---
title = "Home"
---
<h1>{{ title }}</h1>
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"ok": True}
```

Two limits while `useRouter` is set:

- pages are not wrapped by `layout.nexy`;
- `useCSR = True` is refused: `nx dev` and `nx build` answer `useCSR requires file-based routing`.

A URL is answered once. Give the included router a prefix, here `/api`, and keep the files of
`src/routes/` off the paths it uses.

## A whole FastAPI app

`useRouter` takes an `APIRouter`, not a `FastAPI` app. An app's routes sit on its `router`
attribute:

```python filename="src/legacy/service.py"
from fastapi import FastAPI

service = FastAPI(title="Billing")


@service.get("/billing/invoices")
async def invoices():
    return []
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.service import service


class NexyConfig(NexyConfigModel):
    useRouter = service.router
```

The app's own middleware, exception handlers and startup events stay behind: move them to
`useMiddlewares` and the other fields of `nexyconfig.py`.

## Dependencies, auth and the database

The router runs in the Nexy process, so `Depends`, security schemes and database sessions work as
in the original app:

```python filename="src/legacy/secure.py"
from fastapi import APIRouter, Depends, Header, HTTPException


def require_token(x_token: str = Header("")) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=401, detail="Bad token")


router = APIRouter(prefix="/secure", dependencies=[Depends(require_token)])


@router.get("/data")
async def data():
    return {"data": 42}
```

## Test it

```python filename="tests/test_legacy.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_the_included_route_answers():
    assert TestClient(app).get("/api/status").json() == {"status": "ok"}
```

## Next steps

- [From FastAPI to Nexy](../../coming-from/fastapi.md): move the routes to files, one by one
- [File-based routing](../fbr/README.md)
- [Modular routing](../modular/README.md): `useRouter = AppModule`
