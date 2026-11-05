# Страницы ошибок

Запрос, который не удался, должен по-прежнему отвечать так же, как и остальная часть вашего сайта: страница вашими словами для посетителя, та же ошибка, что и JSON для API-клиента. Nexy отвечает на оба, и каждый ответ заменяется одним файлом.

Эта страница представляет собой карту: какой файл соответствует какому статусу и как сделать свой первый. Страницы папки получают [свою собственную страницу](folder-pages.md).

## Одна неудача, два ответа

```diagram filename="кто отвечает на неудавшийся запрос"
a request that fails
      │
      ├── a browser (Accept: text/html)              ──►  an HTML page
      └── an API client (Accept: application/json)   ──►  {"detail": "…"}  with the same status

the HTML page
      ├── the deepest folder of the URL that holds a file   ──►  your file
      └── no folder of the chain holds one                 ──►  the built-in page
```

## Ваша первая страница

Создайте `src/routes/notfound.nexy` и напишите, что должен прочитать посетитель:

```nexy filename="источник/маршруты/notfound.nexy"
---
title: Page not found
---
<h1>Page not found</h1>
<p>The page moved or never existed. <a href="/">Back home</a>.</p>
```

Сохраните и запросите URL-адрес, который ничего не обслуживает:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/nowhere
# HTTP/1.1 404 Not Found
```

Файл в корне маршрутов отвечает за весь проект; копия в папке отвечает только этой папке и [остальное сохраняет как есть](folder-pages.md). Без какого-либо файла Nexy отображает встроенную стилизованную страницу.

## Какой файл отвечает

| Файл | Ответы |
|---|---|
| `notfound.nexy` | `404` для своего каталога |
| `errors.nexy` | `500` для своего каталога |
| `forbidden.nexy` | `403` для своего каталога |
| `unauthorized.nexy` | `401` для своего каталога |
| `loading.nexy` | зарезервировано; пока нет эффекта времени выполнения |

| Ситуация | Ответ |
|---|---|
| Ни один маршрут не соответствует | `404` |
| Динамический сегмент невозможно преобразовать в его аннотацию | `404` |
| Необработанное исключение на странице или в обработчике API | `500` |
| `raise HTTPException(status_code=403)` | статус, который вы подняли, в формате HTML или JSON |
| `notFound()`, `forbidden()`, `unauthorized()` | `404`, `403`, `401`, из любого места запроса |
| `redirect()`, `permanentRedirect()` | настоящий редирект без страницы с ошибками |

## Оставить страницу или ответить из кода

`redirect`, `permanentRedirect`, `notFound`, `forbidden` и `unauthorized` вызывают исключение HTTP, поэтому один и тот же вызов работает на странице `.nexy`, обработчике API, модульном контроллере, защите и `dependencies.py`. На клиенте они имеют одинаковые имена (`@nexy/client`).

```nexy filename="src/маршруты/сообщения/[слизень].nexy"
---
from nexy import notFound, redirect

from src.posts import find

slug: prop[str]
post = find(slug)
if post is None:
    notFound()
if post.moved_to:
    redirect(post.moved_to)
---
<h1>{{ post.title }}</h1>
```

| Позвонить | Ответить |
|---|---|
| `redirect(url)` | `307`; `redirect(url, status=303)` превращает POST в GET после формы |
| `permanentRedirect(url)` | `308`; браузеры и поисковые системы запоминают это |
| `notFound(detail=None)` | `404`: страница `notfound` или JSON для API-клиента |
| `forbidden(detail=None)` | `403`: посетитель известен, но может не видеть это |
| `unauthorized(detail=None, scheme=None)` | `401`; `scheme="Bearer"` добавляет `WWW-Authenticate` |

Перенаправление отвечает с заголовком `Location` и без страницы, а также клиенту API. Создайте пункт назначения на основе ценностей, которым вы доверяете: `redirect(request.query_params["next"])` отправляет посетителей туда, где указано в ссылке. Пункт назначения с разрывом строки отклоняется.

Охранник защищает целую папку:

```python filename="src/routes/private/dependents.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

## HTML или JSON

Одно и то же исключение отвечает по-разному в зависимости от того, кто спрашивает:

- Браузер (`Accept: text/html`) получает HTML-страницу. Детали экранируются HTML, поэтому сообщение, созданное на основе пользовательского ввода, не может внедрить разметку.
- Клиент, который запрашивает JSON, а не страницу (`Accept: application/json`), получает `{"detail": "..."}` с тем же кодом состояния.

```python filename="src/маршруты/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=403, detail="Out of range")
    return {"id": id}
```

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!ПРИМЕЧАНИЕ]
> клиент, который отправляет `Accept: */*` (по умолчанию `curl` и многие HTTP-библиотеки), получает HTML-страницу. Установите `Accept: application/json` для ошибок JSON.

## Необработанные исключения

Исключение, при котором ничего не обрабатывается, регистрируется один раз, за исключением того, откуда оно пришло и код вокруг него, и на него дается ответ в соответствии с режимом.

| | `nx dev` | `nx start` |
|---|---|---|
| Браузер | страница с ошибкой, строки вашего кода, вызвавшие ее, и полная трассировка | встроенной `500` страницы (или вашей `errors.nexy`) со ссылкой |
| Клиент JSON | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Журнал сервера | исключение и строки вашего кода | исключение и вся трассировка с той же ссылкой |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

Ссылка состоит из восьми символов, новых для каждой неудачи. Посетитель может процитировать его, и вы найдете обратную трассировку, выполнив поиск в журнале. Ни исключение, ни код не доходят до посетителя в рабочей среде. Пользовательский `errors.nexy` заменяет только страницу; строка журнала остается.

## Ошибки валидации

Отсутствует заголовок, параметр запроса или поле тела ответа `422` с телом JSON FastAPI для каждого клиента. См. [Проверка и ошибки](../handlers/validation-and-errors.md).

## Следующие шаги

- [Страницы с ошибками в папке](folder-pages.md): ваша собственная ошибка 404, 403 или 401 в одной папке.
- [Динамические маршруты](../pages/dynamic-routes.md)
- [Маршруты API](../handlers/README.md)
- [Тестирование](../../../guides/testing.md)
