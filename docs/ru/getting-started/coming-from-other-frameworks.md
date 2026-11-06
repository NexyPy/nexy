# Исходя из другой структуры

Nexy — это FastAPI плюс маршрутизация на основе файлов, страницы, отображаемые на сервере, и дополнительные острова React, Vue, Svelte, Solid или Preact. На этой странице отображено то, что вы уже знаете.

У каждого приведенного ниже фреймворка также есть собственная страница, для каждой задачи, с известным вам кодом, а затем кодом Nexy:

| Python | Бэкэнд | Полный стек JavaScript |
|---|---|---|
| [FastAPI](../coming-from/fastapi.md) | [Экспресс](../coming-from/express.md), [Фастификация](../coming-from/fastify.md) | [Next.js](../coming-from/nextjs.md), [Remix](../coming-from/remix.md) |
| [Flask](../coming-from/flask.md) | [Элизия](../coming-from/elysia.md), [Хоно](../coming-from/hono.md) | [Следующий](../coming-from/nuxt.md) |
| [Django](../coming-from/django.md) | [NestJS](../coming-from/nestjs.md), [Пружинная загрузка](../coming-from/spring-boot.md) | [SvelteKit](../coming-from/sveltekit.md) |
| | [Laravel](../coming-from/laravel.md), [Ruby on Rails](../coming-from/rails.md) | [Astro](../coming-from/astro.md) |

## Из FastAPI

| FastAPI | Некси |
|---|---|
| `@app.get("/users")` в импортируемом модуле | Функция `GET` в `src/routes/users.py` |
| `app.include_router(router)` | путь к файлу — это URL-адрес; нечего регистрироваться |
| Параметр пути `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | еще `Depends(...)`: обработчики — это FastAPI обработчики |
| Jinja2 `TemplateResponse` | страница `.nexy` рядом с конечной точкой |
| Запустите с помощью `uvicorn main:app` | `nx dev`, затем `nx build && nx start` |

Все под `src/routes/*.py` обычное FastAPI: зависимости, Pydantic модели, промежуточное ПО и `/docs` продолжают работать.

Та же конечная точка, до и после:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/маршруты/пользователи/[id].py"
async def GET(id: int):
    return {"id": id}
```

## Из Next.js

| Next.js | Некси |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` или `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (владеет `<html>`) | `src/routes/layout.tsx` с `useCSR = True` (React) или `src/routes/layout.nexy` в режиме сервера |
| вложенный `layout.tsx` | вложенные `layout.tsx` / `layout.vue` / `layout.svelte` в режиме клиента, вложенные `layout.nexy` в режиме сервера |
| `use client` компоненты на странице сервера | [острова](../rendering/islands.md) в режиме сервера |
| Обработчики маршрутов `route.ts` | `src/routes/api/x.py`, написано в Python |
| `(group)` папки | то же самое: `(group)/` |
| Действия сервера | [`@Action`](../guides/actions.md) функции, вызываемые из формы или как типизированные клиентские функции |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

Бэкэнд – Python, поэтому ваш API использует общий код с вашими данными и работой машинного обучения. Клиентские компоненты объединяются в виде островов, а не в виде полностраничного React дерева.

Страница Next.js перемещается почти как есть, а ее компонент `"use client"` становится островком серверной страницы:

```tsx filename="src/маршруты/блог/[слизень].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

```nexy filename="src/маршруты/блог/[слизняк].nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```

## Из серверов Express или Node

| Экспресс | Некси |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` с `async def GET(id)` |
| `app.use(middleware)` | FastAPI промежуточное программное обеспечение, зарегистрированное от `nexyconfig.py` |
| `res.json(obj)` | вернуть dict или модель Pydantic |
| EJS / Просмотры мопсов | `.nexy` (Jinja2) страниц |
| `npm run dev` | `nx dev` |

`app.use(...)` становится полем `nexyconfig.py`, а `res.json(...)` становится возвращаемым значением:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/маршруты/пользователи/[id].py"
async def GET(id: int):
    return {"id": id, "name": "Ada"}  # res.json({ id, name })
```

## Выбор роутера

| Использование | Когда |
|---|---|
| Файловый маршрутизатор | страницы и конечные точки, сопоставленные с файлами; по умолчанию |
| Модульный маршрутизатор | контроллеры, модули и внедрение зависимостей, в стиле NestJS |

Модульный маршрутизатор в двух файлах: контроллер и модуль `nexyconfig.py`, на который указывает `useRouter = AppModule`:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller


@Controller()
class AppController:
    async def get(self):
        return {"message": "Hello"}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

Оба поддерживаются `nx new` и проходят одни и те же сквозные тесты. См. [Маршрутизация](../routing/README.md) и [Модульная маршрутизация](../routing/modular/README.md).

## Где дальше

- [Быстрый старт](quick-start.md): создайте проект и запустите его
- [Структура проекта](project-structure.md): место каждого файла
- [Маршрутизация](../routing/README.md): выберите маршрутизатор
