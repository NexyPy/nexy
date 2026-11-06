# من FastAPI إلى النكسي

معالج Nexy هو معالج FastAPI في ملف مساره هو عنوان URL: تبقى نماذجك وتبعياتك و `/docs`، وتذهب أدوات الديكور واستدعاءات `include_router`.

كل قسم أدناه يوضح عادة FastAPI، ثم نفس الشيء في Nexy.

## نقطة نهاية

FastAPI يسجل دالة في تطبيق باستخدام مصمم ديكور:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/hello")
async def hello():
    return {"message": "Hello"}
```

يقرأ Nexy عنوان URL من مسار الملف والطريقة من اسم الوظيفة:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## معلمات المسار والاستعلام

```python filename="main.py"
@app.get("/api/users/{id}")
async def get_user(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

تصبح معلمة المسار مقطعًا `[id]` من اسم الملف. لا تتحرك معلمة الاستعلام:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` يجيب `404`، لأن `abc` ليس `int`.

## هيئة طلب

```python filename="main.py"
from pydantic import BaseModel


class NewItem(BaseModel):
    name: str
    price: float


@app.post("/api/items", status_code=201)
async def create_item(item: NewItem):
    return item
```

النموذج Pydantic هو نفسه. ينتقل رمز الحالة إلى الاستجابة:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

والجسم غير المطابق للنموذج يجيب `422`، كما في FastAPI.

## عدة طرق على عنوان URL واحد

```python filename="main.py"
@app.get("/api/notes/{id}")
async def read_note(id: int): ...


@app.delete("/api/notes/{id}")
async def delete_note(id: int): ...
```

يحتوي ملف واحد على كل طريقة لعنوان URL:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## أجهزة التوجيه والبادئات

```python filename="main.py"
from fastapi import APIRouter

admin = APIRouter(prefix="/admin")


@admin.get("/stats")
async def stats():
    return {"users": 3}


app.include_router(admin)
```

المجلد هو البادئة، ولا يوجد شيء لتضمينه:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## التبعيات على مجموعة من الطرق

```python filename="main.py"
from fastapi import Depends, Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
```

يتم تشغيل `dependencies.py` في المجلد قبل كل مسار أسفله:

```python filename="src/routes/admin/dependeency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

لا تزال التبعية لمعالج واحد `Depends`، في توقيعه:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header


def current_user(authorization: str = Header(...)) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## الوسيطة

```python filename="main.py"
from fastapi import Request


@app.middleware("http")
async def add_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

A `middleware.py` يغلف مسارات المجلد الخاص به، ويغلفها الجذر جميعًا:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## CORS وGZip وغيرها من البرامج الوسيطة على مستوى التطبيق

```python filename="main.py"
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["https://example.com"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

كل واحد هو حقل `nexyconfig.py`، مع نفس الوسائط:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## صفحات HTML

```python filename="main.py"
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


@app.get("/users")
async def users_page(request: Request):
    users = [{"name": "Ada"}, {"name": "Alan"}]
    return templates.TemplateResponse(request, "users.html", {"users": users})
```

صفحة `.nexy` تحتوي على Python أعلى السطر `---` و Jinja2 أسفله، في ملف واحد:

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

## وراثة القالب

```html filename="قوالب/base.html"
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

A `layout.nexy` يغلف كل صفحة من المجلد الخاص به، مع عدم وجود `{% extends %}` في الصفحات:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## الملفات الثابتة

```python filename="main.py"
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

يتم تقديم الملفات الموجودة في `public/` من الجذر: `public/robots.txt` هو `/robots.txt`.

```text
public/
├─ robots.txt     /robots.txt
└─ logo.png       /logo.png
```

## صفحات لم يتم العثور عليها

```python filename="main.py"
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def not_found(request: Request, exc: StarletteHTTPException):
    return HTMLResponse("<h1>Not found</h1>", status_code=exc.status_code)
```

يجيب `notfound.nexy` على المتصفحات، ولا يزال عملاء API يحصلون على `{"detail": ...}`:

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

## الاختبارات

```python filename="الاختبارات/test_main.py"
from fastapi.testclient import TestClient

from main import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

العميل هو نفسه؛ التطبيق يأتي من Nexy:

```python filename="الاختبارات/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## الجري

| FastAPI | نكسي |
|---|---|
| `uvicorn main:app --reload` | `nx dev` |
| `uvicorn main:app --workers 4` | `nx build`، ثم `nx start` |
| `/docs` من `FastAPI()` | `/docs`، سرد كل `.py` الطريق |

## الحفاظ على التطبيق الموجود

ليس عليك تحريك كل مسار مرة واحدة. `APIRouter` لديك بالفعل حوامل كما هي:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

مساراتك القديمة وملفات `src/routes/` ثم قم بالإجابة جنبًا إلى جنب. أثناء تعيين `useRouter`، لا يتم تغليف الصفحات `.nexy` بواسطة `layout.nexy`: انقل واجهة برمجة التطبيقات أولاً، ثم الصفحات، ثم قم بإزالة الحقل. راجع [تكامل جهاز التوجيه المخصص](../routing/custom/README.md).

## الخطوات التالية

- [معالجات الطريق](../routing/fbr/handlers/README.md)
- [التبعيات والحراس](../routing/fbr/dependencies/README.md)
- [ملفات .nexy](../views/nexy/README.md)
- [قادمة من إطار آخر](../getting-started/coming-from-other-frameworks.md)
