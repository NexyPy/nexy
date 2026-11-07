# Dari FastAPI hingga Nexy

Nexy adalah FastAPI dengan rute yang ditulis sebagai file: fungsi yang menjawab di bawah `@app.get("/x")` menjawab di `src/routes/x.py` sebagai `GET`, dan kode Anda lainnya tetap sama.

## Apa yang bertahan, apa yang berubah

Nexy melayani penangan Anda dengan FastAPI itu sendiri, sehingga semua yang ada di dalam penangan berfungsi tidak berubah:

| Tetap sama | Perubahan |
|---|---|
| Pydantic model, badan permintaan dan tanggapan | `@app.get("/x")` menjadi `src/routes/x.py` dengan `async def GET()` |
| `Depends`, `Query`, `Header`, `Cookie`, `Form`, `File` | `{id}` di jalur menjadi file `[id].py` atau folder `[id]/`. |
| `HTTPException`, `status`, `JSONResponse`, `RedirectResponse` | `APIRouter(prefix="/users")` menjadi folder `users/` |
| `Request`, `BackgroundTasks`, `UploadFile`, WebSockets | `dependencies=[...]` pada router menjadi file `dependencies.py` |
| Kelas middleware, `/docs`, `TestClient` | `app.add_middleware(...)` menjadi bidang `nexyconfig.py`: `useCORS`, `useGZip`, `useMiddlewares` |

Impornya dari `fastapi` seperti sebelumnya, atau dari `nexy.http`, yang mengekspor ulang objek yang sama.

Setiap bagian di bawah menunjukkan kebiasaan FastAPI, lalu hal yang sama di Nexy.

## Sebuah titik akhir

FastAPI mendaftarkan fungsi pada aplikasi dengan dekorator:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/hello")
async def hello():
    return {"message": "Hello"}
```

Nexy membaca URL dari jalur file dan metode dari nama fungsi:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Parameter jalur dan kueri

```python filename="main.py"
@app.get("/api/users/{id}")
async def get_user(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

Parameter jalur menjadi segmen `[id]` dari nama file. Parameter kueri tidak berpindah:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` menjawab `404`, karena `abc` bukan `int`.

## Badan permintaan

```python filename="main.py"
from pydantic import BaseModel


class NewItem(BaseModel):
    name: str
    price: float


@app.post("/api/items", status_code=201)
async def create_item(item: NewItem):
    return item
```

Model Pydantic juga sama. Kode status berpindah ke respons:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

Badan yang tidak cocok dengan model menjawab `422`, seperti pada FastAPI.

## Beberapa metode pada satu URL

```python filename="main.py"
@app.get("/api/notes/{id}")
async def read_note(id: int): ...


@app.delete("/api/notes/{id}")
async def delete_note(id: int): ...
```

Satu file menampung setiap metode URL:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Router dan awalan

```python filename="main.py"
from fastapi import APIRouter

admin = APIRouter(prefix="/admin")


@admin.get("/stats")
async def stats():
    return {"users": 3}


app.include_router(admin)
```

Foldernya adalah awalan, dan tidak ada yang perlu disertakan:

```python filename="src/route/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Ketergantungan pada sekelompok rute

```python filename="main.py"
from fastapi import Depends, Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
```

A `dependencies.py` dalam folder dijalankan sebelum setiap rute di bawahnya:

```python filename="src/rute/admin/dependensi.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

Ketergantungan untuk satu penangan masih `Depends`, dalam tanda tangannya:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header


def current_user(authorization: str = Header(...)) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## Perangkat Tengah

```python filename="main.py"
from fastapi import Request


@app.middleware("http")
async def add_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

A `middleware.py` membungkus rute foldernya, root membungkus semuanya:

```python filename="src/rute/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## CORS, GZip, dan middleware seluruh aplikasi lainnya

```python filename="main.py"
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["https://example.com"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

Masing-masing adalah bidang `nexyconfig.py`, dengan argumen yang sama:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## halaman HTML

```python filename="main.py"
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


@app.get("/users")
async def users_page(request: Request):
    users = [{"name": "Ada"}, {"name": "Alan"}]
    return templates.TemplateResponse(request, "users.html", {"users": users})
```

Halaman `.nexy` menampung Python di atas baris `---` dan Jinja2 di bawahnya, dalam satu file:

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

## Warisan templat

```html filename="templat/base.html"
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

`layout.nexy` membungkus setiap halaman foldernya, tanpa `{% extends %}` di halaman:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## File statis

```python filename="main.py"
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

File di `public/` disajikan dari root: `public/robots.txt` adalah `/robots.txt`.

```text
public/
├─ robots.txt     /robots.txt
└─ logo.png       /logo.png
```

## Halaman tidak ditemukan

```python filename="main.py"
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def not_found(request: Request, exc: StarletteHTTPException):
    return HTMLResponse("<h1>Not found</h1>", status_code=exc.status_code)
```

A `notfound.nexy` menjawab browser, dan klien API masih mendapatkan `{"detail": ...}`:

```nexy filename="src/rute/tidak ditemukan.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## soket web

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

## Tes

```python filename="tes/test_main.py"
from fastapi.testclient import TestClient

from main import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

Kliennya sama; aplikasi ini berasal dari Nexy:

```python filename="tes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Berlari

| FastAPI | Nexy |
|---|---|
| `uvicorn main:app --reload` | `nx dev` |
| `uvicorn main:app --workers 4` | `nx build`, lalu `nx start` |
| `/docs` dari `FastAPI()` | `/docs`, mencantumkan setiap `.py` rute |

## Mempertahankan aplikasi yang sudah ada

Anda tidak harus berpindah setiap rute sekaligus. Sebuah `APIRouter` Anda sudah memiliki tunggangan apa adanya:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Rute lama Anda dan file `src/routes/` lalu jawab secara berdampingan. Saat `useRouter` disetel, halaman `.nexy` tidak dibungkus dengan `layout.nexy`: pindahkan API terlebih dahulu, lalu halamannya, lalu hapus bidangnya. Lihat [Integrasi router khusus](../routing/custom/README.md).

## Langkah selanjutnya

- [Penangan rute](../routing/fbr/handlers/README.md)
- [Ketergantungan dan penjaga](../routing/fbr/dependencies/README.md)
- [file .nexy](../views/nexy/README.md)
- [Berasal dari kerangka lain](../getting-started/coming-from-other-frameworks.md)
