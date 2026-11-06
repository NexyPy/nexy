# من Flask إلى النكسي

في Nexy، يصبح العرض Flask ملفًا ضمن `src/routes/`: ملف `.py` لـ JSON، وملف `.nexy` لـ HTML، مع الاحتفاظ بـ Jinja2 واختفاء الديكورات والمخططات و `request` العامة.

كل قسم أدناه يوضح عادة Flask، ثم نفس الشيء في Nexy.

## طريق

```python filename="app.py"
from flask import Flask

app = Flask(__name__)


@app.get("/api/hello")
def hello():
    return {"message": "Hello"}
```

مسار الملف هو عنوان URL واسم الوظيفة هو الطريقة:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## متغيرات URL

```python filename="app.py"
@app.get("/api/users/<int:id>")
def get_user(id):
    return {"id": id}
```

يصبح المحول تعليقًا توضيحيًا للنوع، والمتغير مقطعًا `[id]`:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` هو مقطع جامع، `[...rest].py`.

## سلاسل الاستعلام

```python filename="app.py"
from flask import request


@app.get("/api/search")
def search():
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    return {"q": q, "page": page}
```

لا يوجد `request` عالمي: معلمة الاستعلام هي معلمة دالة، تم تحويلها والتحقق من صحتها:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## هيئة JSON

```python filename="app.py"
@app.post("/api/items")
def create_item():
    data = request.get_json()
    if "name" not in data:
        return {"error": "name is required"}, 400
    return {"created": data["name"]}, 201
```

نموذج Pydantic يثبت صحة الجسد، والنموذج السيئ يجيب `422` من تلقاء نفسه:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## عدة طرق على عنوان URL واحد

```python filename="app.py"
@app.route("/api/notes/<int:id>", methods=["GET", "DELETE"])
def note(id):
    if request.method == "DELETE":
        return {"deleted": id}
    return {"id": id}
```

دالة واحدة لكل طريقة، في نفس الملف:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## قوالب

```python filename="app.py"
from flask import render_template


@app.get("/users")
def users():
    return render_template("users.html", users=[{"name": "Ada"}, {"name": "Alan"}])
```

العرض والقالب الخاص به هما ملف `.nexy` واحد: Python أعلى السطر `---`، نفس Jinja2 أدناه:

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

## قالب أساسي

```html filename="قوالب/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

A `layout.nexy` يغلف كل صفحة من المجلد الخاص به وأدناه؛ صفحات لا `{% extends %}` ذلك:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## وحدات الماكرو وتتضمن

```html filename="قوالب/macros.html"
{% macro card(title) %}
<article><h2>{{ title }}</h2>{{ caller() }}</article>
{% endmacro %}
```

المكون هو ملف `.nexy` مع الدعائم، المستوردة في المادة الأمامية:

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

`@` هو `src/`: `nx new` يكتب `useAliases = {"@": "src"}` في `nexyconfig.py`.

## المخططات

```python filename="admin.py"
from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.get("/stats")
def stats():
    return {"users": 3}


app.register_blueprint(admin)
```

المجلد هو البادئة، ولا يتم تسجيل أي شيء:

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

يتم تشغيل `dependencies.py` قبل كل مسار لمجلده وأدناه:

```python filename="src/routes/admin/dependeency.py"
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

أ `middleware.py` يرى الطلب قبل المسار والاستجابة بعده:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## النماذج وعمليات إعادة التوجيه

```python filename="app.py"
from flask import redirect, url_for


@app.post("/notes")
def add_note():
    NOTES.append(request.form["title"])
    return redirect(url_for("notes"))
```

الإجراء هو وظيفة Python يتم إرسال النموذج إليها. يمنحها Nexy مسارًا، ويقرأ حقول النموذج كمعلمات لها، ويرسل الزائر مرة أخرى إلى الصفحة مع `303`:

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

## الجلسات

```python filename="app.py"
from flask import session

app.secret_key = "change-me"


@app.post("/api/login")
def login():
    session["user"] = request.json["name"]
    return {"user": session["user"]}
```

ينتقل السر إلى `nexyconfig.py`، وتتوقف الجلسة عن الطلب:

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

صفحة تقرأها بـ `useSession()`:

```nexy filename="src/routes/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Hello {{ user }}</h1>
```

## `abort(404)` ومعالجات الأخطاء

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

`notFound()` يوقف الصفحة، ويرسم `notfound.nexy` الجواب:

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

## الملفات الثابتة

```text
static/logo.png        Flask:  /static/logo.png
public/logo.png        Nexy:   /logo.png
```

## قارورة CORS

```python filename="app.py"
from flask_cors import CORS

CORS(app, origins=["https://example.com"])
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## الاختبارات

```python filename="الاختبارات/test_app.py"
from app import app


def test_hello():
    assert app.test_client().get("/api/hello").json == {"message": "Hello"}
```

```python filename="الاختبارات/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## الجري

| Flask | نكسي |
|---|---|
| `flask run --debug` | `nx dev` |
| `gunicorn app:app` | `nx build`، ثم `nx start` |
| `flask db migrate` (القارورة تهاجر) | `nx migrate -m "message"` |
| لا توجد مستندات API | `/docs`، سرد كل `.py` الطريق |

## الخطوات التالية

- [من FastAPI إلى Nexy](fastapi.md): معالجات Nexy هي معالجات FastAPI
- [الإجراءات](../guides/actions.md)
- [ملفات .nexy](../views/nexy/README.md)
- [الوصفات](../guides/recipes.md): تسجيل الدخول، CRUD والتحميلات
