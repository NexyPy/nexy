# De Flask à Nexy

Dans Nexy, une vue Flask devient un fichier sous `src/routes/` : un fichier `.py` pour JSON, un fichier `.nexy` pour HTML, avec Jinja2 conservé et les décorateurs, les plans et `request` globaux disparus.

Chaque section ci-dessous montre une habitude Flask, puis la même chose dans Nexy.

## Un itinéraire

```python filename="app.py"
from flask import Flask

app = Flask(__name__)


@app.get("/api/hello")
def hello():
    return {"message": "Hello"}
```

Le chemin du fichier est l'URL et le nom de la fonction est la méthode :

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Variables d'URL

```python filename="app.py"
@app.get("/api/users/<int:id>")
def get_user(id):
    return {"id": id}
```

Le convertisseur devient une annotation de type, et la variable un segment `[id]` :

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` est un segment fourre-tout, `[...rest].py`.

## Chaînes de requête

```python filename="app.py"
from flask import request


@app.get("/api/search")
def search():
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    return {"q": q, "page": page}
```

Il n'y a pas de `request` global : un paramètre de requête est un paramètre de fonction, converti et validé :

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Un corps JSON

```python filename="app.py"
@app.post("/api/items")
def create_item():
    data = request.get_json()
    if "name" not in data:
        return {"error": "name is required"}, 400
    return {"created": data["name"]}, 201
```

Un modèle Pydantic valide le corps, et un mauvais modèle répond `422` tout seul :

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## Plusieurs méthodes sur une seule URL

```python filename="app.py"
@app.route("/api/notes/<int:id>", methods=["GET", "DELETE"])
def note(id):
    if request.method == "DELETE":
        return {"deleted": id}
    return {"id": id}
```

Une fonction par méthode, dans le même fichier :

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Modèles

```python filename="app.py"
from flask import render_template


@app.get("/users")
def users():
    return render_template("users.html", users=[{"name": "Ada"}, {"name": "Alan"}])
```

La vue et son modèle sont un seul fichier `.nexy` : Python au-dessus de la ligne `---`, le même Jinja2 en dessous :

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

## Un modèle de base

```html filename="modèles/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

Un `layout.nexy` enveloppe chaque page de son dossier et en dessous ; les pages ne le font pas `{% extends %}` il :

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Macros et inclusions

```html filename="modèles/macros.html"
{% macro card(title) %}
<article><h2>{{ title }}</h2>{{ caller() }}</article>
{% endmacro %}
```

Un composant est un fichier `.nexy` avec des accessoires, importé dans le frontmatter :

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

`@` est `src/` : `nx new` écrit `useAliases = {"@": "src"}` dans `nexyconfig.py`.

## Plans

```python filename="admin.py"
from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.get("/stats")
def stats():
    return {"users": 3}


app.register_blueprint(admin)
```

Un dossier est le préfixe, et rien n'est enregistré :

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

Un `dependencies.py` s'exécute avant chaque route de son dossier et ci-dessous :

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

Un `middleware.py` voit la requête avant la route et la réponse après :

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Formulaires et redirections

```python filename="app.py"
from flask import redirect, url_for


@app.post("/notes")
def add_note():
    NOTES.append(request.form["title"])
    return redirect(url_for("notes"))
```

Une action est une fonction Python dans laquelle le formulaire est publié. Nexy lui donne un chemin, lit les champs du formulaire comme paramètres et renvoie le visiteur vers la page avec un `303` :

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

## Séances

```python filename="app.py"
from flask import session

app.secret_key = "change-me"


@app.post("/api/login")
def login():
    session["user"] = request.json["name"]
    return {"user": session["user"]}
```

Le secret est déplacé vers `nexyconfig.py` et la session suspend la requête :

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

Une page le lit avec `useSession()` :

```nexy filename="src/routes/compte.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Hello {{ user }}</h1>
```

## `abort(404)` et gestionnaires d'erreurs

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

`notFound()` arrête la page, et `notfound.nexy` dessine la réponse :

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

## Fichiers statiques

```text
static/logo.png        Flask:  /static/logo.png
public/logo.png        Nexy:   /logo.png
```

## Flacon-CORS

```python filename="app.py"
from flask_cors import CORS

CORS(app, origins=["https://example.com"])
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## Essais

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

## Courir

| Flask | Nexy |
|---|---|
| `flask run --debug` | `nx dev` |
| `gunicorn app:app` | `nx build`, puis `nx start` |
| `flask db migrate` (Flask-Migrer) | `nx migrate -m "message"` |
| pas de documentation API | `/docs`, répertoriant chaque `.py` itinéraire |

## Prochaines étapes

- [De FastAPI à Nexy](fastapi.md) : les gestionnaires Nexy sont des gestionnaires FastAPI
- [Actions](../guides/actions.md)
- [Fichiers .nexy](../views/nexy/README.md)
- [Recettes](../guides/recipes.md) : connexion, CRUD et téléchargements
