# 从 Fastify 到 Nexy

在 Nexy 中，Fastify 路由变成 `src/routes/` 下的 Python 文件：JSON 模式变成 Pydantic 模型，带有 `prefix` 的插件变成文件夹，挂钩变成 `dependencies.py` 和 `middleware.py` 文件。

下面的每个部分都显示了 Fastify 习惯，然后是 Nexy 中的相同内容。

## 一条路线

```js filename="服务器.js"
import Fastify from "fastify";

const app = Fastify({ logger: true });

app.get("/api/hello", async () => ({ message: "Hello" }));

await app.listen({ port: 3000 });
```

文件路径是 URL，函数名是方法：

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

每个请求都会记录其方法、路径、状态和时间，无需设置记录器。

## 参数和查询字符串模式

```js filename="服务器.js"
app.get(
  "/api/users/:id",
  {
    schema: {
      params: { type: "object", properties: { id: { type: "integer" } } },
      querystring: { type: "object", properties: { fields: { type: "string" } } },
    },
  },
  async (request) => ({ id: request.params.id, fields: request.query.fields }),
);
```

架构是签名：文件名中的 `[id]`，输入参数：

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## 身体图式

```js filename="服务器.js"
app.post(
  "/api/items",
  {
    schema: {
      body: {
        type: "object",
        required: ["name", "price"],
        properties: { name: { type: "string" }, price: { type: "number", exclusiveMinimum: 0 } },
      },
    },
  },
  async (request, reply) => reply.code(201).send(request.body),
);
```

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

失败的主体会回答 `422`，而 Fastify 会回答 `400`。

## 响应模式

```js filename="服务器.js"
app.get(
  "/api/me",
  {
    schema: {
      response: {
        200: { type: "object", properties: { name: { type: "string" } } },
      },
    },
  },
  async () => ({ name: "Ada", passwordHash: "x" }),
);
```

返回类型的作用与响应模式的作用相同：未声明的字段将被忽略。

```python filename="src/routes/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## 带前缀的插件

```js filename="路线/admin.js"
export default async function admin(app) {
  app.get("/stats", async () => ({ users: 3 }));
}
```

```js filename="服务器.js"
app.register(admin, { prefix: "/admin" });
```

该文件夹是前缀，没有注册任何内容：

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `preHandler` 和 `onRequest` 钩子

```js filename="路线/admin.js"
export default async function admin(app) {
  app.addHook("preHandler", async (request, reply) => {
    if (request.headers["x-role"] !== "admin") {
      return reply.code(403).send({ error: "Admins only" });
    }
  });
}
```

作用于插件的钩子是其文件夹中的 `dependencies.py`：

```python filename="src/routes/admin/dependency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `onSend` 和 `onResponse` 钩子

```js filename="服务器.js"
app.addHook("onSend", async (request, reply, payload) => {
  reply.header("x-app", "demo");
  return payload;
});
```

`middleware.py` 中 `call_next` 之后的代码在退出时运行：

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `decorate` 和 `decorateRequest`

```js filename="服务器.js"
app.decorate("db", { users: () => [{ name: "Ada" }] });

app.get("/api/users", async function () {
  return this.db.users();
});
```

共享对象是一个返回它的函数，处理程序通过 `Depends` 请求它：

```python filename="src/db.py"
class Db:
    def users(self) -> list[dict]:
        return [{"name": "Ada"}]


db = Db()


def get_db() -> Db:
    return db
```

```python filename="src/routes/api/users/index.py"
from nexy.http import Depends

from src.db import Db, get_db


async def GET(db: Db = Depends(get_db)):
    return db.users()
```

测试将其与 `app.dependency_overrides[get_db]` 交换。

## `@fastify/cors`，`@fastify/compress`，`@fastify/cookie`

```js filename="服务器.js"
await app.register(import("@fastify/cors"), { origin: "https://example.com" });
await app.register(import("@fastify/compress"));
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

cookie 不需要插件：使用 `Cookie` 参数读取它，使用 `response.set_cookie` 设置它。

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## `setErrorHandler` 和 `setNotFoundHandler`

```js filename="服务器.js"
app.setNotFoundHandler((request, reply) => reply.code(404).type("text/html").send("<h1>Not found</h1>"));
```

浏览器获取 `notfound.nexy`，API客户端 `{"detail": "Not Found"}`：

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

知道出了什么问题的处理程序会引发它：

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id}
```

## `@fastify/static`

```js filename="服务器.js"
await app.register(import("@fastify/static"), { root: path.join(__dirname, "public") });
```

没什么可写的：`public/` 的服务地点是 `/`。

## `@fastify/websocket`

```js filename="服务器.js"
await app.register(import("@fastify/websocket"));

app.get("/ws/echo", { websocket: true }, (socket) => {
  socket.on("message", (message) => socket.send(message));
});
```

```python filename="src/routes/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## `@fastify/swagger`

```js filename="服务器.js"
await app.register(import("@fastify/swagger"));
await app.register(import("@fastify/swagger-ui"), { routePrefix: "/docs" });
```

无需注册：OpenAPI 模式是根据类型注释构建的，并在 `/docs` 中提供服务。

## 使用 `inject` 进行测试

```js filename="服务器.test.js"
const response = await app.inject({ method: "GET", url: "/api/hello" });
expect(response.json()).toEqual({ message: "Hello" });
```

`TestClient` 也在内存中调用应用程序，但没有端口：

```python filename="测试/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## 跑步

| 快速化 | 内克西 |
|---|---|
| `npm init fastify` | `nx new` |
| `fastify start -w app.js` | `nx dev` |
| `node server.js` 正在生产中 | `nx build`，然后 `nx start` |
| `npm test` | `nx test` |

## 后续步骤

- [从 Express 到 Nexy](express.md)
- [路由处理程序](../routing/fbr/handlers/README.md)
- [验证和错误](../routing/fbr/handlers/validation-and-errors.md)
- [依赖项和守卫](../routing/fbr/dependencies/README.md)
