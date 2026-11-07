# Что такое Некси?

Nexy — это Python фреймворк для полнофункциональных веб-приложений: ваши страницы и ваш API находятся в одном проекте и обслуживаются одним сервером.

## Что вы получаете

- **Страницы в Python.** Файл `.nexy` представляет собой HTML с несколькими строками Python сверху; файл `.md` тоже является страницей. Для рендеринга страницы JavaScript не требуется.
<!-- router:fbr -->
- **API в том же проекте.** Файл `.py` под `src/routes/` отвечает на HTTP-запросы: функция с именем `GET` отвечает на `GET`, функция с именем `POST` отвечает на `POST`.
<!-- /router -->
<!-- router:modular -->
- **API в том же проекте.** Контроллер отвечает на HTTP-запросы: его метод `get` отвечает на `GET`, его метод `post` отвечает на `POST`, а модуль группирует контроллеры и их сервисы.
<!-- /router -->
<!-- router:custom -->
- **API в том же проекте.** Маршрутизатор FastAPI, который у вас уже есть, продолжает отвечать, а страницы и файлы маршрутов `src/routes/` отвечают рядом с ним.
<!-- /router -->
- **Документация по API бесплатна.** Каждый маршрут API отображается в схеме OpenAPI, а Scalar показывает его в виде интерактивной ссылки в `/docs`.
- **Формы, вызывающие Python.** Форма или типизированный вызов из браузера достигают той же функции Python.
- **Фреймворк внешнего интерфейса, когда он вам нужен.** React, Vue, Svelte, Solid или Preact, для одного компонента или для всего сайта.
- **Одна команда для работы, другая для отправки.** `nx dev` перезагружается по мере сохранения; `nx build` готовит производство.

## На чем он построен

Текущая версия 2.2 основана на инструментах, которые вы, возможно, уже знаете:

| Часть | Построен на | Что это значит для тебя |
|---|---|---|
| Сервер и API | [FastAPI](https://fastapi.tiangolo.com/) | маршрут API — это маршрут FastAPI: проверка Pydantic и зависимости работают как обычно |
| Справочник по API | OpenAPI и [Скаляр](https://scalar.com/) | схема находится по адресу `/openapi.json`, ссылка по адресу `/docs` |
| Страницы | Jinja2 | страница `.nexy` использует теги Jinja2, такие как `{{ title }}` |
| Фронтенд (необязательно) | [Vite](https://vite.dev/) | только с интерфейсной платформой, для которой также требуется Node.js |

## Первая страница и первая конечная точка

<!-- router:fbr,custom -->
Страница по адресу `/hello`:

```nexy filename="src/маршруты/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

Конечная точка по адресу `GET /api/items`, указанная в `/docs` без дополнительного кода:

```python filename="src/routes/api/items.py"
from nexy.http import Request


async def GET(request: Request):
    return {"items": []}
```
<!-- /router -->

<!-- router:modular -->
Представление и контроллеры, отвечающие на `/hello/` и `GET /api/items/`. Конечная точка указана по адресу `/docs` без какого-либо дополнительного кода, а URL-адрес без последней косой черты перенаправляет на нее:

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

```python filename="src/apps/hello_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews("src/apps/hello_view.nexy", context={"title": "Hello"})


@Controller("/api/items")
class ItemsController:
    async def get(self):
        return {"items": []}
```

Корневой модуль перечисляет их, а `useRouter = AppModule` в `nexyconfig.py` монтирует его:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .hello_controller import HelloController, ItemsController


@Module()
class AppModule:
    controllers = [HelloController, ItemsController]
```
<!-- /router -->

## Что Nexy оставляет вам

База данных, логин и правила о том, кто и что может делать, принадлежат вашему приложению, поэтому библиотеки выбираете вы. [Базы данных](../guides/databases.md) и [Промежуточное ПО и безопасность](../guides/middleware-and-security.md) показывают, где подключается каждая из них.

## Следующие шаги

- [Установка](installation.md): установите uv и создайте проект
- [Быстрый старт](quick-start.md): запустите, измените страницу, создайте ее
- [Основные понятия](core-concepts.md): несколько слов, которые используются в остальной документации.
