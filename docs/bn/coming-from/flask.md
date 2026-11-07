# Flask থেকে নেক্সি পর্যন্ত

নেক্সিতে একটি Flask ভিউ `src/routes/` এর অধীনে একটি ফাইল হয়ে যায়: JSON-এর জন্য একটি `.py` ফাইল, HTML-এর জন্য একটি `.nexy` ফাইল, Jinja2 রাখা এবং ডেকোরেটর, ব্লুপ্রিন্ট এবং `request` গ্লোবাল চলে গেছে।

নীচের প্রতিটি বিভাগ একটি Flask অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস।

## একটি রুট

```python filename="app.py"
from flask import Flask

app = Flask(__name__)


@app.get("/api/hello")
def hello():
    return {"message": "Hello"}
```

ফাইল পাথ হল URL এবং ফাংশনের নাম হল পদ্ধতি:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## URL ভেরিয়েবল

```python filename="app.py"
@app.get("/api/users/<int:id>")
def get_user(id):
    return {"id": id}
```

রূপান্তরকারী একটি টাইপ টীকা হয়, এবং পরিবর্তনশীল একটি `[id]` সেগমেন্ট:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` একটি ক্যাচ-অল সেগমেন্ট, `[...rest].py`।

## প্রশ্ন স্ট্রিং

```python filename="app.py"
from flask import request


@app.get("/api/search")
def search():
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    return {"q": q, "page": page}
```

কোন `request` বিশ্বব্যাপী নেই: একটি ক্যোয়ারী প্যারামিটার হল একটি ফাংশন প্যারামিটার, রূপান্তরিত এবং বৈধ:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## একটি JSON বডি

```python filename="app.py"
@app.post("/api/items")
def create_item():
    data = request.get_json()
    if "name" not in data:
        return {"error": "name is required"}, 400
    return {"created": data["name"]}, 201
```

একটি Pydantic মডেল শরীরের বৈধতা দেয়, এবং একটি খারাপ একটি নিজেই উত্তর দেয় `422`:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## একটি ইউআরএলে বিভিন্ন পদ্ধতি

```python filename="app.py"
@app.route("/api/notes/<int:id>", methods=["GET", "DELETE"])
def note(id):
    if request.method == "DELETE":
        return {"deleted": id}
    return {"id": id}
```

প্রতি পদ্ধতিতে একটি ফাংশন, একই ফাইলে:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## টেমপ্লেট

```python filename="app.py"
from flask import render_template


@app.get("/users")
def users():
    return render_template("users.html", users=[{"name": "Ada"}, {"name": "Alan"}])
```

ভিউ এবং এর টেমপ্লেটটি একটি `.nexy` ফাইল: `---` লাইনের উপরে Python, নীচে একই Jinja2:

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

## একটি বেস টেমপ্লেট

```html filename="templates/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

একটি `layout.nexy` তার ফোল্ডারের প্রতিটি পৃষ্ঠা এবং নীচে মোড়ানো; পৃষ্ঠাগুলি এটি `{% extends %}` করে না:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## ম্যাক্রো এবং অন্তর্ভুক্ত

```html filename="templates/macros.html"
{% macro card(title) %}
<article><h2>{{ title }}</h2>{{ caller() }}</article>
{% endmacro %}
```

একটি কম্পোনেন্ট হল একটি `.nexy` ফাইল, প্রপস সহ, ফ্রন্টম্যাটারে আমদানি করা হয়:

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

`@` হল `src/`: `nx new` লিখেছেন `useAliases = {"@": "src"}` `nexyconfig.py`।

## ব্লুপ্রিন্ট

```python filename="admin.py"
from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.get("/stats")
def stats():
    return {"users": 3}


app.register_blueprint(admin)
```

একটি ফোল্ডার হল উপসর্গ, এবং কিছুই নিবন্ধিত নেই:

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

একটি `dependencies.py` তার ফোল্ডারের প্রতিটি রুটের আগে এবং নীচে চলে:

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

A `middleware.py` রুটের আগে অনুরোধ এবং এর পরে প্রতিক্রিয়া দেখে:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## ফর্ম এবং পুনঃনির্দেশ

```python filename="app.py"
from flask import redirect, url_for


@app.post("/notes")
def add_note():
    NOTES.append(request.form["title"])
    return redirect(url_for("notes"))
```

একটি কর্ম হল একটি Python ফাংশন যা ফর্ম পোস্ট করে। Nexy এটিকে একটি পথ দেয়, ফর্ম ক্ষেত্রগুলিকে এর প্যারামিটার হিসাবে পড়ে, এবং একটি `303` সহ ভিজিটরকে পৃষ্ঠায় ফেরত পাঠায়:

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

## সেশন

```python filename="app.py"
from flask import session

app.secret_key = "change-me"


@app.post("/api/login")
def login():
    session["user"] = request.json["name"]
    return {"user": session["user"]}
```

গোপনটি `nexyconfig.py` এ চলে যায়, এবং সেশনটি অনুরোধটি বন্ধ করে দেয়:

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

একটি পৃষ্ঠা এটি `useSession()` দিয়ে পড়ে:

```nexy filename="src/routes/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Hello {{ user }}</h1>
```

## `abort(404)` এবং ত্রুটি হ্যান্ডলার

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

`notFound()` পৃষ্ঠা বন্ধ করে, এবং `notfound.nexy` উত্তরটি আঁকে:

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

## স্ট্যাটিক ফাইল

```text
static/logo.png        Flask:  /static/logo.png
public/logo.png        Nexy:   /logo.png
```

## ফ্লাস্ক-CORS

```python filename="app.py"
from flask_cors import CORS

CORS(app, origins=["https://example.com"])
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## টেস্ট

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

## চলছে

| Flask | নেক্সি |
|---|---|
| `flask run --debug` | `nx dev` |
| `gunicorn app:app` | `nx build`, তারপর `nx start` |
| `flask db migrate` (ফ্লাস্ক-মাইগ্রেট) | `nx migrate -m "message"` |
| কোনো API ডক্স নেই | `/docs`, প্রতিটি `.py` রুটের তালিকা করা |

## পরবর্তী পদক্ষেপ

- [থেকে FastAPI থেকে Nexy](fastapi.md): Nexy হ্যান্ডলার হল FastAPI হ্যান্ডলার
- [কর্ম](../guides/actions.md)
- [.nexy ফাইল](../views/nexy/README.md)
- [রেসিপি ](../guides/recipes.md): সাইন-ইন, CRUD এবং আপলোড
