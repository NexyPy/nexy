# Nexy and NestJS

The modular router is inspired by NestJS: controllers, modules and constructor injection. It is a
thin layer over FastAPI, so it does not try to reproduce all of NestJS. This page lists both sides.

## What matches

| NestJS | Nexy |
|---|---|
| `@Controller('users')` | `@Controller("/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` with the same four class attributes |
| `@Injectable()` | `@Injectable()` |
| Constructor injection | `__init__` parameters resolved from type annotations |
| Singleton, request and transient scopes | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (a FastAPI dependency) |
| `@ApiOperation`, `@ApiResponse` (Swagger) | `@UseRoute`, `@UseResponse` (OpenAPI, served at `/docs`) |
| WebSocket gateways | `async def SOCKET(...)` on a controller |
| DTO validation (`class-validator`) | Pydantic models, native to FastAPI |
| Circular dependency detection | `RecursionError` naming the class |

The same controller and its injected service, NestJS first:

```ts filename="users.controller.ts"
@Injectable()
export class UsersService {
  findAll() {
    return [{ id: 1, name: "Ada" }];
  }
}

@Controller("users")
export class UsersController {
  constructor(private readonly users: UsersService) {}

  @Get()
  findAll() {
    return this.users.findAll();
  }
}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller, Injectable


@Injectable()
class UserService:
    def find_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]


@Controller("/users")
class UserController:
    def __init__(self, users: UserService) -> None:
        self.users = users

    async def get(self) -> list[dict]:
        return self.users.find_all()
```

## What differs

- Handlers are methods named after the HTTP verb (`get`, `post`...), one per controller.
- Guards and middleware decorators are FastAPI `Depends`, not classes with `canActivate`.
- Parameters (`@Body`, `@Param`, `@Query`) are FastAPI parameters: type annotations, `Query`, `Path`,
  `Body`.
- Pipes are Pydantic validation and FastAPI dependencies.

`@Query()`, a DTO and a guard class become an annotation, a Pydantic model and a function:

```python filename="src/apps/posts/post_controller.py"
from fastapi import Header, HTTPException, Query
from pydantic import BaseModel
from nexy.decorators import Controller, UseGuard


class NewPost(BaseModel):
    title: str


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller("/posts")
@UseGuard(require_token)
class PostController:
    async def get(self, limit: int = Query(10)) -> list[dict]:
        return []

    async def post(self, body: NewPost) -> dict:
        return {"title": body.title}
```

## What is missing

| NestJS feature | Status in Nexy |
|---|---|
| Custom providers (`useValue`, `useFactory`, `useClass`, string tokens) | not available: only `@Injectable()` classes |
| Injecting by interface or abstract class | not available |
| Module encapsulation | not enforced: the container is process-wide, `exports` only controls eager resolution |
| Dynamic and global modules (`forRoot`, `@Global`) | not available |
| Lifecycle hooks (`onModuleInit`, `onApplicationShutdown`) | not available |
| Interceptors | use ASGI middleware (`useMiddlewares`) or dependencies |
| Exception filters | use FastAPI exception handlers |
| Testing module with provider overrides | no public API; use FastAPI `dependency_overrides` and `TestClient` |
| Config module, scheduling, queues, CQRS, microservices, caching | not part of Nexy; use the Python ecosystem |

In place of a `useFactory` provider, a plain function behind `Depends`, which a test overrides with
`dependency_overrides`:

```python filename="src/apps/reports/report_controller.py"
from fastapi import Depends
from nexy.decorators import Controller


def get_settings() -> dict:
    return {"currency": "EUR"}


@Controller("/reports")
class ReportController:
    async def get(self, settings: dict = Depends(get_settings)) -> dict:
        return {"currency": settings["currency"]}
```

## When to pick it

Pick the modular router when you want a class-based structure with injection for a larger API.
Pick the file-based router when the URL structure is the organising principle. Both are scaffolded
by `nx new`, run on the same FastAPI application, and can coexist.

> [!NOTE]
> the missing items above are the honest gap. If you need `useFactory` providers
> or overridable providers in tests today, keep the logic in plain functions and FastAPI
> `Depends`, which compose and override naturally.

## Next steps

- [Dependency injection](dependency-injection.md)
- [Guards and metadata](guards-and-metadata.md)
- [Testing](../../guides/testing.md)
