# Маршрутизация на основе файлов

Маршрут — это файл. URL-адрес — это путь к файлу относительно `src/routes/` без расширения.

## Файл по URL

| Файл | URL-адрес |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` сопоставляется со своим каталогом, а не с `/index`. Каталог в скобках представляет собой **группу**: он упорядочивает файлы, не отображаясь в URL-адресе.

В клиентском режиме файлы подкачки имеют вид `.tsx`, `.vue` или `.svelte` вместо `.nexy`; правила URL такие же.

Два файла этой таблицы: страница, считывающая свой сегмент, и обработчик, отвечающий на JSON.

```nexy filename="src/маршруты/блог/[слизняк].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/routes/api/users.py"
async def GET():
    return {"users": []}
```

## Два режима

`useCSR` решает, что это за страницы. Их нельзя смешивать в одном проекте: Nexy отказывается запускаться, когда страница сервера находится рядом с клиентским маршрутом.

| Режим | Страницы | Корневая раскладка | См. |
|---|---|---|---|
| Сервер (`useCSR = False`) | `.nexy`, `.md`, `.mdx` | `layout.nexy` | [Режим сервера и режим клиента](modes.md) |
| Клиент (`useCSR = True`) | файлы фреймворка | `layout.tsx` | [макет.tsx](../../views/react/differences.md) |

Файлы `.py` являются обработчиками API в обоих режимах.

Переключатель — это одна строка `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True  # client mode: src/routes/*.tsx are the pages
```

## Что не является маршрутом

- Зарезервированные имена файлов: `layout.*`, `loading.nexy`, `errors.nexy`, `notfound.nexy`, `dependencies.py`, `middleware.py`, `__init__.py`.
- Файлы и папки, начинающиеся с `_` или `.`: используйте их для частичных изображений и черновиков.
- Расширения, которые не активны для вашего проекта. Файл, расширение которого неактивно, пропускается с предупреждением.

```text
src/routes/
├─ layout.nexy          wraps the pages, not a route
├─ middleware.py        wraps the requests, not a route
├─ index.nexy           /
├─ _card.nexy           a partial: no URL
└─ .draft.nexy          a draft: no URL
```

## Один файл на каждый URL

Регистрируются два файла, которые разрешаются по одному и тому же URL-адресу. Не создавайте `blog.nexy` рядом с `blog/index.nexy` и не смешивайте `index.nexy` и `index.py` для одного и того же пути. Выберите один.

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: delete one of the two
```

## В этом разделе

| Папка | Что он охватывает |
|---|---|
| [страницы/](pages/README.md) | страницы, [динамические маршруты](pages/dynamic-routes.md), группы маршрутов |
| [макеты/](layouts/README.md) | одна страница на каждый тип файла макета |
| [обработчики/](handlers/README.md) | `.py` обработчики, проверка и ошибки |
| [зависимости/](dependencies/README.md) | `dependencies.py`, охранники |
| [промежуточное программное обеспечение/](middleware/README.md) | `middleware.py` |
| [ошибки/](errors/README.md) | не найденные страницы и страницы ошибок |
| [навигация/](navigation/linking-and-navigating.md) | ссылки, крючки |
| [в реальном времени/](realtime/websocket.md) | WebSocket |
| [наследование](inheritance.md) | правила наследования в одной таблице |

## Следующие шаги

- [Режим сервера и режим клиента](modes.md)
- [Макеты](layouts/README.md)
- [Модульная маршрутизация](../modular/README.md)
