---
name: nexy-modular
description: Writing the modular router of a Nexy project - controllers, modules, dependency injection with @Injectable and scopes, guards, and OpenAPI metadata. Load it when nexyconfig.py sets useRouter or the code lives in src/apps.
---

# Modular routing

Controllers handle requests, modules group them, providers are injected. The module is mounted with
`useRouter` in `nexyconfig.py`. File-based routing keeps working next to it: when `src/routes/`
exists it is scanned too.

```python
# nexyconfig.py
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

## Controllers and modules

```python
# src/apps/users/user_controller.py
from nexy.decorators import Controller

from .user_service import UserService


@Controller(prefix="/users")
class UserController:
    def __init__(self, svc: UserService) -> None:
        self.svc = svc

    def get(self) -> list[dict]:
        return self.svc.get_all()
```

```python
# src/apps/users/users_module.py
from nexy.decorators import Module

from .user_controller import UserController
from .user_service import UserService


@Module()
class UsersModule:
    controllers = [UserController]
    providers = [UserService]
```

- A method is matched to an HTTP verb by its name, case-insensitively: `get`, `post`, `put`,
  `patch`, `delete`, `options`, `head`, `trace`. A controller declares **one handler per verb**: a
  duplicate raises at startup.
- `@Controller(prefix="/users")` mounts every handler under the prefix. `async def SOCKET(...)`
  registers a WebSocket at the same path.
- `controllers` is required in a module; `providers`, `imports` and `exports` are optional.
  `@Module(prefix="/api")` returns an `APIRouter`.

## Dependency injection

A class opts in with `@Injectable()`.

```python
# src/apps/users/user_service.py
from nexy.decorators import Injectable


@Injectable()
class UserService:
    def get_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]
```

- Each `__init__` parameter is resolved from its **type annotation**, which must be an
  `@Injectable()` class, or the parameter needs a default value. Otherwise resolution raises
  `ValueError`. A cycle raises `RecursionError`.
- Never build an `@Injectable()` class yourself: it raises `TypeError`. Receive it in a constructor
  or call `Container.resolve(UserService)`.
- Scope: `Scope.SINGLETON` (default, one per process), `Scope.REQUEST` (one per request),
  `Scope.TRANSIENT` (a new one each time): `@Injectable(scope=Scope.REQUEST)`.
- FastAPI `Depends` still works for handler parameters.
- The container is process-wide and there is no public way to swap a provider in tests: keep services
  small and test them by calling their methods directly.

## Guards and metadata

```python
from fastapi import Header, HTTPException
from nexy.decorators import Controller, UseGuard


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller(prefix="/admin")
@UseGuard(require_token)
class AdminController:
    async def get(self) -> dict:
        return {"ok": True}
```

- `@UseGuard(*guards)` and `@Middleware(*middlewares)` add FastAPI dependencies, on a controller or
  on one method. `@Middleware` is **not** ASGI middleware: use `useMiddlewares` in the config for
  that.
- `@UseRoute(summary=..., tags=[...])` and `@UseResponse(status_code=..., response_model=...)` set
  the OpenAPI description; they do not change the path.
- The reference is served at `/docs` unless `useDocs = False`.

## Views from a controller

`useViews("src/apps/app_view.nexy")` from `nexy.hooks` renders a `.nexy` view; nest one inside
another to wrap it in a layout. For `.nexy` syntax load `nexy-file`.

## Rules

- One controller per resource, one service per intention, one folder per module (`src/apps/users/`).
- A controller adapts HTTP to a service call. Logic lives in the service, where it is tested without
  HTTP.
- Authorization is explicit: a guard or a check in the handler (see `nexy-security`).
- Write the test first (`nexy-testing`).
