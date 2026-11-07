# 从 Flask 到 Nexy

在 Nexy 中，Flask 视图变成 `src/routes/` 下的文件：JSON 的 `.py` 文件，HTML 的 `.nexy` 文件，保留 Jinja2，装饰器、蓝图和 `request` 全局消失。

下面的每个部分都显示了一个 Flask 习惯，然后 Nexy 中也显示了相同的内容。

## 一条路线

```python filename="应用程序.py"
from flask import Flask

app = Flask(__name__)


@app.get("/api/hello")
def hello():
    return {"message": "Hello"}
```

文件路径是 URL，函数名称是方法：

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## 网址变量

```python filename="应用程序.py"
@app.get("/api/users/<int:id>")
def get_user(id):
    return {"id": id}
```

转换器成为类型注释，变量成为 `[id]` 段：

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` 是一个包罗万象的段，`[...rest].py`。

## 查询字符串

```python filename="应用程序.py"
from flask import request


@app.get("/api/search")
def search():
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    return {"q": q, "page": page}
```

没有 `request` 全局：查询参数是函数参数，经过转换和验证：

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## JSON 正文

```python filename="应用程序.py"
@app.post("/api/items")
def create_item():
    data = request.get_json()
    if "name" not in data:
        return {"error": "name is required"}, 400
    return {"created": data["name"]}, 201
```

一个 Pydantic 模型验证主体，而一个糟糕的模型则自行回答 `422`：

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## 一个 URL 上有多种方法

```python filename="应用程序.py"
@app.route("/api/notes/<int:id>", methods=["GET", "DELETE"])
def note(id):
    if request.method == "DELETE":
        return {"deleted": id}
    return {"id": id}
```

同一文件中每个方法一个函数：

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## 模板

```python filename="应用程序.py"
from flask import render_template


@app.get("/users")
def users():
    return render_template("users.html", users=[{"name": "Ada"}, {"name": "Alan"}])
```

视图及其模板是一个 `.nexy` 文件：`---` 行上方的 Python，下面的 Jinja2 相同：

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

## 基础模板

```html filename="模板/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

`layout.nexy` 包裹其文件夹及其下面的每一页；页面不 `{% extends %}` 它：

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## 宏和包含

```html filename="模板/宏.html"
{% macro card(title) %}
<article><h2>{{ title }}</h2>{{ caller() }}</article>
{% endmacro %}
```

组件是一个带有 props 的 `.nexy` 文件，在 frontmatter 中导入：

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
---
<article>
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>Everything published this week.</p>
</Card>
```

`@` 是 `src/`：`nx new` 在 `nexyconfig.py` 中写入 `useAliases = {"@": "src"}`。

## 蓝图

```python filename="管理员.py"
from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.get("/stats")
def stats():
    return {"users": 3}


app.register_blueprint(admin)
```

文件夹是前缀，没有注册任何内容：

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `before_request`

```python filename="管理员.py"
from flask import abort


@admin.before_request
def require_admin():
    if request.headers.get("X-Role") != "admin":
        abort(403)
```

`dependencies.py` 在其文件夹的每条路径之前运行：

```python filename="src/routes/admin/dependency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `after_request`

```python filename="应用程序.py"
@app.after_request
def add_header(response):
    response.headers["X-App"] = "demo"
    return response
```

`middleware.py` 在路由之前看到请求，在路由之后看到响应：

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## 表格和重定向

```python filename="应用程序.py"
from flask import redirect, url_for


@app.post("/notes")
def add_note():
    NOTES.append(request.form["title"])
    return redirect(url_for("notes"))
```

操作是表单发布到的 Python 函数。 Nexy 为其提供一个路径，读取表单字段作为其参数，并将访问者发送回带有 `303` 的页面：

```python filename="src/actions/notes.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/routes/notes.nexy"
---
from src.actions.notes import NOTES
---
<form method="post" action="{{ __actions_path['add_note'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
<ul>
  {% for note in NOTES %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

## 会议

```python filename="应用程序.py"
from flask import session

app.secret_key = "change-me"


@app.post("/api/login")
def login():
    session["user"] = request.json["name"]
    return {"user": session["user"]}
```

秘密移动到 `nexyconfig.py`，并且会话挂起请求：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

```python filename="src/routes/api/login.py"
from pydantic import BaseModel

from nexy.http import Request


class Login(BaseModel):
    name: str


async def POST(request: Request, body: Login):
    request.session["user"] = body.name
    return {"user": body.name}
```

页面用 `useSession()` 读取它：

```nexy filename="src/routes/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Hello {{ user }}</h1>
```

## `abort(404)` 和错误处理程序

```python filename="应用程序.py"
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.get("/posts/<slug>")
def post(slug):
    if slug not in POSTS:
        abort(404)
    return render_template("post.html", post=POSTS[slug])
```

`notFound()` 停止页面，`notfound.nexy` 绘制答案：

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## 静态文件

```text
static/logo.png        Flask:  /static/logo.png
public/logo.png        Nexy:   /logo.png
```

## Flask-CORS

```python filename="应用程序.py"
from flask_cors import CORS

CORS(app, origins=["https://example.com"])
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## 测试

```python filename="测试/test_app.py"
from app import app


def test_hello():
    assert app.test_client().get("/api/hello").json == {"message": "Hello"}
```

```python filename="测试/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## 跑步

| Flask | 内克西 |
|---|---|
| `flask run --debug` | `nx dev` |
| `gunicorn app:app` | `nx build`，然后 `nx start` |
| `flask db migrate`（烧瓶迁移） | `nx migrate -m "message"` |
| 没有 API 文档 | `/docs`，列出每条 `.py` 路线 |

## 后续步骤

- [从 FastAPI 到 Nexy](fastapi.md)：Nexy 处理程序是 FastAPI 处理程序
- [行动](../guides/actions.md)
- [.nexy 文件](../views/nexy/README.md)
- [Recipes](../guides/recipes.md)：登录、CRUD 和上传
