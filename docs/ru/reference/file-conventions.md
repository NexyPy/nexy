# Соглашения о файлах

Зарезервированные имена и правила в `src/routes/`.

## Файлы маршрутов

| Файл | становится |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | маршрут его каталога |
| `about.nexy` | `/about` |
| `[slug].nexy` | динамический сегмент `{slug}` |
| `[...path].nexy` | всеобъемлющий `{path:path}` |
| `(group)/page.nexy` | `/page`: группа не отображается в URL-адресе |
| `name.py` | обработчик API; имена функций `GET`, `POST`, ... — это методы |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | клиентский маршрут, когда платформа включена с помощью `useFF` |

```text
src/routes/
├─ index.nexy           /
├─ about.nexy           /about
├─ (marketing)/
│  └─ pricing.nexy      /pricing
├─ blog/
│  ├─ index.md          /blog
│  └─ [slug].nexy       /blog/{slug}
├─ docs/
│  └─ [...path].nexy    /docs/{path:path}
└─ api/
   └─ users.py          GET /api/users, POST /api/users
```

```python filename="src/routes/api/users.py"
async def GET():
    return {"users": []}


async def POST():
    return {"created": True}
```

## Зарезервированные файлы

| Файл | Роль | Подробности |
|---|---|---|
| `layout.nexy` | режим сервера: оборачивает каждую страницу ниже себя; корневой владеет HTML-документом | [макет.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | клиентский режим (React): корневой владеет HTML-документом, вложенные — обертывают страницы | [макет.tsx](../views/react/differences.md) |
| `layout.vue`, `layout.svelte` | клиентский режим: вложенные макеты | [макет.vue](../views/vue/differences.md), [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | Страница 404 для своего каталога | [Страницы ошибок](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 страниц для своего каталога | [Страницы ошибок](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | Страница 403 для своего каталога | [Страниц ошибок в папке](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | 401 страница для своего каталога | [Страниц ошибок в папке](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | зарезервирован; пока нет эффекта времени выполнения | [Страницы ошибок](../routing/fbr/errors/README.md) |
| `middleware.py` | `async def middleware(request, call_next)` обертка запросов каталога и ниже | [Файлы промежуточного программного обеспечения](../routing/fbr/middleware/README.md) |
| `dependencies.py` | список `dependencies = [fn, ...]` применяется к каталогу и его дочерним элементам | [Зависимости](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python маркер пакета | |
| `favicon.ico` | служил в `/favicon.ico` | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions`, `useUnauthorizedExtensions` и `useLoadingExtensions` резервируют дополнительные расширения для этих имен. См. [Конфигурация](config.md).

Два Python файла таблицы, расположенные рядом в одной папке:

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

И страница, которая отвечает на 404 в своей папке:

```nexy filename="источник/маршруты/notfound.nexy"
<h1>Page not found</h1>
<p><a href="/">Back home</a></p>
```

## Игнорируемые файлы

- Файл или папка, начинающаяся с `_` или `.`: используйте их для партиалов, черновиков и вспомогательных файлов.
- Файл, расширение которого неактивно для проекта: пропускается с предупреждением.

```text
src/routes/
├─ index.nexy           /
├─ _card.nexy           ignored: a partial the pages include
├─ _helpers/            ignored, with everything inside
│  └─ format.py
└─ .draft.nexy          ignored: a draft
```

## Один файл на каждый URL

Регистрируются два файла, которые разрешаются по одному и тому же URL-адресу. Не ставьте `blog.nexy` рядом с `blog/index.nexy`.

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: keep only one of the two
```

## Снаружи `src/routes/`

| Папка | Цель |
|---|---|
| `src/components/` | компоненты, импортированные по страницам; никогда не маршрутизирует |
| `src/apps/` | контроллеры и модули [модульного маршрутизатора](../routing/modular/README.md) |
| `public/` | статические файлы, обслуживаемые в корне: `public/logo.svg` — это `/logo.svg` (также в `/public/`) |
| `__nexy__/` | сгенерированный результат; не совершай |

```text
my-app/
├─ nexyconfig.py
├─ public/
│  └─ logo.svg          /logo.svg
├─ src/
│  ├─ routes/           the routes
│  ├─ components/
│  │  └─ Counter.tsx    imported by pages, never served on its own
│  └─ apps/             the modular router, when you use it
└─ __nexy__/            generated: add it to .gitignore
```

## Следующие шаги

- [Маршрутизация](../routing/README.md)
- [Структура проекта](../getting-started/project-structure.md)
