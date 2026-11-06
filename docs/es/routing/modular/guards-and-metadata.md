# Guardias y metadatos

Decoradores que protegen una ruta y la describen en el esquema OpenAPI.

## guardias

`@UseGuard(*guards)` funciona en un controlador (cada método) o en un método. Cada guardia se agrega como un FastAPI `Depends`, por lo que declara los parámetros que necesita y levanta para rechazar la llamada:

```python filename="src/apps/admin/admin_controller.py"
from fastapi import Header, HTTPException
from nexy.decorators import Controller, UseGuard


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller("/admin")
@UseGuard(require_token)
class AdminController:
    async def get(self) -> dict:
        return {"ok": True}
```

## decorador de middleware

`@Middleware(*middlewares)` se comporta de la misma manera: estas son FastAPI dependencias, no middleware ASGI. Para middleware ASGI real, utilice `useMiddlewares` en [Configuración](../../reference/config.md) o [Middleware y seguridad](../../guides/middleware-and-security.md).

## Metadatos de ruta

`@UseRoute(...)` establece OpenAPI metadatos. No cambia el camino.

| Argumento | Significado |
|---|---|
| `name` | nombre de la ruta |
| `tags` | OpenAPI etiquetas |
| `summary`, `description` | texto en la referencia API |
| `deprecated` | marcar la operación como obsoleta |
| `include_in_schema` | ocultar la ruta del esquema |
| `operation_id` | identificación de operación explícita |
| `openapi_extra` | campos OpenAPI adicionales |

## Respuestas

`@UseResponse(...)` establece `status_code`, `response_class`, `response_model`, `responses` y las opciones de serialización.

```python
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller("/users")
class UserController:
    @UseRoute(summary="List users", tags=["users"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

La referencia de API generada se sirve en `/docs` a menos que `useDocs = False`.

## Próximos pasos

- [Inyección de dependencia](dependency-injection.md)
- [Rutas API](../fbr/handlers/README.md): las mismas opciones para controladores basados en archivos
