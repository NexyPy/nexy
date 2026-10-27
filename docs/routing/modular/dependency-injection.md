# Dependency injection

Nexy resolves constructor dependencies for controllers and services. A class opts in with
`@Injectable()`.

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

## How resolution works

- Each `__init__` parameter is resolved from its **type annotation**. The annotation must be an
  `@Injectable()` class, or the parameter must have a default value; otherwise resolution raises
  `ValueError`.
- Controllers are instantiated with `Container.resolve()` at startup.
- A dependency cycle raises `RecursionError` naming the class.
- Services can inject other services, to any depth.

## Scopes

```python
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class CurrentUser: ...
```

| Scope | Lifetime |
|---|---|
| `Scope.SINGLETON` (default) | one instance for the whole process |
| `Scope.REQUEST` | one instance per request context |
| `Scope.TRANSIENT` | a new instance on every resolution |

## The container

```python
from nexy.decorators import Container

service = Container.resolve(UserService)
```

Constructing an `@Injectable()` class yourself raises `TypeError`: the container owns its lifecycle.
Use `Container.resolve(...)` or receive the class through another constructor.

`Container.clear_request_scope()` drops the current request's instances.

## Route parameters

FastAPI `Depends` works as usual for handler parameters, next to constructor injection:

```python
from fastapi import Depends


def get(self, limit: int = Depends(pagination)) -> list[dict]: ...
```

## Limits

The container is process-wide. Providers are not isolated per module, `exports` only decides which
providers an importing module resolves eagerly, and there is no public API to swap a provider in
tests. See [Nexy and NestJS](vs-nestjs.md) for the full comparison.

## Next steps

- [Guards and metadata](guards-and-metadata.md)
- [Testing](../../guides/testing.md)
