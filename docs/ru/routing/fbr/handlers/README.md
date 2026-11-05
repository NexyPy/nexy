# Обработчики маршрутов

Файл `.py` в папке `src/routes/` является обработчиком API. Путь к файлу — это URL-адрес, и каждая функция, названная в честь метода HTTP, становится конечной точкой.

## Создать конечную точку

```python filename="src/routes/api/items.py"
from nexy.http import Request
from pydantic import BaseModel


class Item(BaseModel):
    name: str


async def GET(request: Request):
    return {"items": []}


async def POST(request: Request, body: Item):
    return {"created": body.name}
```

Этот файл отвечает на `GET /api/items` и `POST /api/items`.

Поддерживаемые имена функций: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `HEAD`. `SOCKET` открывает WebSocket по тому же пути — см. [WebSocket](../realtime/websocket.md).

## HTTP-словарь

Импортируйте то, что нужно обработчику, из `nexy.http`:

```python
from nexy.http import Depends, Header, HTTPException, JSONResponse, Request, status
```

Он предоставляет классы запросов и ответов (`Request`, `Response`, `JSONResponse`, `HTMLResponse`, `PlainTextResponse`, `RedirectResponse`, `StreamingResponse`, `FileResponse`), источники параметров (`Header`, `Query`, `Cookie`, `Path`, `Body`), `Depends`, `BackgroundTasks`, `HTTPException` и `status`. Обработчики, написанные для этого модуля, зависят от контракта Nexy, а не от движка, который их обслуживает. Pydantic модели описывают тела и реакции как обычно.

## Параметры

| Источник | Как это происходит |
|---|---|
| Сегмент пути `[id]` | аргумент функции `id`, преобразованный в его аннотацию |
| Строка запроса | `page: int = 1` |
| Тело JSON | Pydantic аргумент модели |
| FastAPI примитивы | `Depends`, `Header`, `Cookie`, `Form`, `UploadFile` - без изменений |

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

Сегмент пути — `{id}`, поэтому FastAPI проверяет `id: int`. Значение, не являющееся целым числом, отвечает `404`, поскольку динамический маршрут захватывает любой URL-адрес, а URL-адрес, который невозможно преобразовать, не существует. См. [Проверка и ошибки](validation-and-errors.md).

## Ответы

| Возврат | Ответ |
|---|---|
| `dict`, `list`, `BaseModel` | JSON |
| `JSONResponse`, `HTMLResponse`, любой `Response` | точно так, как заявлено |
| `None` | пустой ответ — вместо этого верните `Response` когда статус имеет значение |

Для пользовательского кода состояния или типа контента верните объект ответа:

```python filename="src/routes/api/items.py"
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"created": True}, status_code=201)
```

## Ошибки

Вызовите FastAPI исключений для клиентов. Клиент, который отправляет `Accept: application/json` получает `{"detail": "..."}` с поднятым вами статусом; браузер получает страницу с ошибкой. `notfound.nexy` отображает `404` и `errors.nexy` отображает `500`, каждый из которых ограничен своим каталогом. См. [Проверка и ошибки](validation-and-errors.md) и [Страницы ошибок](../errors/README.md).

## OpenAPI

Каждый маршрут API отображается в сгенерированной схеме, поскольку маршруты являются простыми FastAPI маршрутами. Схема обслуживается по адресу `/openapi.json` и отображается Scalar по адресу `/docs`. Отключите оба с помощью `useDocs = False` в `nexyconfig.py`.

## Следующие шаги

- [Зависимости](../dependencies/README.md): общая аутентификация и настройка для каждого обработчика или для каждого каталога.
- [Проверка и ошибки](validation-and-errors.md): `422`, `404` и ошибки JSON
- [Маршрутизация](../../README.md): путь к URL-адресу файла
- [Действия](../../../guides/actions.md): конечные точки с сгенерированными путями
- [Конфигурация](../../../reference/config.md): промежуточное программное обеспечение, CORS, сеансы
