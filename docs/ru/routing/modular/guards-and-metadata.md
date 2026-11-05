# Охранники и метаданные

Декораторы, защищающие маршрут и описывающие его в схеме OpenAPI.

## Охранники

`@UseGuard(*guards)` работает на контроллере (каждый метод) или на одном методе. Каждый охранник добавляется как FastAPI `Depends`, поэтому он объявляет необходимые ему параметры и выдает их для отклонения вызова:

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

## Декоратор промежуточного программного обеспечения

`@Middleware(*middlewares)` ведет себя таким же образом: это зависимости FastAPI, а не промежуточное ПО ASGI. Для реального промежуточного программного обеспечения ASGI используйте `useMiddlewares` в [Конфигурация](../../reference/config.md) или [Промежуточное программное обеспечение и безопасность](../../guides/middleware-and-security.md).

## Метаданные маршрута

`@UseRoute(...)` устанавливает метаданные OpenAPI. Это не меняет путь.

| Аргумент | Значение |
|---|---|
| `name` | название маршрута |
| `tags` | OpenAPI теги |
| `summary`, `description` | текст в ссылке API |
| `deprecated` | отметить операцию как устаревшую |
| `include_in_schema` | скрыть маршрут из схемы |
| `operation_id` | явный идентификатор операции |
| `openapi_extra` | дополнительные поля OpenAPI |

## Ответы

`@UseResponse(...)` устанавливает `status_code`, `response_class`, `response_model`, `responses` и параметры сериализации.

```python
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller(prefix="/users")
class UserController:
    @UseRoute(summary="List users", tags=["users"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

Сгенерированная ссылка API обслуживается по адресу `/docs`, если только `useDocs = False`.

## Следующие шаги

- [Внедрение зависимостей](dependency-injection.md)
- [Маршруты API](../fbr/handlers/README.md): те же параметры для файловых обработчиков.
