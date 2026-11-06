# Flask سے Nexy تک

Nexy میں ایک Flask منظر `src/routes/` کے تحت فائل بن جاتا ہے: JSON کے لیے ایک `.py` فائل، HTML کے لیے ایک `.nexy` فائل، جس میں Jinja2 رکھا گیا اور ڈیکوریٹر، بلیو پرنٹس اور `request` عالمی طور پر ختم ہو گئے۔

ذیل میں ہر سیکشن ایک Flask عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔

## ایک راستہ

```python filename="app.py"
from flask import Flask

app = Flask(__name__)


@app.get("/api/hello")
def hello():
    return {"message": "Hello"}
```

فائل کا راستہ URL ہے اور فنکشن کا نام طریقہ ہے:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## URL متغیرات

```python filename="app.py"
@app.get("/api/users/<int:id>")
def get_user(id):
    return {"id": id}
```

کنورٹر ایک قسم کی تشریح بن جاتا ہے، اور متغیر ایک `[id]` سیگمنٹ:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` ایک کیچ آل سیگمنٹ ہے، `[...rest].py`۔

## استفسار کے تار

```python filename="app.py"
from flask import request


@app.get("/api/search")
def search():
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    return {"q": q, "page": page}
```

کوئی `request` عالمی نہیں ہے: ایک سوال پیرامیٹر ایک فنکشن پیرامیٹر ہے، تبدیل شدہ اور تصدیق شدہ:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## ایک JSON باڈی

```python filename="app.py"
@app.post("/api/items")
def create_item():
    data = request.get_json()
    if "name" not in data:
        return {"error": "name is required"}, 400
    return {"created": data["name"]}, 201
```

ایک Pydantic ماڈل جسم کی توثیق کرتا ہے، اور ایک برا اپنے طور پر `422` جواب دیتا ہے:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## ایک URL پر کئی طریقے

```python filename="app.py"
@app.route("/api/notes/<int:id>", methods=["GET", "DELETE"])
def note(id):
    if request.method == "DELETE":
        return {"deleted": id}
    return {"id": id}
```

فی طریقہ ایک فنکشن، اسی فائل میں:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## ٹیمپلیٹس

```python filename="app.py"
from flask import render_template


@app.get("/users")
def users():
    return render_template("users.html", users=[{"name": "Ada"}, {"name": "Alan"}])
```

منظر اور اس کا سانچہ ایک `.nexy` فائل ہے: Python `---` لائن کے اوپر، وہی Jinja2 نیچے:

```nexy filename="src/routes/users.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## ایک بنیادی ٹیمپلیٹ

```html filename="templates/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

ایک `layout.nexy` اپنے فولڈر کے ہر صفحے کو اور نیچے سمیٹتا ہے۔ صفحات یہ `{% extends %}` نہیں کرتے:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## میکرو اور شامل ہیں۔

```html filename="templates/macros.html"
{% macro card(title) %}
<article><h2>{{ title }}</h2>{{ caller() }}</article>
{% endmacro %}
```

ایک جزو ایک `.nexy` فائل ہے جس میں پروپس ہے، جو فرنٹ میٹر میں درآمد کی جاتی ہے:

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
---
<article>
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>Everything published this week.</p>
</Card>
```

`@` ہے `src/`: `nx new` `nexyconfig.py` میں `useAliases = {"@": "src"}` لکھتے ہیں۔

## بلیو پرنٹس

```python filename="admin.py"
from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.get("/stats")
def stats():
    return {"users": 3}


app.register_blueprint(admin)
```

ایک فولڈر سابقہ ہے، اور کچھ بھی رجسٹرڈ نہیں ہے:

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

ایک `dependencies.py` اپنے فولڈر کے ہر روٹ سے پہلے اور نیچے چلتا ہے:

```python filename="src/routes/admin/dependencies.py"
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

A `middleware.py` راستے سے پہلے کی درخواست اور اس کے بعد جواب دیکھتا ہے:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## فارم اور ری ڈائریکٹ

```python filename="app.py"
from flask import redirect, url_for


@app.post("/notes")
def add_note():
    NOTES.append(request.form["title"])
    return redirect(url_for("notes"))
```

ایک ایکشن ایک Python فنکشن ہے جو فارم پوسٹ کرتا ہے۔ Nexy اسے ایک راستہ دیتا ہے، فارم کی فیلڈز کو اس کے پیرامیٹرز کے طور پر پڑھتا ہے، اور وزیٹر کو صفحہ پر واپس بھیجتا ہے `303`:

```python filename="src/actions/notes.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/routes/notes.nexy"
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

## سیشنز

```python filename="app.py"
from flask import session

app.secret_key = "change-me"


@app.post("/api/login")
def login():
    session["user"] = request.json["name"]
    return {"user": session["user"]}
```

راز `nexyconfig.py` میں منتقل ہوتا ہے، اور سیشن درخواست کو روک دیتا ہے:

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

ایک صفحہ اسے `useSession()` کے ساتھ پڑھتا ہے:

```nexy filename="src/routes/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Hello {{ user }}</h1>
```

## `abort(404)` اور ایرر ہینڈلرز

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

`notFound()` صفحہ روکتا ہے، اور `notfound.nexy` جواب کھینچتا ہے:

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## جامد فائلیں۔

```text
static/logo.png        Flask:  /static/logo.png
public/logo.png        Nexy:   /logo.png
```

## فلاسک-CORS

```python filename="app.py"
from flask_cors import CORS

CORS(app, origins=["https://example.com"])
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## ٹیسٹ

```python filename="tests/test_app.py"
from app import app


def test_hello():
    assert app.test_client().get("/api/hello").json == {"message": "Hello"}
```

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## چل رہا ہے۔

| Flask | نیکسی |
|---|---|
| `flask run --debug` | `nx dev` |
| `gunicorn app:app` | `nx build`، پھر `nx start` |
| `flask db migrate` (فلاسک-ہجرت) | `nx migrate -m "message"` |
| کوئی API دستاویزات نہیں ہیں۔ | `/docs`، ہر `.py` راستے کی فہرست |

## اگلے اقدامات

- [سے FastAPI سے Nexy](fastapi.md): Nexy ہینڈلرز FastAPI ہینڈلر ہیں
- [اعمال ](../guides/actions.md)
- [.nexy فائلیں](../views/nexy/README.md)
- [ترکیبیں](../guides/recipes.md): سائن ان، CRUD اور اپ لوڈز
