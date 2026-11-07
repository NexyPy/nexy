# Некси и NestJS

Модульный маршрутизатор вдохновлен NestJS: контроллеры, модули и внедрение конструктора. Это тонкий слой над FastAPI, поэтому он не пытается воспроизвести весь NestJS. На этой странице перечислены обе стороны.

## Что соответствует

| NestJS | Некси |
|---|---|
| `@Controller('users')` | `@Controller("/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` с теми же четырьмя атрибутами класса |
| `@Injectable()` | `@Injectable()` |
| Инъекция конструктора | `__init__` параметры, разрешенные из аннотаций типов |
| Синглтон, запросы и временные области | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (зависимость FastAPI) |
| `@ApiOperation`, `@ApiResponse` (Сваггер) | `@UseRoute`, `@UseResponse` (OpenAPI, обслуживается в `/docs`) |
| WebSocket шлюзы | `async def SOCKET(...)` на контроллере |
| Проверка DTO (`class-validator`) | Pydantic модели, родные для FastAPI |
| Обнаружение циклических зависимостей | `RecursionError` присвоение имени классу |

Тот же контроллер и его внедренный сервис, сначала NestJS:

```ts filename="пользователи.controller.ts"
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

## Чем отличается

- Обработчики - это методы, названные в честь глагола HTTP (`get`, `post`...), по одному на каждый контроллер.
- Охранники и декораторы промежуточного программного обеспечения - это FastAPI `Depends`, а не классы с `canActivate`.
- Параметры (`@Body`, `@Param`, `@Query`) - это FastAPI параметры: аннотации типов, `Query`, `Path`, `Body`.
- Каналы - это Pydantic проверка и FastAPI зависимости.

`@Query()`, DTO и охранный класс становятся аннотацией, моделью Pydantic и функцией:

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

## Чего не хватает

| NestJS функция | Статус в Некси |
|---|---|
| Пользовательские поставщики (`useValue`, `useFactory`, `useClass`, строковые токены) | недоступно: только `@Injectable()` классов |
| Внедрение через интерфейс или абстрактный класс | не доступен |
| Инкапсуляция модуля | не применяется: контейнер распространяется на весь процесс, `exports` контролирует только активное разрешение |
| Динамические и глобальные модули (`forRoot`, `@Global`) | не доступен |
| Перехватчики жизненного цикла (`onModuleInit`, `onApplicationShutdown`) | не доступен |
| Перехватчики | используйте промежуточное программное обеспечение ASGI (`useMiddlewares`) или зависимости |
| Фильтры исключений | используйте обработчики исключений FastAPI |
| Модуль тестирования с переопределением провайдера | нет общедоступного API; используйте FastAPI `dependency_overrides` и `TestClient` |
| Модуль конфигурации, планирование, очереди, CQRS, микросервисы, кеширование | не является частью Nexy; использовать экосистему Python |

Вместо поставщика `useFactory` - простая функция, стоящая за `Depends`, которую тест переопределяет с помощью `dependency_overrides`:

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

## Когда выбирать

Выбирайте модульный маршрутизатор, если вам нужна структура на основе классов с внедрением более крупного API. Выбирайте файловый маршрутизатор, если структура URL является принципом организации. Оба созданы `nx new`, запускаются в одном и том же приложении FastAPI и могут сосуществовать.

> [!NOTE]
> недостающие элементы выше - это честный пробел. Если сегодня в тестах вам нужны поставщики `useFactory` или переопределяемые поставщики, сохраните логику в простых функциях и FastAPI `Depends`, которые компонуются и переопределяются естественным образом.

## Следующие шаги

- [Внедрение зависимостей](dependency-injection.md)
- [Охранники и метаданные](guards-and-metadata.md)
- [Тестирование](../../guides/testing.md)
