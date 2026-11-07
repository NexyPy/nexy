# FastAPI থেকে নেক্সি পর্যন্ত

Nexy হল FastAPI একটি ফাইল হিসাবে লেখা রুট সহ: একটি ফাংশন যা `@app.get("/x")` এর অধীনে উত্তর দেয় `src/routes/x.py` হিসাবে `GET`, এবং আপনার বাকি কোড একই থাকে।

## কি থাকে, কি পরিবর্তন হয়

Nexy আপনার হ্যান্ডলারগুলিকে FastAPI দিয়েই পরিবেশন করে, তাই হ্যান্ডলারের ভিতরে সবকিছু অপরিবর্তিত কাজ করে:

| একই থাকে | পরিবর্তন |
|---|---|
| Pydantic মডেল, অনুরোধ সংস্থা এবং প্রতিক্রিয়া | `@app.get("/x")` `async def GET()` এর সাথে `src/routes/x.py` হয়ে যায় |
| `Depends`, `Query`, `Header`, `Cookie`, `Form`, `File` | পাথে `{id}` একটি `[id].py` ফাইল বা `[id]/` ফোল্ডার হয়ে যায় |
| `HTTPException`, `status`, `JSONResponse`, `RedirectResponse` | `APIRouter(prefix="/users")` ফোল্ডার হয়ে যায় `users/` |
| `Request`, `BackgroundTasks`, `UploadFile`, ওয়েবসকেট | একটি রাউটারে `dependencies=[...]` একটি `dependencies.py` ফাইল হয়ে যায় |
| মিডলওয়্যার ক্লাস, `/docs`, `TestClient` | `app.add_middleware(...)` একটি ক্ষেত্র হয়ে যায় `nexyconfig.py`: `useCORS`, `useGZip`, `useMiddlewares` |

আগের মতই `fastapi` থেকে অথবা `nexy.http` থেকে এগুলি আমদানি করুন, যা একই বস্তুকে পুনরায় রপ্তানি করে।

নীচের প্রতিটি বিভাগ একটি FastAPI অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস।

## একটি শেষ বিন্দু

FastAPI একটি ডেকোরেটরের সাথে একটি অ্যাপে একটি ফাংশন নিবন্ধন করে:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/hello")
async def hello():
    return {"message": "Hello"}
