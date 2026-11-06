# 从 Express 到 Nexy

在 Nexy 中，Express 路由变成 `src/routes/` 下的 Python 文件：`app.get` 是 `GET` 函数，`req` 变成类型参数，`res.json` 变成返回值，`app.use` 变成配置字段或 `middleware.py`。

下面的每个部分都显示了 Express 习惯，然后是 Nexy 中的相同内容。

## 一条路线

```js filename="索引.js"
import express from "express";

const app = express();

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello" });
});

app.listen(3000);
```

文件路径是 URL，函数名称是方法，返回值是 JSON 正文：

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `req.params`

```js filename="索引.js"
app.get("/api/users/:id", (req, res) => {
  const id = Number(req.params.id);
  if (Number.isNaN(id)) return res.status(404).end();
  res.json({ id });
});
```

`:id` 是一个 `[id]` 段，类型注释进行转换，`404`：

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

`*` 通配符是 `[...rest].py` 文件。

## `req.query`

```js filename="索引.js"
app.get("/api/search", (req, res) => {
  const q = req.query.q ?? "";
  const page = Number(req.query.page ?? 1);
  res.json({ q, page });
});
```

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

`?page=abc` 使用失败的参数回答 `422`，而不是 `NaN`。

## `req.body` 和验证

```js filename="索引.js"
import { z } from "zod";

app.use(express.json());

const NewItem = z.object({ name: z.string(), price: z.number().positive() });

app.post("/api/items", (req, res) => {
  const parsed = NewItem.safeParse(req.body);
  if (!parsed.success) return res.status(422).json(parsed.error);
  res.status(201).json(parsed.data);
});
```

在函数运行之前，根据 Pydantic 模型对主体进行解析和验证：

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## `express.Router()`

```js filename="路线/admin.js"
const admin = express.Router();

admin.get("/stats", (req, res) => res.json({ users: 3 }));

app.use("/admin", admin);
```

该文件夹是挂载路径：

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## 路由中间件

```js filename="路线/admin.js"
function requireAdmin(req, res, next) {
  if (req.get("x-role") !== "admin") return res.status(403).json({ error: "Admins only" });
  next();
}

admin.use(requireAdmin);
```

`dependencies.py` 在其文件夹的每个路由之前运行。引发会停止请求，就像不调用 `next()` 一样：

```python filename="src/routes/admin/dependency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `app.use` 中间件

```js filename="索引.js"
app.use((req, res, next) => {
  const start = Date.now();
  res.on("finish", () => console.log(req.method, req.url, Date.now() - start));
  next();
});
```

路由根部的 `middleware.py` 包装每个请求； `call_next` 是 `next()`：

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## `cors`、`compression`、`helmet` 型主机

```js filename="索引.js"
import compression from "compression";
import cors from "cors";

app.use(cors({ origin: "https://example.com" }));
app.use(compression());
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
    useTrustedHost = {"allowed_hosts": ["example.com", "*.example.com"]}
    useSession = {"secret_key": "change-me"}
```

## 饼干

```js filename="索引.js"
import cookieParser from "cookie-parser";

app.use(cookieParser());

app.post("/api/theme", (req, res) => {
  res.cookie("theme", "dark").json({ theme: "dark" });
});

app.get("/api/theme", (req, res) => res.json({ theme: req.cookies.theme ?? "light" }));
```

cookie是读取的参数，写入响应的方法：

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie, JSONResponse


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}


async def POST():
    response = JSONResponse({"theme": "dark"})
    response.set_cookie("theme", "dark")
    return response
```

## `express-session`

```js filename="索引.js"
import session from "express-session";

app.use(session({ secret: "change-me" }));

app.post("/api/login", (req, res) => {
  req.session.user = req.body.name;
  res.json({ user: req.session.user });
});
```

`nexyconfig.py`（上面）中的 `useSession` 打开会话； `request.session` 是一个字典：

```python filename="src/routes/api/login.py"
from pydantic import BaseModel

from nexy.http import Request


class Login(BaseModel):
    name: str


async def POST(request: Request, body: Login):
    request.session["user"] = body.name
    return {"user": body.name}
```

## `res.redirect`

```js filename="索引.js"
app.get("/old", (req, res) => res.redirect(301, "/new"));
```

```python filename="src/routes/old.py"
from nexy.http import RedirectResponse


async def GET():
    return RedirectResponse("/new", status_code=301)
```

## 使用 `multer` 上传文件

```js filename="索引.js"
import multer from "multer";

const upload = multer({ limits: { fileSize: 1_000_000 } });

app.post("/api/upload", upload.single("file"), (req, res) => {
  res.json({ name: req.file.originalname, size: req.file.size });
});
```

```python filename="src/routes/api/upload.py"
from nexy.http import HTTPException, UploadFile


async def POST(file: UploadFile):
    data = await file.read()
    if len(data) > 1_000_000:
        raise HTTPException(status_code=413, detail="File too large")
    return {"name": file.filename, "size": len(data)}
```

## 使用 EJS 或 Pug 的视图

```js filename="索引.js"
app.set("view engine", "ejs");

app.get("/users", (req, res) => {
  res.render("users", { users: [{ name: "Ada" }, { name: "Alan" }] });
});
```

```html filename="视图/users.ejs"
<ul>
  <% users.forEach((user) => { %>
  <li><%= user.name %></li>
  <% }) %>
</ul>
```

`.nexy` 页面同时包含路线和视图：

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

`<%= %>` 转义，而 `{{ }}` 不转义：转义访问者用 `{{ value | e }}` 键入的内容。

## `express.static`

```js filename="索引.js"
app.use(express.static("public"));
```

没什么可写的：`public/` 的服务地点是 `/`。

## 404 处理程序和错误处理程序

```js filename="索引.js"
app.use((req, res) => res.status(404).send("<h1>Not found</h1>"));

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send("<h1>Something broke</h1>");
});
```

路由根目录下有两个文件。 API 客户端仍然获取 JSON，浏览器获取页面：

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

```nexy filename="src/routes/errors.nexy"
<h1>Something broke</h1>
```

## WebSockets 与 `ws`

```js filename="索引.js"
import { WebSocketServer } from "ws";

const wss = new WebSocketServer({ server, path: "/ws/echo" });
wss.on("connection", (socket) => socket.on("message", (data) => socket.send(data)));
```

```python filename="src/routes/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## 使用 Jest 和 Supertest 进行测试

```js filename="索引.test.js"
import request from "supertest";
import { app } from "./app.js";

test("hello", async () => {
  const res = await request(app).get("/api/hello");
  expect(res.body).toEqual({ message: "Hello" });
});
```

```python filename="测试/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## 跑步

| 快递 | 内克西 |
|---|---|
| `npm init` + `npm i express` | `nx new` |
| `nodemon index.js` | `nx dev` |
| `NODE_ENV=production node index.js` | `nx build`，然后 `nx start` |
| `npm test` | `nx test` |
| 没有 API 文档 | `/docs`，列出每条 `.py` 路线 |

## 保留您的 React 前端

如果 Express 应用程序提供 React SPA，则组件将移动到 `src/components/` 并呈现为 `.nexy` 页面的岛屿，或者整个站点移动到使用 `useCSR = True` 的客户端路由。参见[岛屿](../rendering/islands.md) 和[CSR](../rendering/csr.md)。

## 后续步骤

- [来自另一个框架](../getting-started/coming-from-other-frameworks.md)
- [路由处理程序](../routing/fbr/handlers/README.md)
- [中间件文件](../routing/fbr/middleware/README.md)
- [食谱](../guides/recipes.md)
