# От FastAPI до Некси

Nexy - это FastAPI с маршрутом, записанным в виде файла: функция, которая отвечает на `@app.get("/x")`, отвечает на `src/routes/x.py` как `GET`, а остальная часть вашего кода остается прежней.

## Что остается, что меняется

Nexy обслуживает ваши обработчики с помощью FastAPI, поэтому все внутри обработчика работает без изменений:

| Остается прежним | Изменения |
|---|---|
| Pydantic модели, тела запросов и ответы | `@app.get("/x")` становится `src/routes/x.py` с `async def GET()` |
| `Depends`, `Query`, `Header`, `Cookie`, `Form`, `File` | `{id}` в пути становится файлом `[id].py` или папкой `[id]/` |
| `HTTPException`, `status`, `JSONResponse`, `RedirectResponse` | `APIRouter(prefix="/users")` становится папкой `users/` |
| `Request`, `BackgroundTasks`, `UploadFile`, веб-сокеты | `dependencies=[...]` на маршрутизаторе становится файлом `dependencies.py` |
| Классы промежуточного программного обеспечения, `/docs`, `TestClient` | `app.add_middleware(...)` становится полем `nexyconfig.py`: `useCORS`, `useGZip`, `useMiddlewares` |

Импортируйте их из `fastapi`, как раньше, или из `nexy.http`, который реэкспортирует те же объекты.

В каждом разделе ниже показана привычка FastAPI, затем то же самое в Nexy.

## Конечная точка

FastAPI регистрирует функцию в приложении с помощью декоратора:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/hello")
async def hello():
    return {"message": "Hello"}
```

Nexy считывает URL-адрес из пути к файлу и метод из имени функции:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Путь и параметры запроса

```python filename="main.py"
@app.get("/api/users/{id}")
async def get_user(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

Параметр пути становится сегментом `[id]` имени файла. Параметр запроса не перемещается:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` отвечает на `404`, потому что `abc` не является `int`.

## Тело запроса

```python filename="main.py"
from pydantic import BaseModel


class NewItem(BaseModel):
    name: str
    price: float


@app.post("/api/items", status_code=201)
async def create_item(item: NewItem):
    return item
```

Модель Pydantic такая же. Код состояния перемещается в ответ:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

Тело, не соответствующее модели, отвечает `422`, как и в FastAPI.

## Несколько методов на одном URL

```python filename="main.py"
@app.get("/api/notes/{id}")
async def read_note(id: int): ...


@app.delete("/api/notes/{id}")
async def delete_note(id: int): ...
```

Один файл содержит каждый метод URL:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Маршрутизаторы и префиксы

```python filename="main.py"
from fastapi import APIRouter

admin = APIRouter(prefix="/admin")


@admin.get("/stats")
async def stats():
    return {"users": 3}


app.include_router(admin)
```

Папка является префиксом, и включать в нее нечего:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Зависимости от группы маршрутов

```python filename="main.py"
from fastapi import Depends, Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
```

`dependencies.py` в папке запускается перед каждым маршрутом ниже нее:

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

Зависимость для одного обработчика по-прежнему имеет вид `Depends` в сигнатуре:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header


def current_user(authorization: str = Header(...)) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## Промежуточное ПО

```python filename="main.py"
from fastapi import Request


@app.middleware("http")
async def add_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

`middleware.py` оборачивает маршруты своей папки, корневая оборачивает их все:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## CORS, GZip и другое промежуточное ПО для всего приложения.

```python filename="main.py"
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["https://example.com"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

Каждое из них представляет собой поле `nexyconfig.py` с одинаковыми аргументами:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## HTML-страницы

```python filename="main.py"
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


@app.get("/users")
async def users_page(request: Request):
    users = [{"name": "Ada"}, {"name": "Alan"}]
    return templates.TemplateResponse(request, "users.html", {"users": users})
```

Страница `.nexy` содержит Python над строкой `---` и Jinja2 под ней в одном файле:

```nexy filename="src/маршруты/users.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Наследование шаблонов

```html filename="шаблоны/base.html"
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

`layout.nexy` оборачивает каждую страницу своей папки, без `{% extends %}` на страницах:

```nexy filename="src/маршруты/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Статические файлы

```python filename="main.py"
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

Файлы в `public/` обслуживаются из корня: `public/robots.txt` - это `/robots.txt`.

```text
public/
├─ robots.txt     /robots.txt
└─ logo.png       /logo.png
```

## Не найденные страницы

```python filename="main.py"
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def not_found(request: Request, exc: StarletteHTTPException):
    return HTMLResponse("<h1>Not found</h1>", status_code=exc.status_code)
```

`notfound.nexy` отвечает браузерам, а клиенты API по-прежнему получают `{"detail": ...}`:

```nexy filename="источник/маршруты/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## Вебсокеты

```python filename="main.py"
from fastapi import WebSocket


@app.websocket("/ws/echo")
async def echo(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

```python filename="src/routes/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## Тесты

```python filename="тесты/test_main.py"
from fastapi.testclient import TestClient

from main import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

Клиент тот же; приложение от Nexy:

```python filename="тесты/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Бег

| FastAPI | Некси |
|---|---|
| `uvicorn main:app --reload` | `nx dev` |
| `uvicorn main:app --workers 4` | `nx build`, затем `nx start` |
| `/docs` из `FastAPI()` | `/docs`, список всех `.py` маршрутов |

## Сохранение существующего приложения

Вам не обязательно перемещаться по всем маршрутам одновременно. `APIRouter` у вас уже есть крепления как есть:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Ваши старые маршруты и файлы `src/routes/` затем ответят бок о бок. Пока установлено `useRouter`, страницы `.nexy` не переносятся в `layout.nexy`: сначала переместите API, затем страницы, затем удалите поле. См. [Интеграция пользовательского маршрутизатора](../routing/custom/README.md).

## Следующие шаги

- [Обработчики маршрутов](../routing/fbr/handlers/README.md)
- [Зависимости и меры защиты](../routing/fbr/dependencies/README.md)
- [файлы .nexy](../views/nexy/README.md)
- [Исходя из другого фреймворка](../getting-started/coming-from-other-frameworks.md)
