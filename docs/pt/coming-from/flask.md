# De Flask para Nexy

No Nexy, uma visualização Flask se torna um arquivo em `src/routes/`: um arquivo `.py` para JSON, um arquivo `.nexy` para HTML, com Jinja2 mantido e os decoradores, blueprints e `request` globais desaparecidos.

Cada seção abaixo mostra um hábito Flask, então a mesma coisa no Nexy.

## Uma rota

```python filename="aplicativo.py"
from flask import Flask

app = Flask(__name__)


@app.get("/api/hello")
def hello():
    return {"message": "Hello"}
```

O caminho do arquivo é a URL e o nome da função é o método:

```python filename="src/rotas/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Variáveis de URL

```python filename="aplicativo.py"
@app.get("/api/users/<int:id>")
def get_user(id):
    return {"id": id}
```

O conversor se torna uma anotação de tipo e a variável um segmento `[id]`:

```python filename="src/rotas/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` é um segmento abrangente, `[...rest].py`.

## Cadeias de caracteres de consulta

```python filename="aplicativo.py"
from flask import request


@app.get("/api/search")
def search():
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    return {"q": q, "page": page}
```

Não existe `request` global: um parâmetro de consulta é um parâmetro de função, convertido e validado:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Um corpo JSON

```python filename="aplicativo.py"
@app.post("/api/items")
def create_item():
    data = request.get_json()
    if "name" not in data:
        return {"error": "name is required"}, 400
    return {"created": data["name"]}, 201
```

Um modelo Pydantic valida o corpo, e um modelo ruim responde `422` por conta própria:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## Vários métodos em um URL

```python filename="aplicativo.py"
@app.route("/api/notes/<int:id>", methods=["GET", "DELETE"])
def note(id):
    if request.method == "DELETE":
        return {"deleted": id}
    return {"id": id}
```

Uma função por método, no mesmo arquivo:

```python filename="src/rotas/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Modelos

```python filename="aplicativo.py"
from flask import render_template


@app.get("/users")
def users():
    return render_template("users.html", users=[{"name": "Ada"}, {"name": "Alan"}])
```

A visualização e seu modelo são um arquivo `.nexy`: Python acima da linha `---`, o mesmo Jinja2 abaixo:

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

## Um modelo básico

```html filename="modelos/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

Um `layout.nexy` envolve todas as páginas de sua pasta e abaixo; páginas não `{% extends %}` isso:

```nexy filename="src/rotas/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Macros e inclui

```html filename="modelos/macros.html"
{% macro card(title) %}
<article><h2>{{ title }}</h2>{{ caller() }}</article>
{% endmacro %}
```

Um componente é um arquivo `.nexy` com props, importado no frontmatter:

```nexy filename="src/componentes/Card.nexy"
---
title: prop[str]
---
<article>
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/rotas/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>Everything published this week.</p>
</Card>
```

`@` é `src/`: `nx new` escreve `useAliases = {"@": "src"}` em `nexyconfig.py`.

## Plantas

```python filename="admin.py"
from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.get("/stats")
def stats():
    return {"users": 3}


app.register_blueprint(admin)
```

Uma pasta é o prefixo e nada é registrado:

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

Um `dependencies.py` é executado antes de cada rota de sua pasta e abaixo:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `after_request`

```python filename="aplicativo.py"
@app.after_request
def add_header(response):
    response.headers["X-App"] = "demo"
    return response
```

Um `middleware.py` vê a solicitação antes da rota e a resposta depois dela:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Formulários e redirecionamentos

```python filename="aplicativo.py"
from flask import redirect, url_for


@app.post("/notes")
def add_note():
    NOTES.append(request.form["title"])
    return redirect(url_for("notes"))
```

Uma ação é uma função Python para a qual o formulário é postado. Nexy fornece um caminho, lê os campos do formulário como seus parâmetros e envia o visitante de volta à página com um `303`:

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

## Sessões

```python filename="aplicativo.py"
from flask import session

app.secret_key = "change-me"


@app.post("/api/login")
def login():
    session["user"] = request.json["name"]
    return {"user": session["user"]}
```

O segredo passa para `nexyconfig.py` e a sessão interrompe a solicitação:

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

Uma página lê com `useSession()`:

```nexy filename="src/rotas/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Hello {{ user }}</h1>
```

## `abort(404)` e manipuladores de erros

```python filename="aplicativo.py"
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.get("/posts/<slug>")
def post(slug):
    if slug not in POSTS:
        abort(404)
    return render_template("post.html", post=POSTS[slug])
```

`notFound()` interrompe a página e `notfound.nexy` desenha a resposta:

```nexy filename="src/rotas/posts/[slug].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="src/rotas/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## Arquivos estáticos

```text
static/logo.png        Flask:  /static/logo.png
public/logo.png        Nexy:   /logo.png
```

## Frasco-CORS

```python filename="aplicativo.py"
from flask_cors import CORS

CORS(app, origins=["https://example.com"])
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## Testes

```python filename="testes/test_app.py"
from app import app


def test_hello():
    assert app.test_client().get("/api/hello").json == {"message": "Hello"}
```

```python filename="testes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Correndo

| Flask | Nexy |
|---|---|
| `flask run --debug` | `nx dev` |
| `gunicorn app:app` | `nx build`, então `nx start` |
| `flask db migrate` (Flask-Migrate) | `nx migrate -m "message"` |
| sem documentos de API | `/docs`, listando todas as `.py` rotas |

## Próximas etapas

- [De FastAPI a Nexy](fastapi.md): manipuladores Nexy são manipuladores FastAPI
- [Ações](../guides/actions.md)
- [Arquivos .nexy](../views/nexy/README.md)
- [Receitas](../guides/recipes.md): login, CRUD e uploads
