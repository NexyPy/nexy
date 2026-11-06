# De FastAPI a Nexy

Un controlador Nexy es un controlador FastAPI en un archivo cuya ruta es la URL: sus modelos, dependencias y `/docs` permanecen, y los decoradores y las llamadas `include_router` se van.

Cada sección a continuación muestra un hábito FastAPI, luego lo mismo en Nexy.

## Un punto final

FastAPI registra una función en una aplicación con un decorador:

```python filename="principal.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/hello")
async def hello():
    return {"message": "Hello"}
```

Nexy lee la URL de la ruta del archivo y el método del nombre de la función:

```python filename="src/rutas/api/hola.py"
async def GET():
    return {"message": "Hello"}
```

## Parámetros de ruta y consulta

```python filename="principal.py"
@app.get("/api/users/{id}")
async def get_user(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

El parámetro de ruta se convierte en un segmento `[id]` del nombre del archivo. El parámetro de consulta no se mueve:

```python filename="src/rutas/api/usuarios/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` responde a `404`, porque `abc` no es un `int`.

## Un cuerpo de solicitud

```python filename="principal.py"
from pydantic import BaseModel


class NewItem(BaseModel):
    name: str
    price: float


@app.post("/api/items", status_code=201)
async def create_item(item: NewItem):
    return item
```

El modelo Pydantic es el mismo. El código de estado pasa a la respuesta:

```python filename="src/rutas/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

Un cuerpo que no coincide con el modelo responde `422`, como en FastAPI.

## Varios métodos en una URL

```python filename="principal.py"
@app.get("/api/notes/{id}")
async def read_note(id: int): ...


@app.delete("/api/notes/{id}")
async def delete_note(id: int): ...
```

Un archivo contiene todos los métodos de una URL:

```python filename="src/rutas/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Enrutadores y prefijos

```python filename="principal.py"
from fastapi import APIRouter

admin = APIRouter(prefix="/admin")


@admin.get("/stats")
async def stats():
    return {"users": 3}


app.include_router(admin)
```

La carpeta es el prefijo y no hay nada que incluir:

```python filename="src/rutas/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Dependencias de un grupo de rutas.

```python filename="principal.py"
from fastapi import Depends, Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
```

Un `dependencies.py` en la carpeta se ejecuta antes de cada ruta debajo de ella:

```python filename="src/rutas/admin/dependencias.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

Una dependencia para un controlador sigue siendo `Depends`, en su firma:

```python filename="src/rutas/api/me.py"
from nexy.http import Depends, Header


def current_user(authorization: str = Header(...)) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## software intermedio

```python filename="principal.py"
from fastapi import Request


@app.middleware("http")
async def add_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

Un `middleware.py` envuelve las rutas de su carpeta, la raíz las envuelve todas:

```python filename="src/rutas/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## CORS, GZip y otro middleware para toda la aplicación

```python filename="principal.py"
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["https://example.com"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

Cada uno es un campo de `nexyconfig.py`, con los mismos argumentos:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## páginas HTML

```python filename="principal.py"
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


@app.get("/users")
async def users_page(request: Request):
    users = [{"name": "Ada"}, {"name": "Alan"}]
    return templates.TemplateResponse(request, "users.html", {"users": users})
```

Una página `.nexy` contiene el Python encima de la línea `---` y el Jinja2 debajo de ella, en un archivo:

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

## Herencia de plantilla

```html filename="plantillas/base.html"
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

Un `layout.nexy` envuelve cada página de su carpeta, sin `{% extends %}` en las páginas:

```nexy filename="src/rutas/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Archivos estáticos

```python filename="principal.py"
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

Los archivos en `public/` se sirven desde la raíz: `public/robots.txt` es `/robots.txt`.

```text
public/
├─ robots.txt     /robots.txt
└─ logo.png       /logo.png
```

## Paginas no encontradas

```python filename="principal.py"
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def not_found(request: Request, exc: StarletteHTTPException):
    return HTMLResponse("<h1>Not found</h1>", status_code=exc.status_code)
```

Un `notfound.nexy` responde a los navegadores y los clientes API aún obtienen `{"detail": ...}`:

```nexy filename="src/rutas/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## WebSockets

```python filename="principal.py"
from fastapi import WebSocket


@app.websocket("/ws/echo")
async def echo(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

```python filename="src/rutas/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## Pruebas

```python filename="pruebas/test_main.py"
from fastapi.testclient import TestClient

from main import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

El cliente es el mismo; la aplicación proviene de Nexy:

```python filename="pruebas/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## corriendo

| FastAPI | nexy |
|---|---|
| `uvicorn main:app --reload` | `nx dev` |
| `uvicorn main:app --workers 4` | `nx build`, luego `nx start` |
| `/docs` de `FastAPI()` | `/docs`, enumerando cada `.py` ruta |

## Mantener una aplicación existente

No es necesario moverse por todas las rutas a la vez. Un `APIRouter` ya lo tienes montado tal cual:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Sus rutas antiguas y los archivos de `src/routes/` luego responden uno al lado del otro. Mientras `useRouter` está configurado, las páginas `.nexy` no están empaquetadas por `layout.nexy`: mueva la API primero, luego las páginas y luego elimine el campo. Consulte [Integración de enrutador personalizado](../routing/custom/README.md).

## Próximos pasos

- [Controladores de ruta](../routing/fbr/handlers/README.md)
- [Dependencias y guardias](../routing/fbr/dependencies/README.md)
- [Archivos .nexy](../views/nexy/README.md)
- [Procedente de otro marco](../getting-started/coming-from-other-frameworks.md)
