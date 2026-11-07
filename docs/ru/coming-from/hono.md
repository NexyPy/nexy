# От Хоно до Некси

В Nexy маршрут Hono становится файлом Python в папке `src/routes/`: `c.req` превращается в типизированные параметры, `zValidator` в модель Pydantic, `app.route` в папку, а `hc` RPC-клиент в типизированные действия.

В каждом разделе ниже показаны привычки Hono, а затем то же самое в Nexy.

## Маршрут

```ts filename="источник/index.ts"
import { Hono } from "hono";

const app = new Hono();

app.get("/api/hello", (c) => c.json({ message: "Hello" }));

export default app;
```

Путь к файлу - это URL-адрес, имя функции - это метод, а возвращаемое значение `dict` - это `c.json`:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `c.req.param` и `c.req.query`

```ts filename="источник/index.ts"
app.get("/api/users/:id", (c) => {
  const id = Number(c.req.param("id"));
  const fields = c.req.query("fields");
  return c.json({ id, fields });
});
```

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` отвечает `404`: `abc` не является `int`.

## `zValidator`

```ts filename="источник/index.ts"
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";

const NewItem = z.object({ name: z.string(), price: z.number().positive() });

app.post("/api/items", zValidator("json", NewItem), (c) => c.json(c.req.valid("json"), 201));
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

## `app.route` и `basePath`

```ts filename="src/admin.ts"
export const admin = new Hono();

admin.get("/stats", (c) => c.json({ users: 3 }));
```

```ts filename="источник/index.ts"
app.route("/admin", admin);
```

Папка является базовым путем:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Промежуточное ПО на пути

```ts filename="источник/index.ts"
import { createMiddleware } from "hono/factory";
import { HTTPException } from "hono/http-exception";

const requireAdmin = createMiddleware(async (c, next) => {
  if (c.req.header("x-role") !== "admin") throw new HTTPException(403, { message: "Admins only" });
  await next();
});

app.use("/admin/*", requireAdmin);
```

`/admin/*` - это папка: `dependencies.py` там выполняется перед каждым маршрутом ниже нее.

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## Промежуточное ПО для каждого запроса

```ts filename="источник/index.ts"
app.use("*", async (c, next) => {
  await next();
  c.header("x-app", "demo");
});
```

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `c.set` и `c.get`

```ts filename="источник/index.ts"
app.use("/api/*", async (c, next) => {
  c.set("token", c.req.header("authorization")?.replace("Bearer ", ""));
  await next();
});

app.get("/api/whoami", (c) => c.json({ token: c.get("token") }));
```

Значение, вычисленное для обработчика, является зависимостью, запрашиваемой по имени:

```python filename="src/routes/api/whoami.py"
from nexy.http import Depends, Header


def token(authorization: str = Header("")) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(token: str = Depends(token)):
    return {"token": token}
```

## Встроенное промежуточное программное обеспечение

```ts filename="источник/index.ts"
import { compress } from "hono/compress";
import { cors } from "hono/cors";
import { secureHeaders } from "hono/secure-headers";

app.use("*", cors({ origin: "https://example.com" }), compress(), secureHeaders());
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

Из наборов заголовков `secureHeaders` `nx start` добавляет два самостоятельно: `X-Content-Type-Options` и `Referrer-Policy`. Остальные, например `Content-Security-Policy`, установите в `middleware.py`. См. [Безопасность](../reference/security.md).

## `c.html` и Хоно JSX

```tsx filename="источник/index.tsx"
app.get("/users", (c) => {
  const users = [{ name: "Ada" }, { name: "Alan" }];
  return c.html(
    <ul>
      {users.map((user) => (
        <li>{user.name}</li>
      ))}
    </ul>,
  );
});
```

Страница `.nexy` отображает HTML на сервере из Python и Jinja2:

```nexy filename="src/маршруты/users.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

Интерактивный JSX остается JSX: компонент React, Preact или Solid отображается как остров на странице. См. [Острова](../rendering/islands.md).

## `c.redirect`

```ts filename="источник/index.ts"
app.get("/old", (c) => c.redirect("/new", 301));
```

```python filename="src/маршруты/old.py"
from nexy.http import RedirectResponse


async def GET():
    return RedirectResponse("/new", status_code=301)
```

## Файлы cookie

```ts filename="источник/index.ts"
import { getCookie, setCookie } from "hono/cookie";

app.get("/api/theme", (c) => c.json({ theme: getCookie(c, "theme") ?? "light" }));
app.post("/api/theme", (c) => {
  setCookie(c, "theme", "dark");
  return c.json({ theme: "dark" });
});
```

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie, JSONResponse


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}


async def POST():
    response = JSONResponse({"theme": "dark"})
    response.set_cookie("theme", "dark")
    return response
```

## `HTTPException`, `notFound` и `onError`

```ts filename="источник/index.ts"
app.get("/api/orders/:id", (c) => {
  if (Number(c.req.param("id")) > 100) throw new HTTPException(404, { message: "No such order" });
  return c.json({ id: c.req.param("id") });
});

app.notFound((c) => c.html("<h1>Not found</h1>", 404));
```

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id}
```

```nexy filename="источник/маршруты/notfound.nexy"
<h1>Not found</h1>
```

## `serveStatic`

```ts filename="источник/index.ts"
import { serveStatic } from "hono/bun";

app.use("/*", serveStatic({ root: "./public" }));
```

Писать нечего: `public/` обслуживается в `/`.

## Вебсокеты

```ts filename="источник/index.ts"
import { upgradeWebSocket } from "hono/bun";

app.get(
  "/ws/echo",
  upgradeWebSocket(() => ({
    onMessage(event, ws) {
      ws.send(event.data);
    },
  })),
);
```

```python filename="src/routes/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## `hc` RPC-клиент

```ts filename="источник/index.ts"
const routes = app.post("/todos", zValidator("json", z.object({ title: z.string() })), (c) =>
  c.json({ title: c.req.valid("json").title, done: false }),
);

export type AppType = typeof routes;
```

```ts filename="клиент.ц"
import { hc } from "hono/client";
import type { AppType } from "./src/index";

const client = hc<AppType>("http://localhost:3000");
const todo = await (await client.todos.$post({ json: { title: "Write the docs" } })).json();
```

Действие - это функция сервера и типизированный клиент в одном лице. Nexy записывает типы TypeScript из сигнатуры Python:

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

```tsx filename="источник/компоненты/AddTodo.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export function AddTodo() {
  const { run, data } = useAction(add_todo);
  return <button onClick={() => run({ title: "Write the docs" })}>{data?.title ?? "Add"}</button>;
}
```

## Тесты с `app.request`

```ts filename="источник/index.test.ts"
test("says hello", async () => {
  const res = await app.request("/api/hello");
  expect(await res.json()).toEqual({ message: "Hello" });
});
```

```python filename="тесты/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Бег

| Хоно | Некси |
|---|---|
| `npm create hono@latest` | `nx new` |
| `bun run --hot src/index.ts` или `wrangler dev` | `nx dev` |
| `wrangler deploy` (Рабочие) | `nx build`, затем `nx start` на сервере или в контейнере |
| `bun test` / `vitest` | `nx test` |

Nexy работает на сервере Python, а не в периферийной среде выполнения: см. [Развертывание](../deployment/README.md).

## Следующие шаги

- [От Экспресса до Некси](express.md)
- [От Элизии до Некси](elysia.md)
- [Действия](../guides/actions.md)
- [Обработчики маршрутов](../routing/fbr/handlers/README.md)
