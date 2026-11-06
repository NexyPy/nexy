# De FastAPI à Nexy

Nexy est FastAPI avec la route écrite sous forme de fichier : une fonction qui répond sous `@app.get("/x")` répond dans `src/routes/x.py` comme `GET`, et le reste de votre code reste le même.

## Ce qui reste, ce qui change

Nexy sert vos gestionnaires avec FastAPI lui-même, donc tout ce qui se trouve à l'intérieur d'un gestionnaire fonctionne inchangé :

| Reste le même | Changements |
|---|---|
| Pydantic modèles, corps de requête et réponses | `@app.get("/x")` devient `src/routes/x.py` avec `async def GET()` |
| `Depends`, `Query`, `Header`, `Cookie`, `Form`, `File` | `{id}` dans le chemin devient un fichier `[id].py` ou un dossier `[id]/` |
| `HTTPException`, `status`, `JSONResponse`, `RedirectResponse` | `APIRouter(prefix="/users")` devient le dossier `users/` |
| `Request`, `BackgroundTasks`, `UploadFile`, WebSockets | `dependencies=[...]` sur un routeur devient un fichier `dependencies.py` |
| Classes de middleware, `/docs`, `TestClient` | `app.add_middleware(...)` devient un champ de `nexyconfig.py` : `useCORS`, `useGZip`, `useMiddlewares` |

Importez-les depuis `fastapi` comme auparavant, ou depuis `nexy.http`, qui réexporte les mêmes objets.

Chaque section ci-dessous montre une habitude FastAPI, puis la même chose dans Nexy.

## Un point final

FastAPI enregistre une fonction sur une application auprès d'un décorateur :

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/hello")
async def hello():
    return {"message": "Hello"}
```

Nexy lit l'URL à partir du chemin du fichier et la méthode à partir du nom de la fonction :

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Paramètres de chemin et de requête

```python filename="main.py"
@app.get("/api/users/{id}")
async def get_user(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

Le paramètre path devient un segment `[id]` du nom de fichier. Le paramètre de requête ne bouge pas :

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` répond à `404`, car `abc` n'est pas un `int`.

## Un corps de requête

```python filename="main.py"
from pydantic import BaseModel


class NewItem(BaseModel):
    name: str
    price: float


@app.post("/api/items", status_code=201)
async def create_item(item: NewItem):
    return item
```

Le modèle Pydantic est le même. Le code d'état passe dans la réponse :

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

Un corps qui ne correspond pas au modèle répond `422`, comme dans FastAPI.

## Plusieurs méthodes sur une seule URL

```python filename="main.py"
@app.get("/api/notes/{id}")
async def read_note(id: int): ...


@app.delete("/api/notes/{id}")
async def delete_note(id: int): ...
```

Un fichier contient toutes les méthodes d'une URL :

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Routeurs et préfixes

```python filename="main.py"
from fastapi import APIRouter

admin = APIRouter(prefix="/admin")


@admin.get("/stats")
async def stats():
    return {"users": 3}


app.include_router(admin)
```

Le dossier est le préfixe, et il n'y a rien à inclure :

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Dépendances sur un groupe de routes

```python filename="main.py"
from fastapi import Depends, Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
```

Un `dependencies.py` dans le dossier s'exécute avant chaque route située en dessous :

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

Une dépendance pour un gestionnaire est toujours `Depends`, dans sa signature :

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header


def current_user(authorization: str = Header(...)) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## Intergiciel

```python filename="main.py"
from fastapi import Request


@app.middleware("http")
async def add_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

Un `middleware.py` enveloppe les routes de son dossier, la racine les enveloppe toutes :

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## CORS, GZip et autres middlewares à l'échelle de l'application

```python filename="main.py"
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["https://example.com"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

Chacun est un champ de `nexyconfig.py`, avec les mêmes arguments :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## Pages HTML

```python filename="main.py"
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


@app.get("/users")
async def users_page(request: Request):
    users = [{"name": "Ada"}, {"name": "Alan"}]
    return templates.TemplateResponse(request, "users.html", {"users": users})
```

Une page `.nexy` contient le Python au-dessus de la ligne `---` et le Jinja2 en dessous, dans un seul fichier :

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

## Héritage de modèles

```html filename="modèles/base.html"
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

Un `layout.nexy` enveloppe chaque page de son dossier, sans `{% extends %}` dans les pages :

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Fichiers statiques

```python filename="main.py"
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

Les fichiers dans `public/` sont servis à partir de la racine : `public/robots.txt` est `/robots.txt`.

```text
public/
├─ robots.txt     /robots.txt
└─ logo.png       /logo.png
```

## Pages introuvables

```python filename="main.py"
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def not_found(request: Request, exc: StarletteHTTPException):
    return HTMLResponse("<h1>Not found</h1>", status_code=exc.status_code)
```

Un `notfound.nexy` répond aux navigateurs, et les clients API obtiennent toujours `{"detail": ...}` :

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## WebSockets

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

## Essais

```python filename="tests/test_main.py"
from fastapi.testclient import TestClient

from main import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

Le client est le même ; l'application vient de Nexy :

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Courir

| FastAPI | Nexy |
|---|---|
| `uvicorn main:app --reload` | `nx dev` |
| `uvicorn main:app --workers 4` | `nx build`, puis `nx start` |
| `/docs` de `FastAPI()` | `/docs`, répertoriant chaque `.py` itinéraire |

## Conserver une application existante

Vous n’êtes pas obligé de déplacer tous les itinéraires en même temps. Un `APIRouter` vous avez déjà des montures telles quelles :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Vos anciens itinéraires et les fichiers de `src/routes/` répondent alors côte à côte. Lorsque `useRouter` est défini, les pages `.nexy` ne sont pas encapsulées par `layout.nexy` : déplacez d'abord l'API, puis les pages, puis supprimez le champ. Voir [Intégration de routeur personnalisé](../routing/custom/README.md).

## Prochaines étapes

- [Gestionnaires de routes](../routing/fbr/handlers/README.md)
- [Dépendances et gardiens](../routing/fbr/dependencies/README.md)
- [Fichiers .nexy](../views/nexy/README.md)
- [Venant d'un autre cadre](../getting-started/coming-from-other-frameworks.md)
