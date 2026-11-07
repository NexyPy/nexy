# De Flask a Nexy

En Nexy, una vista Flask se convierte en un archivo en `src/routes/`: un archivo `.py` para JSON, un archivo `.nexy` para HTML, con Jinja2 conservado y los decoradores, planos y `request` globales desaparecidos.

Cada sección a continuación muestra un hábito Flask, luego lo mismo en Nexy.

## una ruta

```python filename="aplicación.py"
from flask import Flask

app = Flask(__name__)


@app.get("/api/hello")
def hello():
    return {"message": "Hello"}
```

La ruta del archivo es la URL y el nombre de la función es el método:

```python filename="src/rutas/api/hola.py"
async def GET():
    return {"message": "Hello"}
```

## variables de URL

```python filename="aplicación.py"
@app.get("/api/users/<int:id>")
def get_user(id):
    return {"id": id}
```

El convertidor se convierte en una anotación de tipo y la variable en un segmento `[id]`:

```python filename="src/rutas/api/usuarios/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` es un segmento general, `[...rest].py`.

## cadenas de consulta

```python filename="aplicación.py"
from flask import request


@app.get("/api/search")
def search():
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    return {"q": q, "page": page}
```

No existe `request` global: un parámetro de consulta es un parámetro de función, convertido y validado:

```python filename="src/rutas/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Un cuerpo JSON

```python filename="aplicación.py"
@app.post("/api/items")
def create_item():
    data = request.get_json()
    if "name" not in data:
        return {"error": "name is required"}, 400
    return {"created": data["name"]}, 201
```

Un modelo Pydantic valida el cuerpo y uno malo responde `422` por sí solo:

```python filename="src/rutas/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## Varios métodos en una URL

```python filename="aplicación.py"
@app.route("/api/notes/<int:id>", methods=["GET", "DELETE"])
def note(id):
    if request.method == "DELETE":
        return {"deleted": id}
    return {"id": id}
```

Una función por método, en el mismo archivo:

```python filename="src/rutas/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Plantillas

```python filename="aplicación.py"
from flask import render_template


@app.get("/users")
def users():
    return render_template("users.html", users=[{"name": "Ada"}, {"name": "Alan"}])
```

La vista y su plantilla son un archivo `.nexy`: Python encima de la línea `---`, el mismo Jinja2 debajo:

```nexy filename="src/rutas/usuarios.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Una plantilla base

```html filename="plantillas/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

Un `layout.nexy` envuelve cada página de su carpeta y debajo; las páginas no `{% extends %}` lo:

```nexy filename="src/rutas/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Macros e incluye

```html filename="plantillas/macros.html"
{% macro card(title) %}
<article><h2>{{ title }}</h2>{{ caller() }}</article>
{% endmacro %}
```

Un componente es un archivo `.nexy` con accesorios, importado en el frontmatter:

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
---
<article>
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/rutas/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>Everything published this week.</p>
</Card>
```

`@` es `src/`: `nx new` escribe `useAliases = {"@": "src"}` en `nexyconfig.py`.

## Planos

```python filename="administrador.py"
from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.get("/stats")
def stats():
    return {"users": 3}


app.register_blueprint(admin)
```

Una carpeta es el prefijo y no queda nada registrado:

```python filename="src/rutas/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `before_request`

```python filename="administrador.py"
from flask import abort


@admin.before_request
def require_admin():
    if request.headers.get("X-Role") != "admin":
        abort(403)
```

Un `dependencies.py` se ejecuta antes de cada ruta de su carpeta y debajo:

```python filename="src/rutas/admin/dependencias.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `after_request`

```python filename="aplicación.py"
@app.after_request
def add_header(response):
    response.headers["X-App"] = "demo"
    return response
```

Un `middleware.py` ve la solicitud antes de la ruta y la respuesta después de ella:

```python filename="src/rutas/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Formularios y redirecciones

```python filename="aplicación.py"
from flask import redirect, url_for


@app.post("/notes")
def add_note():
    NOTES.append(request.form["title"])
    return redirect(url_for("notes"))
```

Una acción es una Python función en la que se publica el formulario. Nexy le proporciona una ruta, lee los campos del formulario como parámetros y envía al visitante de regreso a la página con un `303`:

```python filename="src/acciones/notas.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/rutas/notas.nexy"
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

## Sesiones

```python filename="aplicación.py"
from flask import session

app.secret_key = "change-me"


@app.post("/api/login")
def login():
    session["user"] = request.json["name"]
    return {"user": session["user"]}
```

El secreto se mueve a `nexyconfig.py` y la sesión cuelga de la solicitud:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

```python filename="src/rutas/api/login.py"
from pydantic import BaseModel

from nexy.http import Request


class Login(BaseModel):
    name: str


async def POST(request: Request, body: Login):
    request.session["user"] = body.name
    return {"user": body.name}
```

Una página lo lee con `useSession()`:

```nexy filename="src/rutas/cuenta.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Hello {{ user }}</h1>
```

## `abort(404)` y controladores de errores

```python filename="aplicación.py"
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.get("/posts/<slug>")
def post(slug):
    if slug not in POSTS:
        abort(404)
    return render_template("post.html", post=POSTS[slug])
```

`notFound()` detiene la página y `notfound.nexy` extrae la respuesta:

```nexy filename="src/rutas/publicaciones/[slug].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="src/rutas/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## Archivos estáticos

```text
static/logo.png        Flask:  /static/logo.png
public/logo.png        Nexy:   /logo.png
```

## Matraz-CORS

```python filename="aplicación.py"
from flask_cors import CORS

CORS(app, origins=["https://example.com"])
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## Pruebas

```python filename="pruebas/test_app.py"
from app import app


def test_hello():
    assert app.test_client().get("/api/hello").json == {"message": "Hello"}
```

```python filename="pruebas/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## corriendo

| Flask | nexy |
|---|---|
| `flask run --debug` | `nx dev` |
| `gunicorn app:app` | `nx build`, luego `nx start` |
| `flask db migrate` (Flask-Migrate) | `nx migrate -m "message"` |
| sin documentos API | `/docs`, enumerando cada `.py` ruta |

## Próximos pasos

- [De FastAPI a Nexy](fastapi.md): Los controladores Nexy son controladores FastAPI
- [Acciones](../guides/actions.md)
- [Archivos .nexy](../views/nexy/README.md)
- [Recetas](../guides/recipes.md): inicio de sesión, CRUD y cargas
