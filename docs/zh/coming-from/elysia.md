# 从艾丽西亚到内克西

在 Nexy 中，Elysia 路由变为 `src/routes/` 下的 Python 文件：`t.Object` 模式变为 Pydantic 模型，`.group` 变为文件夹，`beforeHandle` 变为 `dependencies.py`，Eden 的类型化客户端变为类型化操作。

下面的每个部分都显示了 Elysia 习惯，然后是 Nexy 中的相同内容。

## 一条路线

```ts filename="src/index.ts"
import { Elysia } from "elysia";

new Elysia().get("/api/hello", () => ({ message: "Hello" })).listen(3000);
```

文件路径是 URL，函数名是方法：

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## 参数和查询 `t`

```ts filename="src/index.ts"
import { Elysia, t } from "elysia";

new Elysia().get("/api/users/:id", ({ params, query }) => ({ id: params.id, fields: query.fields }), {
  params: t.Object({ id: t.Numeric() }),
  query: t.Object({ fields: t.Optional(t.String()) }),
});
```

类型位于参数上，`:id` 是 `[id]` 段：

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## 具有 `t.Object` 的主体

```ts filename="src/index.ts"
app.post("/api/items", ({ body, set }) => {
  set.status = 201;
  return body;
}, {
  body: t.Object({ name: t.String(), price: t.Number({ exclusiveMinimum: 0 }) }),
});
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

## `response` 模式

```ts filename="src/index.ts"
app.get("/api/me", () => ({ name: "Ada" }), {
  response: t.Object({ name: t.String() }),
});
```

返回类型是响应模式：未声明的字段将被排除在答案之外。

```python filename="src/routes/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## `.group`

```ts filename="src/index.ts"
app.group("/admin", (admin) => admin.get("/stats", () => ({ users: 3 })));
```

该文件夹是组：

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `beforeHandle` 和 `guard`

```ts filename="src/index.ts"
app.group("/admin", (admin) =>
  admin
    .guard({
      beforeHandle({ headers, error }) {
        if (headers["x-role"] !== "admin") return error(403, "Admins only");
      },
    })
    .get("/stats", () => ({ users: 3 })),
);
```

`dependencies.py` 保护其文件夹的每一条路径：

```python filename="src/routes/admin/dependency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `derive`、`decorate` 和 `state`

```ts filename="src/index.ts"
app
  .derive(({ headers }) => ({ token: headers.authorization?.replace("Bearer ", "") }))
  .get("/api/whoami", ({ token }) => ({ token }));
```

`derive` 添加到上下文的是处理程序要求的依赖项：

```python filename="src/routes/api/whoami.py"
from nexy.http import Depends, Header


def token(authorization: str = Header("")) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(token: str = Depends(token)):
    return {"token": token}
```

`decorate` 和 `state` 是普通的模块级对象，在需要的地方导入。

## `onAfterHandle` 和 `mapResponse`

```ts filename="src/index.ts"
app.onAfterHandle(({ set }) => {
  set.headers["x-app"] = "demo";
});
```

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `error()` 和 `onError`

```ts filename="src/index.ts"
app.get("/api/orders/:id", ({ params, error }) => {
  if (Number(params.id) > 100) return error(404, "No such order");
  return { id: params.id };
});
```

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id}
```

路由根目录中的 `notfound.nexy` 会应答未知 URL 上的浏览器。

## 饼干

```ts filename="src/index.ts"
app.get("/api/theme", ({ cookie: { theme } }) => ({ theme: theme.value ?? "light" }));
```

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## 伊甸条约

```ts filename="src/index.ts"
const app = new Elysia().post("/todos", ({ body }) => ({ title: body.title, done: false }), {
  body: t.Object({ title: t.String() }),
});

export type App = typeof app;
```

```ts filename="客户端.ts"
import { treaty } from "@elysiajs/eden";
import type { App } from "./src/index";

const api = treaty<App>("localhost:3000");
const { data } = await api.todos.post({ title: "Write the docs" });
```

操作是 Python 函数及其类型化客户端。 Nexy 从 Python 签名生成 TypeScript 类型：

```python filename="src/actions/todos.py"
from pydantic import BaseModel

from nexy.decorators import Action


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    return Todo(title=title)
```

```tsx filename="src/components/AddTodo.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export function AddTodo() {
  const { run, pending, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```

请参阅[操作](../guides/actions.md)。

## 插件：`cors`、`swagger`、`static`

```ts filename="src/index.ts"
import { cors } from "@elysiajs/cors";
import { staticPlugin } from "@elysiajs/static";
import { swagger } from "@elysiajs/swagger";

app.use(cors({ origin: "https://example.com" })).use(swagger()).use(staticPlugin());
```

| 艾丽西亚插件 | 内克西 |
|---|---|
| `@elysiajs/cors` | `useCORS = {"allow_origins": [...]}` 在 `nexyconfig.py` |
| `@elysiajs/swagger` | 什么都没有： `/docs` 默认打开 |
| `@elysiajs/static` | 什么都没有： `public/` 在 `/` 供应 |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## WebSockets

```ts filename="src/index.ts"
app.ws("/ws/echo", {
  message(ws, message) {
    ws.send(message);
  },
});
```

```python filename="src/routes/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## 使用 `app.handle` 进行测试

```ts filename="测试/index.test.ts"
import { describe, expect, it } from "bun:test";

it("says hello", async () => {
  const response = await app.handle(new Request("http://localhost/api/hello"));
  expect(await response.json()).toEqual({ message: "Hello" });
});
```

```python filename="测试/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## 跑步

| 艾丽西亚 | 内克西 |
|---|---|
| `bun create elysia app` | `nx new` |
| `bun dev` | `nx dev` |
| `bun build --compile` | `nx build`，然后 `nx start` |
| `bun test` | `nx test` |

Nexy 在 Python 上运行。仅当项目具有客户端组件时才需要节点：Vite 构建它们，`nx start` 无需它即可运行。

## 后续步骤

- [从 Express 到 Nexy](express.md)
- [从 Fastify 到 Nexy](fastify.md)
- [行动](../guides/actions.md)
- [路由处理程序](../routing/fbr/handlers/README.md)
