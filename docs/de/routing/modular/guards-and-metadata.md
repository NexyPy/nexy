# Guards und Metadaten

Dekoratoren, die eine Route schützen und sie im OpenAPI-Schema beschreiben.

## Wachen

`@UseGuard(*guards)` funktioniert auf einem Controller (jede Methode) oder auf einer Methode. Jeder Guard wird als FastAPI `Depends` hinzugefügt, sodass er die benötigten Parameter deklariert und auslöst, um den Aufruf abzulehnen:

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

## Middleware-Dekorateur

`@Middleware(*middlewares)` verhält sich genauso: Dies sind FastAPI Abhängigkeiten, keine ASGI-Middleware. Für echte ASGI-Middleware verwenden Sie `useMiddlewares` in [Config](../../reference/config.md) oder [Middleware und Sicherheit](../../guides/middleware-and-security.md).

## Routenmetadaten

`@UseRoute(...)` legt OpenAPI Metadaten fest. Es ändert den Pfad nicht.

| Argument | Bedeutung |
|---|---|
| `name` | Routenname |
| `tags` | OpenAPI Tags |
| `summary`, `description` | Text in der API-Referenz |
| `deprecated` | Markieren Sie den Vorgang als veraltet |
| `include_in_schema` | Die Route aus dem Schema ausblenden |
| `operation_id` | explizite Operations-ID |
| `openapi_extra` | zusätzliche OpenAPI Felder |

## Antworten

`@UseResponse(...)` legt `status_code`, `response_class`, `response_model`, `responses` und die Serialisierungsoptionen fest.

```python
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller(prefix="/users")
class UserController:
    @UseRoute(summary="List users", tags=["users"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

Die generierte API-Referenz wird unter `/docs` bereitgestellt, sofern nicht `useDocs = False`.

## Nächste Schritte

- [Abhängigkeitsinjektion](dependency-injection.md)
- [API-Routen](../fbr/handlers/README.md): die gleichen Optionen für dateibasierte Handler
