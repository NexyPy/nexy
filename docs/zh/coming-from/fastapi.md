# 从 FastAPI 到 Nexy

Nexy 是 FastAPI，路线写为文件：在 `@app.get("/x")` 下回答的函数在 `src/routes/x.py` 中回答为 `GET`，其余代码保持不变。

## 什么留下，什么改变

Nexy serves your handlers with FastAPI itself, so everything inside a handler works unchanged:

| 保持不变 | 变化 |
|---|---|
| Pydantic 模型、请求机构和响应 | `@app.get("/x")` 变为 `src/routes/x.py` 和 `async def GET()` |
| `Depends`、`Query`、`Header`、`Cookie`、`Form`、`File` | 路径中的 `{id}` 变为 `[id].py` 文件或 `[id]/` 文件夹 |
| `HTTPException`、`status`、`JSONResponse`、`RedirectResponse` | `APIRouter(prefix="/users")` 成为文件夹 `users/` |
| `Request`、`BackgroundTasks`、`UploadFile`、WebSocket | 路由器上的 `dependencies=[...]` 变成 `dependencies.py` 文件 |
| 中间件类，`/docs`，`TestClient` | `app.add_middleware(...)` 成为 `nexyconfig.py` 的字段：`useCORS`、`useGZip`、`useMiddlewares` |

像以前一样从 `fastapi` 导入它们，或者从 `nexy.http` 导入它们，这会重新导出相同的对象。

Each section below shows a FastAPI habit, then the same thing in Nexy.

## 一个端点

FastAPI 使用装饰器在应用程序上注册一个函数：

```python filename="主要.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/hello")
async def hello():
    return {"message": "Hello"}
```

Nexy 从文件路径读取 URL，从函数名读取方法：

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## 路径和查询参数

```python filename="主要.py"
@app.get("/api/users/{id}")
async def get_user(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

The path parameter becomes a `[id]` segment of the file name.查询参数不动：

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` 回答 `404`，因为 `abc` 不是 `int`。

## 请求体

```python filename="主要.py"
from pydantic import BaseModel


class NewItem(BaseModel):
    name: str
    price: float


@app.post("/api/items", status_code=201)
async def create_item(item: NewItem):
    return item
```

Pydantic 模型是相同的。状态代码移至响应中：

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

与模型不匹配的主体会回答 `422`，如 FastAPI。

## 一个 URL 上有多种方法

```python filename="主要.py"
@app.get("/api/notes/{id}")
async def read_note(id: int): ...


@app.delete("/api/notes/{id}")
async def delete_note(id: int): ...
```

一个文件包含 URL 的每一种方法：

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## 路由器和前缀

```python filename="主要.py"
from fastapi import APIRouter

admin = APIRouter(prefix="/admin")


@admin.get("/stats")
async def stats():
    return {"users": 3}


app.include_router(admin)
```

文件夹是前缀，没有什么可包含的：

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## 对一组路由的依赖

```python filename="主要.py"
from fastapi import Depends, Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
```

文件夹中的 `dependencies.py` 在其下面的每个路由之前运行：

```python filename="src/routes/admin/dependency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

一个处理程序的依赖项仍然是 `Depends`，在其签名中：

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header


def current_user(authorization: str = Header(...)) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## 中间件

```python filename="主要.py"
from fastapi import Request


@app.middleware("http")
async def add_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

`middleware.py` 包装其文件夹的路由，根文件夹包装所有路由：

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## CORS、GZip 和其他应用程序范围的中间件

```python filename="主要.py"
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["https://example.com"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

每个都是 `nexyconfig.py` 的一个字段，具有相同的参数：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## HTML 页面

```python filename="主要.py"
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


@app.get("/users")
async def users_page(request: Request):
    users = [{"name": "Ada"}, {"name": "Alan"}]
    return templates.TemplateResponse(request, "users.html", {"users": users})
```

`.nexy` 页面将 `---` 行上方的 Python 及其下方的 Jinja2 保存在一个文件中：

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

## 模板继承

```html filename="模板/base.html"
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

`layout.nexy` 包裹其文件夹的每一页，页面中没有 `{% extends %}`：

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## 静态文件

```python filename="主要.py"
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

`public/` 中的文件从根目录提供：`public/robots.txt` 是 `/robots.txt`。

```text
public/
├─ robots.txt     /robots.txt
└─ logo.png       /logo.png
```

## 未找到页面

```python filename="主要.py"
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def not_found(request: Request, exc: StarletteHTTPException):
    return HTMLResponse("<h1>Not found</h1>", status_code=exc.status_code)
```

`notfound.nexy` 回答浏览器，API 客户端仍然得到 `{"detail": ...}`：

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## WebSockets

```python filename="主要.py"
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

## 测试

```python filename="测试/test_main.py"
from fastapi.testclient import TestClient

from main import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

客户是一样的；该应用程序来自 Nexy：

```python filename="测试/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## 跑步

| FastAPI | 内克西 |
|---|---|
| `uvicorn main:app --reload` | `nx dev` |
| `uvicorn main:app --workers 4` | `nx build`，然后 `nx start` |
| `/docs` 来自 `FastAPI()` | `/docs`，列出每条 `.py` 路线 |

## 保留现有应用程序

您不必一次移动每条路线。你已经拥有了一个 `APIRouter` 坐骑：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

然后你的旧路线和 `src/routes/` 的文件并排回答。设置 `useRouter` 时，`.nexy` 页面不会被 `layout.nexy` 包裹：首先移动 API，然后移动页面，然后删除该字段。请参阅[自定义路由器集成](../routing/custom/README.md)。

## 后续步骤

- [路由处理程序](../routing/fbr/handlers/README.md)
- [依赖项和守卫](../routing/fbr/dependencies/README.md)
- [.nexy 文件](../views/nexy/README.md)
- [来自另一个框架](../getting-started/coming-from-other-frameworks.md)
