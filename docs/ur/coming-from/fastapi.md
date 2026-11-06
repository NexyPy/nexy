# FastAPI سے Nexy تک

Nexy ایک فائل کے طور پر لکھے گئے راستے کے ساتھ FastAPI ہے: ایک فنکشن جو `@app.get("/x")` کے تحت جوابات `src/routes/x.py` میں `GET` کے طور پر دیتا ہے، اور آپ کا باقی کوڈ وہی رہتا ہے۔

## کیا رہتا ہے، کیا بدلتا ہے۔

Nexy آپ کے ہینڈلرز کو خود FastAPI کے ساتھ کام کرتا ہے، لہذا ہینڈلر کے اندر موجود ہر چیز بغیر کسی تبدیلی کے کام کرتی ہے:

| وہی رہتا ہے۔ | تبدیلیاں |
|---|---|
| Pydantic ماڈلز، باڈیز اور جوابات کی درخواست کرتے ہیں۔ | `@app.get("/x")` `async def GET()` کے ساتھ `src/routes/x.py` بن جاتا ہے۔ |
| `Depends`، `Query`، `Header`، `Cookie`، `Form`، `File` | راستے میں `{id}` ایک `[id].py` فائل یا `[id]/` فولڈر بن جاتا ہے۔ |
| `HTTPException`، `status`، `JSONResponse`، `RedirectResponse` | `APIRouter(prefix="/users")` فولڈر بن جاتا ہے `users/` |
| `Request`، `BackgroundTasks`، `UploadFile`، ویب ساکٹس | روٹر پر `dependencies=[...]` ایک `dependencies.py` فائل بن جاتی ہے۔ |
| مڈل ویئر کلاسز، `/docs`، `TestClient` | `app.add_middleware(...)` ایک میدان بن جاتا ہے `nexyconfig.py`: `useCORS`، `useGZip`، `useMiddlewares` |

انہیں پہلے کی طرح `fastapi` سے درآمد کریں، یا `nexy.http` سے، جو وہی اشیاء کو دوبارہ برآمد کرتا ہے۔

ذیل میں ہر سیکشن ایک FastAPI عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔

## ایک اختتامی نقطہ

FastAPI ڈیکوریٹر کے ساتھ ایپ پر ایک فنکشن رجسٹر کرتا ہے:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/hello")
async def hello():
    return {"message": "Hello"}
