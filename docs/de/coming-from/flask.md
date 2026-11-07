# Von Flask zu Nexy

In Nexy wird eine Flask-Ansicht zu einer Datei unter `src/routes/`: eine `.py`-Datei für JSON, eine `.nexy`-Datei für HTML, wobei Jinja2 beibehalten wird und die Dekoratoren, Blaupausen und `request` global wegfallen.

Jeder Abschnitt unten zeigt eine Flask-Gewohnheit, dann dasselbe in Nexy.

## Eine Route

```python filename="app.py"
from flask import Flask

app = Flask(__name__)


@app.get("/api/hello")
def hello():
    return {"message": "Hello"}
```

Der Dateipfad ist die URL und der Funktionsname ist die Methode:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## URL-Variablen

```python filename="app.py"
@app.get("/api/users/<int:id>")
def get_user(id):
    return {"id": id}
```

Der Konverter wird zu einer Typanmerkung und die Variable zu einem `[id]`-Segment:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` ist ein Sammelsegment, `[...rest].py`.

## Abfragezeichenfolgen

```python filename="app.py"
from flask import request


@app.get("/api/search")
def search():
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    return {"q": q, "page": page}
```

Es gibt kein `request` global: Ein Abfrageparameter ist ein Funktionsparameter, konvertiert und validiert:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Ein JSON-Körper

```python filename="app.py"
@app.post("/api/items")
def create_item():
    data = request.get_json()
    if "name" not in data:
        return {"error": "name is required"}, 400
    return {"created": data["name"]}, 201
```

Ein Pydantic Modell validiert den Körper, und ein schlechtes antwortet `422` von selbst:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## Mehrere Methoden auf einer URL

```python filename="app.py"
@app.route("/api/notes/<int:id>", methods=["GET", "DELETE"])
def note(id):
    if request.method == "DELETE":
        return {"deleted": id}
    return {"id": id}
```

Eine Funktion pro Methode in derselben Datei:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Vorlagen

```python filename="app.py"
from flask import render_template


@app.get("/users")
def users():
    return render_template("users.html", users=[{"name": "Ada"}, {"name": "Alan"}])
```

Die Ansicht und ihre Vorlage befinden sich in einer `.nexy`-Datei: Python über der Zeile `---`, dasselbe Jinja2 darunter:

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

## Eine Basisvorlage

```html filename="templates/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

Ein `layout.nexy` umschließt jede Seite seines Ordners und darunter; Seiten tun es nicht `{% extends %}`:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Makros und Includes

```html filename="templates/macros.html"
{% macro card(title) %}
<article><h2>{{ title }}</h2>{{ caller() }}</article>
{% endmacro %}
```

Eine Komponente ist eine `.nexy`-Datei mit Requisiten, die in die Frontmatter importiert wird:

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

`@` ist `src/`: `nx new` schreibt `useAliases = {"@": "src"}` in `nexyconfig.py`.

## Blaupausen

```python filename="admin.py"
from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.get("/stats")
def stats():
    return {"users": 3}


app.register_blueprint(admin)
```

Ein Ordner ist das Präfix und nichts wird registriert:

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

Ein `dependencies.py` läuft vor jeder Route seines Ordners und darunter:

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

Ein `middleware.py` sieht die Anfrage vor der Route und die Antwort danach:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Formulare und Weiterleitungen

```python filename="app.py"
from flask import redirect, url_for


@app.post("/notes")
def add_note():
    NOTES.append(request.form["title"])
    return redirect(url_for("notes"))
```

Eine Aktion ist eine Python Funktion, an die das Formular sendet. Nexy gibt ihm einen Pfad, liest die Formularfelder als Parameter und sendet den Besucher mit einem `303` zurück zur Seite:

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

## Sitzungen

```python filename="app.py"
from flask import session

app.secret_key = "change-me"


@app.post("/api/login")
def login():
    session["user"] = request.json["name"]
    return {"user": session["user"]}
```

Das Geheimnis wird nach `nexyconfig.py` verschoben und die Sitzung hängt von der Anfrage ab:

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

Eine Seite liest es mit `useSession()`:

```nexy filename="src/routes/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Hello {{ user }}</h1>
```

## `abort(404)` und Fehlerhandler

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

`notFound()` stoppt die Seite und `notfound.nexy` zeichnet die Antwort:

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

## Statische Dateien

```text
static/logo.png        Flask:  /static/logo.png
public/logo.png        Nexy:   /logo.png
```

## Kolben-CORS

```python filename="app.py"
from flask_cors import CORS

CORS(app, origins=["https://example.com"])
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## Tests

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

## Laufen

| Flask | Nexy |
|---|---|
| `flask run --debug` | `nx dev` |
| `gunicorn app:app` | `nx build`, dann `nx start` |
| `flask db migrate` (Flaschenmigration) | `nx migrate -m "message"` |
| Keine API-Dokumente | `/docs`, Auflistung aller `.py` Routen |

## Nächste Schritte

- [Von FastAPI zu Nexy](fastapi.md): Nexy-Handler sind FastAPI-Handler
- [Aktionen](../guides/actions.md)
- [.nexy-Dateien](../views/nexy/README.md)
- [Rezepte](../guides/recipes.md): Anmeldung, CRUD und Uploads
