# Модульная маршрутизация

Модульная маршрутизация использует классы с декораторами вместо файлов в `src/routes/`: контроллеры обрабатывают запросы, модули группируют их, а провайдеры внедряются. Смонтируйте полученный `APIRouter` с `useRouter` в `nexyconfig.py`.

**Прежде чем начать:** проект Nexy и одна рабочая страница. Модульный маршрутизатор заменяет файловый маршрутизатор, поэтому сначала прочтите [Маршрутизация](../README.md), если вы еще не выбрали маршрутизатор.

| Страница | Что он охватывает |
|---|---|
| Эта страница | Монтируем модуль, пишем контроллер, группируем контроллеры |
| [Внедрение зависимостей](dependency-injection.md) | `@Injectable`, области видимости, контейнер |
| [Охранники и метаданные](guards-and-metadata.md) | `@UseGuard`, `@Middleware`, `@UseRoute`, `@UseResponse` |
| [Некси и NestJS](vs-nestjs.md) | Что соответствует NestJS, а что нет |

## Настройте маршрутизатор

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!NOTE]
> Маршрутизация на основе файлов продолжает работать. Если `src/routes/` существует, оно сканируется, даже если установлено `useRouter`.

## Напишите контроллер

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

Методы сопоставляются по имени без учета регистра: `get`, `post`, `put`, `patch`, `delete`, `options`, `head`, `trace`.

Контроллер объявляет один обработчик для каждого метода HTTP; дубликат поднимается при запуске. Первый аргумент `@Controller("/users")` — это путь, по которому отвечает каждый обработчик, `/users/`. `async def SOCKET(...)` на контроллере регистрирует WebSocket по тому же пути.

## Группа контроллеров в модуле

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` возвращает `APIRouter`. `controllers` требуется; `providers`, `imports` и `exports` являются необязательными. Импортированные модули монтируются как подмаршрутизаторы, а их экспортированные поставщики разрешаются при запуске.

## Виды с контроллера

Контроллер может вернуть страницу. `useViews` отображает представление `.nexy`; вложите одно в другое, чтобы обернуть его в макет:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller()
class AppController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/app_view.nexy"),
        })
```

См. [Макеты](../fbr/layouts/README.md).

## Пример

См. `examples/Modular/api/minimal/`.

## Следующие шаги

- [Внедрение зависимостей](dependency-injection.md): сервисы и области действия
- [Охранники и метаданные](guards-and-metadata.md): защищают и документируют маршруты
- [Маршрутизация](../README.md): файловый маршрутизатор
- [Конфигурация](../../reference/config.md): все опции, включая `useRouter`
