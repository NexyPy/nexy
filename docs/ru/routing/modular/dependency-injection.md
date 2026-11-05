# Внедрение зависимостей

Nexy разрешает зависимости конструкторов для контроллеров и сервисов. Класс соглашается с `@Injectable()`.

## Внедрить сервис

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

Зарегистрируйте контроллер в модуле. Листинг службы в `providers` дополнительно разрешает ее при запуске:

```python filename="src/apps/users/users_module.py"
from nexy.decorators import Module
from .user_controller import UserController
from .user_service import UserService


@Module()
class UsersModule:
    controllers = [UserController]
    providers = [UserService]
```

## Как работает разрешение

- Каждый параметр `__init__` определяется на основе его аннотации типа ****. Аннотация должна быть классом `@Injectable()` или параметр должен иметь значение по умолчанию; в противном случае разрешение повышает `ValueError`.
- Контроллеры создаются с помощью `Container.resolve()` при запуске.
- Цикл зависимостей вызывает `RecursionError` имя класса.
- Сервисы могут внедрять другие сервисы на любую глубину.

## Области применения

```python
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class CurrentUser: ...
```

| Область применения | Срок службы |
|---|---|
| `Scope.SINGLETON` (по умолчанию) | один экземпляр для всего процесса |
| `Scope.REQUEST` | один экземпляр на каждый контекст запроса |
| `Scope.TRANSIENT` | новый экземпляр при каждом разрешении |

## Контейнер

```python
from nexy.decorators import Container

service = Container.resolve(UserService)
```

Самостоятельное создание класса `@Injectable()` повышает `TypeError`: контейнер владеет своим жизненным циклом. Используйте `Container.resolve(...)` или получите класс через другой конструктор.

`Container.clear_request_scope()` удаляет экземпляры текущего запроса.

## Параметры маршрута

FastAPI `Depends` работает как обычно для параметров обработчика, после внедрения конструктора:

```python
from fastapi import Depends


def get(self, limit: int = Depends(pagination)) -> list[dict]: ...
```

## Пределы

Контейнер охватывает весь процесс. Провайдеры не изолированы для каждого модуля, `exports` только решает, каких провайдеров с готовностью разрешает импортирующий модуль, и не существует общедоступного API для замены провайдера в тестах. См. [Nexy и NestJS](vs-nestjs.md) для полного сравнения.

## Следующие шаги

- [Защитники и метаданные](guards-and-metadata.md)
- [Тестирование](../../guides/testing.md)
