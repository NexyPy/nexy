# Исходя из другой структуры

Nexy — это FastAPI плюс маршрутизация на основе файлов, страницы, отображаемые на сервере, и дополнительные острова React, Vue, Svelte, Solid или Preact. На этой странице отображено то, что вы уже знаете.

## Из FastAPI

| FastAPI | Некси |
|---|---|
| `@app.get("/users")` в модуле, который вы импортируете | `GET` функцию в `src/routes/users.py` |
| `app.include_router(router)` | путь к файлу — это URL-адрес; нечего регистрировать |
| Параметр пути `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | еще `Depends(...)`: обработчики — это FastAPI обработчики |
| Jinja2 `TemplateResponse` | страница `.nexy` рядом с конечной точкой |
| Запустите с помощью `uvicorn main:app` | `nx dev`, затем `nx build && nx start` |

Все под `src/routes/*.py` обычное FastAPI: зависимости, Pydantic модели, промежуточное ПО и `/docs` продолжают работать.

## Из Next.js

| Next.js | Некси |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` или `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (владеет `<html>`) | `src/routes/layout.tsx` с `useCSR = True` (React) или `src/routes/layout.nexy` в режиме сервера |
| вложенный `layout.tsx` | вложенный `layout.tsx` / `layout.vue` / `layout.svelte` в режиме клиента, вложенный `layout.nexy` в режиме сервера |
| `use client` компоненты на странице сервера | [острова](../rendering/islands.md) в режиме сервера |
| Обработчики маршрутов `route.ts` | `src/routes/api/x.py`, написанные на Python |
| `(group)` папки | то же: `(group)/` |
| Действия сервера | [`@Action`](../guides/actions.md) функции, вызываемые из формы или как типизированные клиентские функции |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

Бэкэнд – Python, поэтому ваш API использует общий код с вашими данными и работой машинного обучения. Клиентские компоненты объединяются в виде островов, а не в виде полностраничного React дерева.

## Из серверов Express или Node

| Экспресс | Некси |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` с `async def GET(id)` |
| `app.use(middleware)` | FastAPI промежуточное программное обеспечение, зарегистрированное от `nexyconfig.py` |
| `res.json(obj)` | возвращает словарь или Pydantic модель |
| Просмотры EJS/Pug | `.nexy` (Jinja2) страниц |
| `npm run dev` | `nx dev` |

## Выбор роутера

| Используйте | Когда |
|---|---|
| Файловый маршрутизатор | страниц и конечных точек, отображаемых из файлов; по умолчанию |
| Модульные маршрутизаторы, | контроллеры, модули и внедрение зависимостей, в стиле NestJS |

Оба поддерживаются `nx new` и проходят одни и те же сквозные тесты. См. [Маршрутизация](../routing/README.md) и [Модульная маршрутизация](../routing/modular/README.md).

## Где дальше

- [Быстрый старт](quick-start.md): создайте проект и запустите его
- [Структура проекта](project-structure.md): место каждого файла
- [Маршрутизация](../routing/README.md): выберите маршрутизатор.