```

Nexy فائل پاتھ سے URL اور فنکشن کے نام سے طریقہ پڑھتا ہے:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## راستہ اور استفسار کے پیرامیٹرز

```python filename="main.py"
@app.get("/api/users/{id}")
async def get_user(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

پاتھ پیرامیٹر فائل کے نام کا ایک `[id]` سیگمنٹ بن جاتا ہے۔ استفسار پیرامیٹر منتقل نہیں ہوتا ہے:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` جواب دیتا ہے `404`، کیونکہ `abc` ایک `int` نہیں ہے۔

## ایک درخواست جسم

```python filename="main.py"
from pydantic import BaseModel


class NewItem(BaseModel):
    name: str
    price: float


@app.post("/api/items", status_code=201)
async def create_item(item: NewItem):
    return item
```

Pydantic ماڈل ایک ہی ہے۔ اسٹیٹس کوڈ جواب میں منتقل ہوتا ہے:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

ایک جسم جو ماڈل کے جوابات سے میل نہیں کھاتا ہے `422`، جیسا کہ FastAPI میں ہے۔

## ایک URL پر کئی طریقے

```python filename="main.py"
@app.get("/api/notes/{id}")
async def read_note(id: int): ...


@app.delete("/api/notes/{id}")
async def delete_note(id: int): ...
```

ایک فائل میں URL کا ہر طریقہ ہوتا ہے:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## راؤٹرز اور سابقے

```python filename="main.py"
from fastapi import APIRouter

admin = APIRouter(prefix="/admin")


@admin.get("/stats")
async def stats():
    return {"users": 3}


app.include_router(admin)
```

فولڈر سابقہ ہے، اور اس میں شامل کرنے کے لیے کچھ نہیں ہے:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## راستوں کے ایک گروپ پر انحصار

```python filename="main.py"
from fastapi import Depends, Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
```

فولڈر میں ایک `dependencies.py` اس کے نیچے ہر راستے سے پہلے چلتا ہے:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

ایک ہینڈلر کے لیے انحصار اب بھی ہے `Depends`، اس کے دستخط میں:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header


def current_user(authorization: str = Header(...)) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## مڈل ویئر

```python filename="main.py"
from fastapi import Request


@app.middleware("http")
async def add_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

A `middleware.py` اپنے فولڈر کے راستوں کو سمیٹتا ہے، جڑ والا ان سب کو سمیٹتا ہے:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## CORS، GZip اور دیگر ایپ وسیع مڈل ویئر

```python filename="main.py"
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["https://example.com"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

ہر ایک `nexyconfig.py` کا ایک میدان ہے، اسی دلائل کے ساتھ:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## HTML صفحات

```python filename="main.py"
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


@app.get("/users")
async def users_page(request: Request):
    users = [{"name": "Ada"}, {"name": "Alan"}]
    return templates.TemplateResponse(request, "users.html", {"users": users})
```

ایک `.nexy` صفحہ Python کو `---` لائن کے اوپر اور اس کے نیچے Jinja2 کو ایک فائل میں رکھتا ہے:

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

## ٹیمپلیٹ وراثت

```html filename="templates/base.html"
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

ایک `layout.nexy` اپنے فولڈر کے ہر صفحے کو سمیٹتا ہے، صفحات میں `{% extends %}` کے بغیر:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## جامد فائلیں۔

```python filename="main.py"
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

`public/` میں فائلیں روٹ سے پیش کی جاتی ہیں: `public/robots.txt` ہے `/robots.txt`۔

```text
public/
├─ robots.txt     /robots.txt
└─ logo.png       /logo.png
```

## نہ ملے صفحات

```python filename="main.py"
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def not_found(request: Request, exc: StarletteHTTPException):
    return HTMLResponse("<h1>Not found</h1>", status_code=exc.status_code)
```

A `notfound.nexy` براؤزرز کو جواب دیتا ہے، اور API کلائنٹس کو اب بھی `{"detail": ...}` ملتا ہے:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## ویب ساکٹس

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

## ٹیسٹ

```python filename="tests/test_main.py"
from fastapi.testclient import TestClient

from main import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

کلائنٹ ایک ہی ہے؛ ایپ Nexy سے آتی ہے:

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## چل رہا ہے۔

| FastAPI | نیکسی |
|---|---|
| `uvicorn main:app --reload` | `nx dev` |
| `uvicorn main:app --workers 4` | `nx build`، پھر `nx start` |
| `/docs` سے `FastAPI()` | `/docs`، ہر `.py` راستے کی فہرست |

## موجودہ ایپ کو برقرار رکھنا

آپ کو ہر راستے کو ایک ساتھ منتقل کرنے کی ضرورت نہیں ہے۔ ایک `APIRouter` آپ کے پاس پہلے سے ہی ماؤنٹس ہیں جیسا کہ یہ ہے:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

آپ کے پرانے راستے اور `src/routes/` کی فائلیں تو ساتھ ساتھ جواب دیں۔ جبکہ `useRouter` سیٹ ہے، `.nexy` صفحات کو `layout.nexy` کے ذریعے لپیٹ نہیں کیا جاتا ہے: پہلے API کو منتقل کریں، پھر صفحات، پھر فیلڈ کو ہٹا دیں۔ دیکھیں [کسٹم راؤٹر انٹیگریشن](../routing/custom/README.md)۔

## اگلے اقدامات

- [روٹ ہینڈلر](../routing/fbr/handlers/README.md)
- [انحصار اور محافظ ](../routing/fbr/dependencies/README.md)
- [.nexy فائلیں](../views/nexy/README.md)
- [دوسرے فریم ورک سے آرہا ہے](../getting-started/coming-from-other-frameworks.md)
