# Guardas e metadados

Decoradores que protegem uma rota e a descrevem no esquema OpenAPI.

## Guardas

`@UseGuard(*guards)` funciona em um controlador (todos os métodos) ou em um método. Cada guarda é adicionado como um FastAPI `Depends`, então ele declara os parâmetros necessários e aumenta para rejeitar a chamada:

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

## Decorador de middleware

`@Middleware(*middlewares)` se comporta da mesma maneira: são dependências FastAPI, não middleware ASGI. Para middleware ASGI real, use `useMiddlewares` em [Configuração](../../reference/config.md) ou [Middleware e segurança](../../guides/middleware-and-security.md).

## Metadados de rota

`@UseRoute(...)` define OpenAPI metadados. Isso não muda o caminho.

| Argumento | Significado |
|---|---|
| `name` | nome da rota |
| `tags` | OpenAPI tags |
| `summary`, `description` | texto na referência da API |
| `deprecated` | marque a operação obsoleta |
| `include_in_schema` | ocultar a rota do esquema |
| `operation_id` | ID de operação explícita |
| `openapi_extra` | OpenAPI campos extras |

## Respostas

`@UseResponse(...)` define `status_code`, `response_class`, `response_model`, `responses` e as opções de serialização.

```python
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller("/users")
class UserController:
    @UseRoute(summary="List users", tags=["users"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

A referência de API gerada é veiculada em `/docs`, a menos que `useDocs = False`.

## Próximas etapas

- [Injeção de dependência](dependency-injection.md)
- [Rotas API](../fbr/handlers/README.md): as mesmas opções para manipuladores baseados em arquivo
