# Проверка и ошибки

Как обработчик API сообщает о некорректном запросе.

## Валидация

Параметры обработчика проверяются FastAPI на соответствие их аннотациям.

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| Проблема | Статус | Тело |
|---|---|---|
| отсутствует или недействителен запрос, заголовок, файл cookie или поле тела | `422` | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| неверный сегмент **путь** (`/api/users/abc` для `id: int`) | `404` | не найденная страница или JSON для `Accept: application/json` |

Сегмент пути, который невозможно преобразовать, - это `404`, а не `422`: динамический маршрут захватывает любой URL-адрес, а URL-адрес, который невозможно преобразовать, не существует.

Тело `422` имеет стандартную форму FastAPI, поэтому существующие клиенты и созданные SDK продолжают работать.

## Вызов ошибок

```python filename="src/маршруты/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    item = find(id)
    if item is None:
        raise HTTPException(status_code=404, detail="No such item")
    return item
```

| Клиент отправляет | Ответ |
|---|---|
| `Accept: application/json` | `{"detail": "No such item"}` со статусом `404` |
| `Accept: text/html` | [страница с ошибкой](../errors/README.md) |
| `Accept: */*` | страница с ошибкой |

Установите `Accept: application/json` в клиентах API. Браузеры продолжают получать страницы.

## Необработанные исключения

Исключением является то, что ваш обработчик не перехватывает ответы `500` с тем же выбором HTML или JSON.

## Пользовательские ответы

Возвращайте объект ответа, когда вы управляете телом:

```python
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"error": "conflict"}, status_code=409)
```

## Следующие шаги

- [Маршруты API](README.md)
- [Страницы ошибок](../errors/README.md)
- [Тестирование](../../../guides/testing.md)
