# De FastAPI para Nexy

Um manipulador Nexy é um manipulador FastAPI em um arquivo cujo caminho é a URL: seus modelos, dependências e `/docs` permanecem, e os decoradores e as chamadas `include_router` vão.

Cada seção abaixo mostra um hábito FastAPI, então a mesma coisa no Nexy.

## Um ponto final

FastAPI registra uma função em um aplicativo com um decorador:

```python filename="principal.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/hello")
async def hello():
    return {"message": "Hello"}
```

Nexy lê o URL do caminho do arquivo e o método do nome da função:

```python filename="src/rotas/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Parâmetros de caminho e consulta

```python filename="principal.py"
@app.get("/api/users/{id}")
async def get_user(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

O parâmetro path se torna um segmento `[id]` do nome do arquivo. O parâmetro de consulta não se move:

```python filename="src/rotas/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` responde `404`, porque `abc` não é um `int`.

## Um corpo de solicitação

```python filename="principal.py"
from pydantic import BaseModel


class NewItem(BaseModel):
    name: str
    price: float


@app.post("/api/items", status_code=201)
async def create_item(item: NewItem):
    return item
```

O modelo Pydantic é o mesmo. O código de status passa para a resposta:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

Um corpo que não corresponde ao modelo responde `422`, como em FastAPI.

## Vários métodos em um URL

```python filename="principal.py"
@app.get("/api/notes/{id}")
async def read_note(id: int): ...


@app.delete("/api/notes/{id}")
async def delete_note(id: int): ...
```

Um arquivo contém todos os métodos de uma URL:

```python filename="src/rotas/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Roteadores e prefixos

```python filename="principal.py"
from fastapi import APIRouter

admin = APIRouter(prefix="/admin")


@admin.get("/stats")
async def stats():
    return {"users": 3}


app.include_router(admin)
```

A pasta é o prefixo e não há nada a incluir:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Dependências de um grupo de rotas

```python filename="principal.py"
from fastapi import Depends, Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
```

Um `dependencies.py` na pasta é executado antes de cada rota abaixo dela:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

Uma dependência para um manipulador ainda é `Depends`, em sua assinatura:

```python filename="src/rotas/api/me.py"
from nexy.http import Depends, Header


def current_user(authorization: str = Header(...)) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## Middleware

```python filename="principal.py"
from fastapi import Request


@app.middleware("http")
async def add_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

Um `middleware.py` agrupa as rotas de sua pasta, o root agrupa todas elas:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## CORS, GZip e outros middlewares para todo o aplicativo

```python filename="principal.py"
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["https://example.com"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

Cada um é um campo de `nexyconfig.py`, com os mesmos argumentos:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## Páginas HTML

```python filename="principal.py"
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


@app.get("/users")
async def users_page(request: Request):
    users = [{"name": "Ada"}, {"name": "Alan"}]
    return templates.TemplateResponse(request, "users.html", {"users": users})
```

Uma página `.nexy` contém o Python acima da linha `---` e o Jinja2 abaixo dela, em um arquivo:

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

## Herança de modelo

```html filename="modelos/base.html"
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

Um `layout.nexy` envolve todas as páginas de sua pasta, sem `{% extends %}` nas páginas:

```nexy filename="src/rotas/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Arquivos estáticos

```python filename="principal.py"
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

Os arquivos em `public/` são servidos a partir da raiz: `public/robots.txt` é `/robots.txt`.

```text
public/
├─ robots.txt     /robots.txt
└─ logo.png       /logo.png
```

## Páginas não encontradas

```python filename="principal.py"
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def not_found(request: Request, exc: StarletteHTTPException):
    return HTMLResponse("<h1>Not found</h1>", status_code=exc.status_code)
```

Um `notfound.nexy` responde aos navegadores, e os clientes da API ainda recebem `{"detail": ...}`:

```nexy filename="src/rotas/notfound.nexy"
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

```python filename="src/rotas/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## Testes

```python filename="testes/test_main.py"
from fastapi.testclient import TestClient

from main import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

O cliente é o mesmo; o aplicativo vem da Nexy:

```python filename="testes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Correndo

| FastAPI | Nexy |
|---|---|
| `uvicorn main:app --reload` | `nx dev` |
| `uvicorn main:app --workers 4` | `nx build`, então `nx start` |
| `/docs` de `FastAPI()` | `/docs`, listando todas as `.py` rotas |

## Manter um aplicativo existente

Você não precisa mover todas as rotas ao mesmo tempo. Um `APIRouter` você já tem montagens como estão:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Suas rotas antigas e os arquivos de `src/routes/` respondem lado a lado. Enquanto `useRouter` estiver definido, `.nexy` páginas não serão agrupadas por `layout.nexy`: mova primeiro a API, depois as páginas e, em seguida, remova o campo. Consulte [Integração de roteador personalizado](../routing/custom/README.md).

## Próximas etapas

- [Manipuladores de rota](../routing/fbr/handlers/README.md)
- [Dependências e guardas](../routing/fbr/dependencies/README.md)
- [Arquivos .nexy](../views/nexy/README.md)
- [Vindo de outra estrutura](../getting-started/coming-from-other-frameworks.md)
