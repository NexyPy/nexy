# From FastAPI to Nexy

Nexy is FastAPI with the route written as a file: a function that answers under `@app.get("/x")`
answers in `src/routes/x.py` as `GET`, and the rest of your code stays the same.

## What stays, what changes

Nexy serves your handlers with FastAPI itself, so everything inside a handler works unchanged:

| Stays the same | Changes |
|---|---|
| Pydantic models, request bodies and responses | `@app.get("/x")` becomes `src/routes/x.py` with `async def GET()` |
| `Depends`, `Query`, `Header`, `Cookie`, `Form`, `File` | `{id}` in the path becomes a `[id].py` file or `[id]/` folder |
| `HTTPException`, `status`, `JSONResponse`, `RedirectResponse` | `APIRouter(prefix="/users")` becomes the folder `users/` |
| `Request`, `BackgroundTasks`, `UploadFile`, WebSockets | `dependencies=[...]` on a router becomes a `dependencies.py` file |
| Middleware classes, `/docs`, `TestClient` | `app.add_middleware(...)` becomes a field of `nexyconfig.py`: `useCORS`, `useGZip`, `useMiddlewares` |

Import them from `fastapi` as before, or from `nexy.http`, which re-exports the same objects.

Each section below shows a FastAPI habit, then the same thing in Nexy.

## An endpoint

FastAPI registers a function on an app with a decorator:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/hello")
async def hello():
    return {"message": "Hello"}
```

Nexy reads the URL from the file path and the method from the function name:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Path and query parameters

```python filename="main.py"
@app.get("/api/users/{id}")
async def get_user(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

The path parameter becomes a `[id]` segment of the file name. The query parameter does not move:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` answers `404`, because `abc` is not an `int`.

## A request body

```python filename="main.py"
from pydantic import BaseModel


class NewItem(BaseModel):
    name: str
    price: float


@app.post("/api/items", status_code=201)
async def create_item(item: NewItem):
    return item
```

The Pydantic model is the same. The status code moves into the response:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

A body that does not match the model answers `422`, as in FastAPI.

## Several methods on one URL

```python filename="main.py"
@app.get("/api/notes/{id}")
async def read_note(id: int): ...


@app.delete("/api/notes/{id}")
async def delete_note(id: int): ...
```

One file holds every method of a URL:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Routers and prefixes

```python filename="main.py"
from fastapi import APIRouter

admin = APIRouter(prefix="/admin")


@admin.get("/stats")
async def stats():
    return {"users": 3}


app.include_router(admin)
```

The folder is the prefix, and there is nothing to include:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Dependencies on a group of routes

```python filename="main.py"
from fastapi import Depends, Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
```

A `dependencies.py` in the folder runs before every route below it:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

A dependency for one handler is still `Depends`, in its signature:

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

A `middleware.py` wraps the routes of its folder, the root one wraps them all:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## CORS, GZip and other app-wide middleware

```python filename="main.py"
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["https://example.com"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

Each one is a field of `nexyconfig.py`, with the same arguments:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## HTML pages

```python filename="main.py"
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


@app.get("/users")
async def users_page(request: Request):
    users = [{"name": "Ada"}, {"name": "Alan"}]
    return templates.TemplateResponse(request, "users.html", {"users": users})
```

A `.nexy` page holds the Python above the `---` line and the Jinja2 below it, in one file:

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

## Template inheritance

```html filename="templates/base.html"
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

A `layout.nexy` wraps every page of its folder, with no `{% extends %}` in the pages:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Static files

```python filename="main.py"
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

Files in `public/` are served from the root: `public/robots.txt` is `/robots.txt`.

```text
public/
├─ robots.txt     /robots.txt
└─ logo.png       /logo.png
```

## Not-found pages

```python filename="main.py"
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def not_found(request: Request, exc: StarletteHTTPException):
    return HTMLResponse("<h1>Not found</h1>", status_code=exc.status_code)
```

A `notfound.nexy` answers browsers, and API clients still get `{"detail": ...}`:

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

The client is the same; the app comes from Nexy:

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Running

| FastAPI | Nexy |
|---|---|
| `uvicorn main:app --reload` | `nx dev` |
| `uvicorn main:app --workers 4` | `nx build`, then `nx start` |
| `/docs` from `FastAPI()` | `/docs`, listing every `.py` route |

## Keeping an existing app

You do not have to move every route at once. An `APIRouter` you already have mounts as it is:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Your old routes and the files of `src/routes/` then answer side by side. While `useRouter` is set,
`.nexy` pages are not wrapped by `layout.nexy`: move the API first, then the pages, then remove the
field. See [Custom router integration](../routing/custom/README.md).

## Next steps

- [Route handlers](../routing/fbr/handlers/README.md)
- [Dependencies and guards](../routing/fbr/dependencies/README.md)
- [.nexy files](../views/nexy/README.md)
- [Coming from another framework](../getting-started/coming-from-other-frameworks.md)
