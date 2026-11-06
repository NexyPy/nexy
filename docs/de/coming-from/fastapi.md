# Von FastAPI zu Nexy

Ein Nexy-Handler ist ein FastAPI-Handler in einer Datei, deren Pfad die URL ist: Ihre Modelle, Abhängigkeiten und `/docs` bleiben erhalten, und die Dekoratoren und `include_router`-Aufrufe gehen.

Jeder Abschnitt unten zeigt eine FastAPI-Gewohnheit, dann dasselbe in Nexy.

## Ein Endpunkt

FastAPI registriert eine Funktion in einer App mit einem Dekorator:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/hello")
async def hello():
    return {"message": "Hello"}
```

Nexy liest die URL aus dem Dateipfad und die Methode aus dem Funktionsnamen:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Pfad- und Abfrageparameter

```python filename="main.py"
@app.get("/api/users/{id}")
async def get_user(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

Der Pfadparameter wird zu einem `[id]`-Segment des Dateinamens. Der Abfrageparameter wird nicht verschoben:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` antwortet auf `404`, weil `abc` kein `int` ist.

## Ein Anforderungstext

```python filename="main.py"
from pydantic import BaseModel


class NewItem(BaseModel):
    name: str
    price: float


@app.post("/api/items", status_code=201)
async def create_item(item: NewItem):
    return item
```

Das Pydantic-Modell ist das gleiche. Der Statuscode wird in die Antwort verschoben:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

Ein Körper, der nicht mit dem Modell übereinstimmt, antwortet `422`, wie in FastAPI.

## Mehrere Methoden auf einer URL

```python filename="main.py"
@app.get("/api/notes/{id}")
async def read_note(id: int): ...


@app.delete("/api/notes/{id}")
async def delete_note(id: int): ...
```

Eine Datei enthält jede Methode einer URL:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Router und Präfixe

```python filename="main.py"
from fastapi import APIRouter

admin = APIRouter(prefix="/admin")


@admin.get("/stats")
async def stats():
    return {"users": 3}


app.include_router(admin)
```

Der Ordner ist das Präfix und es gibt nichts einzuschließen:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Abhängigkeiten von einer Gruppe von Routen

```python filename="main.py"
from fastapi import Depends, Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
```

Ein `dependencies.py` im Ordner wird vor jeder Route darunter ausgeführt:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

Eine Abhängigkeit für einen Handler ist immer noch `Depends`, in seiner Signatur:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header


def current_user(authorization: str = Header(...)) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## Middleware

```python filename="main.py"
from fastapi import Request


@app.middleware("http")
async def add_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

Ein `middleware.py` umschließt die Routen seines Ordners, der Root-Ordner umschließt sie alle:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## CORS, GZip und andere App-weite Middleware

```python filename="main.py"
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["https://example.com"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

Jedes ist ein Feld von `nexyconfig.py` mit denselben Argumenten:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## HTML-Seiten

```python filename="main.py"
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


@app.get("/users")
async def users_page(request: Request):
    users = [{"name": "Ada"}, {"name": "Alan"}]
    return templates.TemplateResponse(request, "users.html", {"users": users})
```

Eine `.nexy`-Seite enthält das Python über der Zeile `---` und das Jinja2 darunter in einer Datei:

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

## Vorlagenvererbung

```html filename="templates/base.html"
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

Ein `layout.nexy` umschließt jede Seite seines Ordners, ohne `{% extends %}` in den Seiten:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Statische Dateien

```python filename="main.py"
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

Dateien in `public/` werden vom Stammverzeichnis aus bereitgestellt: `public/robots.txt` ist `/robots.txt`.

```text
public/
├─ robots.txt     /robots.txt
└─ logo.png       /logo.png
```

## Nicht gefundene Seiten

```python filename="main.py"
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def not_found(request: Request, exc: StarletteHTTPException):
    return HTMLResponse("<h1>Not found</h1>", status_code=exc.status_code)
```

Ein `notfound.nexy` antwortet Browsern und API-Clients erhalten weiterhin `{"detail": ...}`:

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

## Tests

```python filename="tests/test_main.py"
from fastapi.testclient import TestClient

from main import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

Der Kunde ist derselbe; Die App kommt von Nexy:

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Laufen

| FastAPI | Nexy |
|---|---|
| `uvicorn main:app --reload` | `nx dev` |
| `uvicorn main:app --workers 4` | `nx build`, dann `nx start` |
| `/docs` von `FastAPI()` | `/docs`, Auflistung aller `.py` Routen |

## Bestehende App beibehalten

Sie müssen nicht jede Route auf einmal verschieben. Ein `APIRouter` Sie haben bereits Reittiere wie sie sind:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Ihre alten Routen und die Dateien von `src/routes/` antworten dann nebeneinander. Während `useRouter` festgelegt ist, werden `.nexy`-Seiten nicht von `layout.nexy` umbrochen: Verschieben Sie zuerst die API, dann die Seiten und dann das Feld. Siehe [Benutzerdefinierte Router-Integration](../routing/custom/README.md).

## Nächste Schritte

- [Routenhandler](../routing/fbr/handlers/README.md)
- [Abhängigkeiten und Wachen](../routing/fbr/dependencies/README.md)
- [.nexy-Dateien](../views/nexy/README.md)
- [Aus einem anderen Rahmen kommend](../getting-started/coming-from-other-frameworks.md)
