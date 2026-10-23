# Modular routing

Modular routing uses classes with decorators instead of files under `src/routes/`. Mount the
resulting `APIRouter` with `useRouter` in `nexyconfig.py`.

## Set up the router

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> **Good to know**: file-based routing keeps working. If `src/routes/` exists, it is scanned even
> when `useRouter` is set.

## Write a controller

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

Methods are matched by name, case-insensitively: `get`, `post`, `put`, `patch`, `delete`, `options`,
`head`, `trace`.

A controller declares one handler per HTTP method; a duplicate raises at startup. Add a prefix with
`@Controller(prefix="/users")` - every handler is mounted on `prefix/`. `async def SOCKET(...)` on a
controller registers a WebSocket at the same path.

## Group controllers in a module

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` returns an `APIRouter`. `controllers` is required; `providers`, `imports`
and `exports` are optional. Imported modules are mounted as sub-routers, and their exported providers
are resolved at startup.

## Inject a service

```python filename="src/apps/users/user_service.py"
from nexy.decorators import Injectable


@Injectable()
class UserService:
    def get_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from .user_service import UserService


@Controller(prefix="/users")
class UserController:
    def __init__(self, svc: UserService) -> None:
        self.svc = svc

    def get(self) -> list[dict]:
        return self.svc.get_all()
```

Register the controller in a module. Listing the service in `providers` additionally resolves it
eagerly at startup:

```python filename="src/apps/users/users_module.py"
from nexy.decorators import Module
from .user_controller import UserController
from .user_service import UserService


@Module()
class UsersModule:
    controllers = [UserController]
    providers = [UserService]
```

- Controllers are instantiated with `Container.resolve()` at startup; each `__init__` parameter
  annotated with an `@Injectable()` class is resolved first.
- `@Injectable(scope=...)` accepts `Scope.SINGLETON` (default), `Scope.REQUEST` or
  `Scope.TRANSIENT`. Import `Scope` from `nexy.decorators`.
- Constructing an `@Injectable()` class yourself raises `TypeError`. Resolve it with
  `Container.resolve(UserService)` (imported from `nexy.decorators`) or receive it in a controller.
- FastAPI `Depends` works as usual for route parameters.

## Guards, metadata and responses

- `@UseGuard(*guards)` on a controller or method: each guard is added as a FastAPI `Depends`, so it
  declares the parameters it needs and raises (for example `HTTPException`) to reject the call.
- `@Middleware(*middlewares)` behaves the same way - these are FastAPI dependencies, not ASGI
  middleware.
- `@UseRoute(...)` sets OpenAPI metadata: `name`, `tags`, `summary`, `description`, `deprecated`,
  `include_in_schema`, `operation_id`, `openapi_extra`. It does not change the path.
- `@UseResponse(...)` sets `status_code`, `response_class`, `response_model`, `responses` and the
  serialization options.

## Example

See `examples/Modular/api/minimal/`.

## Next steps

- [Routing](README.md): the file-based router
- [API](../api.md): handlers and OpenAPI
- [Config](../config.md): every option, including `useRouter`
