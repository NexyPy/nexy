# От Flask до Некси

В Nexy представление Flask становится файлом в папке `src/routes/`: файлом `.py` для JSON, файлом `.nexy` для HTML, при этом Jinja2 сохраняется, а декораторы, чертежи и `request` глобальные исчезают.

В каждом разделе ниже показана привычка Flask, затем то же самое в Nexy.

## Маршрут

```python filename="app.py"
from flask import Flask

app = Flask(__name__)


@app.get("/api/hello")
def hello():
    return {"message": "Hello"}
```

Путь к файлу — это URL-адрес, а имя функции — это метод:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## URL-переменные

```python filename="app.py"
@app.get("/api/users/<int:id>")
def get_user(id):
    return {"id": id}
```

Конвертер становится аннотацией типа, а переменная — сегментом `[id]`:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` — это универсальный сегмент, `[...rest].py`.

## Строки запроса

```python filename="app.py"
from flask import request


@app.get("/api/search")
def search():
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    return {"q": q, "page": page}
```

Глобального `request` нет: параметр запроса — это параметр функции, преобразованный и проверенный:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Тело JSON

```python filename="app.py"
@app.post("/api/items")
def create_item():
    data = request.get_json()
    if "name" not in data:
        return {"error": "name is required"}, 400
    return {"created": data["name"]}, 201
```

Модель Pydantic проверяет тело, а плохая отвечает на `422` самостоятельно:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## Несколько методов на одном URL

```python filename="app.py"
@app.route("/api/notes/<int:id>", methods=["GET", "DELETE"])
def note(id):
    if request.method == "DELETE":
        return {"deleted": id}
    return {"id": id}
```

Одна функция на метод в одном файле:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Шаблоны

```python filename="app.py"
from flask import render_template


@app.get("/users")
def users():
    return render_template("users.html", users=[{"name": "Ada"}, {"name": "Alan"}])
```

Представление и его шаблон — это один файл `.nexy`: Python над строкой `---`, тот же Jinja2 снизу:

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

## Базовый шаблон

```html filename="шаблоны/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

`layout.nexy` оборачивает каждую страницу своей папки и ниже; страницы не `{% extends %}` это:

```nexy filename="src/маршруты/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Макросы и включает в себя

```html filename="шаблоны/macros.html"
{% macro card(title) %}
<article><h2>{{ title }}</h2>{{ caller() }}</article>
{% endmacro %}
```

Компонент представляет собой файл `.nexy` с реквизитами, импортированный во вступительной части:

```nexy filename="источник/компоненты/Card.nexy"
---
title: prop[str]
---
<article>
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="источник/маршруты/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>Everything published this week.</p>
</Card>
```

`@` — это `src/`: `nx new` записывает `useAliases = {"@": "src"}` в `nexyconfig.py`.

## Чертежи

```python filename="admin.py"
from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.get("/stats")
def stats():
    return {"users": 3}


app.register_blueprint(admin)
```

Папка — это префикс, и ничего не прописано:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `before_request`

```python filename="admin.py"
from flask import abort


@admin.before_request
def require_admin():
    if request.headers.get("X-Role") != "admin":
        abort(403)
```

`dependencies.py` выполняется перед каждым маршрутом в своей папке и ниже:

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `after_request`

```python filename="app.py"
@app.after_request
def add_header(response):
    response.headers["X-App"] = "demo"
    return response
```

`middleware.py` видит запрос перед маршрутом и ответ после него:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Формы и редиректы

```python filename="app.py"
from flask import redirect, url_for


@app.post("/notes")
def add_note():
    NOTES.append(request.form["title"])
    return redirect(url_for("notes"))
```

Действие — это функция Python, в которую отправляется форма. Nexy задает ему путь, считывает поля формы как параметры и отправляет посетителя обратно на страницу с помощью `303`:

```python filename="src/actions/notes.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/маршруты/notes.nexy"
---
from src.actions.notes import NOTES
---
<form method="post" action="{{ __actions_path['add_note'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
<ul>
  {% for note in NOTES %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

## Сессии

```python filename="app.py"
from flask import session

app.secret_key = "change-me"


@app.post("/api/login")
def login():
    session["user"] = request.json["name"]
    return {"user": session["user"]}
```

Секрет перемещается в `nexyconfig.py`, и сеанс зависает на запросе:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

```python filename="src/routes/api/login.py"
from pydantic import BaseModel

from nexy.http import Request


class Login(BaseModel):
    name: str


async def POST(request: Request, body: Login):
    request.session["user"] = body.name
    return {"user": body.name}
```

Страница читает его с помощью `useSession()`:

```nexy filename="src/маршруты/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Hello {{ user }}</h1>
```

## `abort(404)` и обработчики ошибок

```python filename="app.py"
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.get("/posts/<slug>")
def post(slug):
    if slug not in POSTS:
        abort(404)
    return render_template("post.html", post=POSTS[slug])
```

`notFound()` останавливает страницу, а `notfound.nexy` рисует ответ:

```nexy filename="src/маршруты/сообщения/[слизень].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="источник/маршруты/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## Статические файлы

```text
static/logo.png        Flask:  /static/logo.png
public/logo.png        Nexy:   /logo.png
```

## Колба-КОРС

```python filename="app.py"
from flask_cors import CORS

CORS(app, origins=["https://example.com"])
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## Тесты

```python filename="тесты/test_app.py"
from app import app


def test_hello():
    assert app.test_client().get("/api/hello").json == {"message": "Hello"}
```

```python filename="тесты/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Бег

| Flask | Некси |
|---|---|
| `flask run --debug` | `nx dev` |
| `gunicorn app:app` | `nx build`, затем `nx start` |
| `flask db migrate` (Flask-Migrate) | `nx migrate -m "message"` |
| нет документации по API | `/docs`, список всех `.py` маршрутов |

## Следующие шаги

- [От FastAPI до Nexy](fastapi.md): обработчики Nexy — это обработчики FastAPI
- [Действия](../guides/actions.md)
- [файлы .nexy](../views/nexy/README.md)
- [Рецепты](../guides/recipes.md): вход в систему, CRUD и загрузка
