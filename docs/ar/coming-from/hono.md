# من هونو إلى Nexy

في Nexy، يتحول مسار Hono إلى ملف Python ضمن `src/routes/`: يتحول `c.req` إلى معلمات مكتوبة، و `zValidator` إلى نموذج Pydantic، و `app.route` إلى مجلد، وعميل RPC `hc` إلى إجراءات مكتوبة.

يوضح كل قسم أدناه عادة Hono، ثم نفس الشيء في Nexy.

## طريق

```ts filename="src/index.ts"
import { Hono } from "hono";

const app = new Hono();

app.get("/api/hello", (c) => c.json({ message: "Hello" }));

export default app;
```

مسار الملف هو عنوان URL، واسم الوظيفة هو الطريقة، و `dict` الذي تم إرجاعه هو `c.json`:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `c.req.param` و `c.req.query`

```ts filename="src/index.ts"
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

`/api/users/abc` الإجابات `404`: `abc` ليس `int`.

## `zValidator`

```ts filename="src/index.ts"
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

## `app.route` و `basePath`

```ts filename="سرك/admin.ts"
export const admin = new Hono();

admin.get("/stats", (c) => c.json({ users: 3 }));
```

```ts filename="src/index.ts"
app.route("/admin", admin);
```

المجلد هو المسار الأساسي:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## الوسيطة على الطريق

```ts filename="src/index.ts"
import { createMiddleware } from "hono/factory";
import { HTTPException } from "hono/http-exception";

const requireAdmin = createMiddleware(async (c, next) => {
  if (c.req.header("x-role") !== "admin") throw new HTTPException(403, { message: "Admins only" });
  await next();
});

app.use("/admin/*", requireAdmin);
```

`/admin/*` هو المجلد: هناك `dependencies.py` يجري قبل كل طريق تحته.

```python filename="src/routes/admin/dependeency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## الوسيطة حول كل طلب

```ts filename="src/index.ts"
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

## `c.set` و `c.get`

```ts filename="src/index.ts"
app.use("/api/*", async (c, next) => {
  c.set("token", c.req.header("authorization")?.replace("Bearer ", ""));
  await next();
});

app.get("/api/whoami", (c) => c.json({ token: c.get("token") }));
```

القيمة المحسوبة للمعالج هي تبعية، تُسأل بالاسم:

```python filename="src/routes/api/whoami.py"
from nexy.http import Depends, Header


def token(authorization: str = Header("")) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(token: str = Depends(token)):
    return {"token": token}
```

## البرمجيات الوسيطة المضمنة

```ts filename="src/index.ts"
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

من مجموعات الرؤوس `secureHeaders`، يضيف `nx start` اثنين على حدة: `X-Content-Type-Options` و `Referrer-Policy`. اضبط الآخرين، مثل `Content-Security-Policy`، في `middleware.py`. انظر [الأمان](../reference/security.md).

## `c.html` وهونو JSX

```tsx filename="src/index.tsx"
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

تعرض صفحة `.nexy` HTML على الخادم من Python و Jinja2:

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

تظل JSX التفاعلية JSX: يتم عرض المكون React أو Preact أو Solid كجزيرة من الصفحة. انظر [الجزر](../rendering/islands.md).

## `c.redirect`

```ts filename="src/index.ts"
app.get("/old", (c) => c.redirect("/new", 301));
```

```python filename="src/routes/old.py"
from nexy.http import RedirectResponse


async def GET():
    return RedirectResponse("/new", status_code=301)
```

## ملفات تعريف الارتباط

```ts filename="src/index.ts"
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

## `HTTPException`، `notFound` و `onError`

```ts filename="src/index.ts"
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

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

## `serveStatic`

```ts filename="src/index.ts"
import { serveStatic } from "hono/bun";

app.use("/*", serveStatic({ root: "./public" }));
```

لا يوجد شيء للكتابة: `public/` يتم تقديمه في `/`.

## WebSockets

```ts filename="src/index.ts"
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

## عميل `hc` RPC

```ts filename="src/index.ts"
const routes = app.post("/todos", zValidator("json", z.object({ title: z.string() })), (c) =>
  c.json({ title: c.req.valid("json").title, done: false }),
);

export type AppType = typeof routes;
```

```ts filename="client.ts"
import { hc } from "hono/client";
import type { AppType } from "./src/index";

const client = hc<AppType>("http://localhost:3000");
const todo = await (await client.todos.$post({ json: { title: "Write the docs" } })).json();
```

الإجراء هو وظيفة الخادم والعميل المكتوب في واحد. يقوم Nexy بكتابة الأنواع TypeScript من التوقيع Python:

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
  const { run, data } = useAction(add_todo);
  return <button onClick={() => run({ title: "Write the docs" })}>{data?.title ?? "Add"}</button>;
}
```

## الاختبارات مع `app.request`

```ts filename="src/index.test.ts"
test("says hello", async () => {
  const res = await app.request("/api/hello");
  expect(await res.json()).toEqual({ message: "Hello" });
});
```

```python filename="الاختبارات/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## الجري

| هونو | نكسي |
|---|---|
| `npm create hono@latest` | `nx new` |
| `bun run --hot src/index.ts` أو `wrangler dev` | `nx dev` |
| `wrangler deploy` (العمال) | `nx build`، ثم `nx start` على خادم أو حاوية |
| `bun test` / `vitest` | `nx test` |

يعمل Nexy على خادم Python، وليس على وقت تشغيل الحافة: راجع [نشر ](../deployment/README.md).

## الخطوات التالية

- [من إكسبريس إلى نيكسي](express.md)
- [من إليسيا إلى نكسي](elysia.md)
- [الإجراءات](../guides/actions.md)
- [معالجات الطريق](../routing/fbr/handlers/README.md)
