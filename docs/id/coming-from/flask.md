# Dari Flask hingga Nexy

Di Nexy, tampilan Flask menjadi file di bawah `src/routes/`: file `.py` untuk JSON, file `.nexy` untuk HTML, dengan Jinja2 disimpan dan dekorator, cetak biru, dan `request` global hilang.

Setiap bagian di bawah menunjukkan kebiasaan Flask, lalu hal yang sama di Nexy.

## Sebuah rute

```python filename="app.py"
from flask import Flask

app = Flask(__name__)


@app.get("/api/hello")
def hello():
    return {"message": "Hello"}
```

Jalur file adalah URL dan nama fungsinya adalah metodenya:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Variabel URL

```python filename="app.py"
@app.get("/api/users/<int:id>")
def get_user(id):
    return {"id": id}
```

Konverter menjadi anotasi tipe, dan variabel menjadi segmen `[id]`:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` adalah segmen yang mencakup semua, `[...rest].py`.

## String kueri

```python filename="app.py"
from flask import request


@app.get("/api/search")
def search():
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    return {"q": q, "page": page}
```

Tidak ada `request` global: parameter kueri adalah parameter fungsi, dikonversi dan divalidasi:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Badan JSON

```python filename="app.py"
@app.post("/api/items")
def create_item():
    data = request.get_json()
    if "name" not in data:
        return {"error": "name is required"}, 400
    return {"created": data["name"]}, 201
```

Model Pydantic memvalidasi isi, dan model yang buruk menjawab `422` dengan sendirinya:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## Beberapa metode pada satu URL

```python filename="app.py"
@app.route("/api/notes/<int:id>", methods=["GET", "DELETE"])
def note(id):
    if request.method == "DELETE":
        return {"deleted": id}
    return {"id": id}
```

Satu fungsi per metode, dalam file yang sama:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Templat

```python filename="app.py"
from flask import render_template


@app.get("/users")
def users():
    return render_template("users.html", users=[{"name": "Ada"}, {"name": "Alan"}])
```

Tampilan dan templatnya adalah satu file `.nexy`: Python di atas baris `---`, Jinja2 yang sama di bawah:

```nexy filename="src/rute/pengguna.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Templat dasar

```html filename="templat/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

A `layout.nexy` membungkus setiap halaman foldernya dan di bawahnya; halaman tidak `{% extends %}` itu:

```nexy filename="src/route/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Makro dan penyertaannya

```html filename="template/macros.html"
{% macro card(title) %}
<article><h2>{{ title }}</h2>{{ caller() }}</article>
{% endmacro %}
```

Komponen adalah file `.nexy` dengan props, yang diimpor di frontmatter:

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
---
<article>
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/rute/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>Everything published this week.</p>
</Card>
```

`@` adalah `src/`: `nx new` menulis `useAliases = {"@": "src"}` di `nexyconfig.py`.

## cetak biru

```python filename="admin.py"
from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.get("/stats")
def stats():
    return {"users": 3}


app.register_blueprint(admin)
```

Folder adalah awalan, dan tidak ada yang terdaftar:

```python filename="src/route/admin/stats.py"
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

`dependencies.py` berjalan sebelum setiap rute foldernya dan di bawahnya:

```python filename="src/rute/admin/dependensi.py"
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

A `middleware.py` melihat permintaan sebelum rute dan respons setelahnya:

```python filename="src/rute/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Formulir dan pengalihan

```python filename="app.py"
from flask import redirect, url_for


@app.post("/notes")
def add_note():
    NOTES.append(request.form["title"])
    return redirect(url_for("notes"))
```

Suatu tindakan adalah fungsi Python yang diposkan oleh formulir. Nexy memberinya jalur, membaca kolom formulir sebagai parameternya, dan mengirim pengunjung kembali ke halaman dengan `303`:

```python filename="src/aksi/catatan.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/rute/catatan.nexy"
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

## Sesi

```python filename="app.py"
from flask import session

app.secret_key = "change-me"


@app.post("/api/login")
def login():
    session["user"] = request.json["name"]
    return {"user": session["user"]}
```

Rahasia berpindah ke `nexyconfig.py`, dan sesi menghentikan permintaan:

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

Sebuah halaman membacanya dengan `useSession()`:

```nexy filename="src/routes/akun.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Hello {{ user }}</h1>
```

## `abort(404)` dan penangan kesalahan

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

`notFound()` menghentikan halaman, dan `notfound.nexy` menarik jawabannya:

```nexy filename="src/rute/postingan/[siput].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="src/rute/tidak ditemukan.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## File statis

```text
static/logo.png        Flask:  /static/logo.png
public/logo.png        Nexy:   /logo.png
```

## Labu-CORS

```python filename="app.py"
from flask_cors import CORS

CORS(app, origins=["https://example.com"])
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## Tes

```python filename="tes/test_app.py"
from app import app


def test_hello():
    assert app.test_client().get("/api/hello").json == {"message": "Hello"}
```

```python filename="tes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Berlari

| Flask | Nexy |
|---|---|
| `flask run --debug` | `nx dev` |
| `gunicorn app:app` | `nx build`, lalu `nx start` |
| `flask db migrate` (Migrasi Labu) | `nx migrate -m "message"` |
| tidak ada dokumen API | `/docs`, mencantumkan setiap `.py` rute |

## Langkah selanjutnya

- [Dari FastAPI hingga Nexy](fastapi.md): Penangan Nexy adalah penangan FastAPI
- [Tindakan](../guides/actions.md)
- [file .nexy](../views/nexy/README.md)
- [Resep](../guides/recipes.md): masuk, CRUD dan unggah
