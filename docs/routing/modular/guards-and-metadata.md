# Guards and metadata

Decorators that protect a route and describe it in the OpenAPI schema.

## Guards

`@UseGuard(*guards)` works on a controller (every method) or on one method. Each guard is added as a
FastAPI `Depends`, so it declares the parameters it needs and raises to reject the call:

```python filename="src/apps/admin/admin_controller.py"
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

## Middleware decorator

`@Middleware(*middlewares)` behaves the same way: these are FastAPI dependencies, not ASGI
middleware. For real ASGI middleware use `useMiddlewares` in
[Config](../../reference/config.md) or [Middleware and security](../../guides/middleware-and-security.md).

## Route metadata

`@UseRoute(...)` sets OpenAPI metadata. It does not change the path.

| Argument | Meaning |
|---|---|
| `name` | route name |
| `tags` | OpenAPI tags |
| `summary`, `description` | text in the API reference |
| `deprecated` | mark the operation deprecated |
| `include_in_schema` | hide the route from the schema |
| `operation_id` | explicit operation id |
| `openapi_extra` | extra OpenAPI fields |

## Responses

`@UseResponse(...)` sets `status_code`, `response_class`, `response_model`, `responses` and the
serialization options.

```python
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller(prefix="/users")
class UserController:
    @UseRoute(summary="List users", tags=["users"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

The generated API reference is served at `/docs` unless `useDocs = False`.

## Next steps

- [Dependency injection](dependency-injection.md)
- [API routes](../fbr/handlers/README.md): the same options for file-based handlers