```

Nexy ফাইল পাথ থেকে URL এবং ফাংশনের নাম থেকে পদ্ধতিটি পড়ে:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## পাথ এবং ক্যোয়ারী প্যারামিটার

```python filename="main.py"
@app.get("/api/users/{id}")
async def get_user(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

পাথ প্যারামিটার ফাইল নামের একটি `[id]` সেগমেন্ট হয়ে যায়। ক্যোয়ারী প্যারামিটার সরে না:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` উত্তর দেয় `404`, কারণ `abc` একটি `int` নয়।

## একটি অনুরোধ শরীর

```python filename="main.py"
from pydantic import BaseModel


class NewItem(BaseModel):
    name: str
    price: float


@app.post("/api/items", status_code=201)
async def create_item(item: NewItem):
    return item
```

Pydantic মডেল একই। স্ট্যাটাস কোড প্রতিক্রিয়াতে চলে যায়:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

একটি শরীর যা মডেলের সাথে মেলে না উত্তর দেয় `422`, যেমন FastAPI।

## একটি ইউআরএলে বিভিন্ন পদ্ধতি

```python filename="main.py"
@app.get("/api/notes/{id}")
async def read_note(id: int): ...


@app.delete("/api/notes/{id}")
async def delete_note(id: int): ...
```

একটি ফাইল একটি URL এর প্রতিটি পদ্ধতি ধারণ করে:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## রাউটার এবং উপসর্গ

```python filename="main.py"
from fastapi import APIRouter

admin = APIRouter(prefix="/admin")


@admin.get("/stats")
async def stats():
    return {"users": 3}


app.include_router(admin)
```

ফোল্ডারটি উপসর্গ, এবং এতে অন্তর্ভুক্ত করার কিছু নেই:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## রুটের একটি গ্রুপের উপর নির্ভরতা

```python filename="main.py"
from fastapi import Depends, Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
```

ফোল্ডারে একটি `dependencies.py` নিচের প্রতিটি রুটের আগে চলে:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

একজন হ্যান্ডলারের জন্য একটি নির্ভরতা এখনও রয়েছে `Depends`, তার স্বাক্ষরে:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header


def current_user(authorization: str = Header(...)) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## মিডলওয়্যার

```python filename="main.py"
from fastapi import Request


@app.middleware("http")
async def add_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

একটি `middleware.py` তার ফোল্ডারের রুটগুলিকে মোড়ানো করে, রুটটি সেগুলিকে মুড়ে দেয়:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## CORS, GZip এবং অন্যান্য অ্যাপ-ওয়াইড মিডলওয়্যার

```python filename="main.py"
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["https://example.com"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

প্রতিটি একটি `nexyconfig.py` এর একটি ক্ষেত্র, একই যুক্তি সহ:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## এইচটিএমএল পেজ

```python filename="main.py"
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


@app.get("/users")
async def users_page(request: Request):
    users = [{"name": "Ada"}, {"name": "Alan"}]
    return templates.TemplateResponse(request, "users.html", {"users": users})
```

একটি `.nexy` পৃষ্ঠা একটি ফাইলে `---` লাইনের উপরে Python এবং এটির নীচে Jinja2 ধরে রাখে:

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

## টেমপ্লেট উত্তরাধিকার

```html filename="templates/base.html"
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

একটি `layout.nexy` তার ফোল্ডারের প্রতিটি পৃষ্ঠা মুড়ে দেয়, পৃষ্ঠাগুলিতে `{% extends %}` নেই:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## স্ট্যাটিক ফাইল

```python filename="main.py"
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

`public/` ফাইলগুলি রুট থেকে পরিবেশন করা হয়: `public/robots.txt` হল `/robots.txt`।

```text
public/
├─ robots.txt     /robots.txt
└─ logo.png       /logo.png
```

## পাওয়া যায়নি পাতা

```python filename="main.py"
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def not_found(request: Request, exc: StarletteHTTPException):
    return HTMLResponse("<h1>Not found</h1>", status_code=exc.status_code)
```

একটি `notfound.nexy` ব্রাউজারগুলির উত্তর দেয় এবং API ক্লায়েন্টরা এখনও `{"detail": ...}` পায়:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## ওয়েবসকেট

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

## টেস্ট

```python filename="tests/test_main.py"
from fastapi.testclient import TestClient

from main import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

ক্লায়েন্ট একই; অ্যাপটি Nexy থেকে আসে:

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## চলছে

| FastAPI | নেক্সি |
|---|---|
| `uvicorn main:app --reload` | `nx dev` |
| `uvicorn main:app --workers 4` | `nx build`, তারপর `nx start` |
| `/docs` `FastAPI()` থেকে | `/docs`, প্রতিটি `.py` রুটের তালিকা করা |

## একটি বিদ্যমান অ্যাপ রাখা

আপনি একবারে প্রতিটি রুট সরাতে হবে না. একটি `APIRouter` আপনার কাছে ইতিমধ্যেই মাউন্ট রয়েছে যেমনটি:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

আপনার পুরানো রুট এবং `src/routes/` এর ফাইলগুলি তারপর পাশাপাশি উত্তর দিন। `useRouter` সেট করার সময়, `.nexy` পৃষ্ঠাগুলি `layout.nexy` দ্বারা মোড়ানো হয় না: প্রথমে API সরান, তারপর পৃষ্ঠাগুলি, তারপর ক্ষেত্রটি সরান৷ [কাস্টম রাউটার ইন্টিগ্রেশন](../routing/custom/README.md) দেখুন।

## পরবর্তী পদক্ষেপ

- [রুট হ্যান্ডলার](../routing/fbr/handlers/README.md)
- [নির্ভরতা এবং প্রহরী](../routing/fbr/dependencies/README.md)
- [.nexy ফাইল](../views/nexy/README.md)
- [অন্য কাঠামো থেকে আসছে](../getting-started/coming-from-other-frameworks.md)
