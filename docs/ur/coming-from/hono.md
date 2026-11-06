# Hono سے Nexy تک

Nexy میں ایک Hono روٹ `src/routes/` کے تحت ایک Python فائل بن جاتا ہے: `c.req` ٹائپ شدہ پیرامیٹرز میں، `zValidator` کو Pydantic ماڈل میں، `app.route` فولڈر میں، اور `hc` RPC کلائنٹ ٹائپ شدہ ایکشنز میں بدل جاتا ہے۔

ذیل میں ہر سیکشن Hono کی عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔

## ایک راستہ

```ts filename="src/index.ts"
import { Hono } from "hono";

const app = new Hono();

app.get("/api/hello", (c) => c.json({ message: "Hello" }));

export default app;
```

فائل کا راستہ یو آر ایل ہے، فنکشن کا نام طریقہ ہے، اور واپس کیا گیا `dict` ہے `c.json`:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `c.req.param` اور `c.req.query`

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

`/api/users/abc` جوابات `404`: `abc` ایک `int` نہیں ہے۔

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

## `app.route` اور `basePath`

```ts filename="src/admin.ts"
export const admin = new Hono();

admin.get("/stats", (c) => c.json({ users: 3 }));
```

```ts filename="src/index.ts"
app.route("/admin", admin);
```

فولڈر بنیادی راستہ ہے:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## ایک راستے پر مڈل ویئر

```ts filename="src/index.ts"
import { createMiddleware } from "hono/factory";
import { HTTPException } from "hono/http-exception";

const requireAdmin = createMiddleware(async (c, next) => {
  if (c.req.header("x-role") !== "admin") throw new HTTPException(403, { message: "Admins only" });
  await next();
});

app.use("/admin/*", requireAdmin);
```

`/admin/*` فولڈر ہے: ایک `dependencies.py` اس کے نیچے ہر راستے سے پہلے چلتا ہے۔

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## ہر درخواست کے ارد گرد مڈل ویئر

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

## `c.set` اور `c.get`

```ts filename="src/index.ts"
app.use("/api/*", async (c, next) => {
  c.set("token", c.req.header("authorization")?.replace("Bearer ", ""));
  await next();
});

app.get("/api/whoami", (c) => c.json({ token: c.get("token") }));
```

ہینڈلر کے لیے شمار کی جانے والی قدر ایک انحصار ہے، جو نام سے مانگی گئی ہے:

```python filename="src/routes/api/whoami.py"
from nexy.http import Depends, Header


def token(authorization: str = Header("")) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(token: str = Depends(token)):
    return {"token": token}
```

## بلٹ ان مڈل ویئر

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

ہیڈر `secureHeaders` سیٹوں میں سے، `nx start` اپنے طور پر دو کا اضافہ کرتا ہے: `X-Content-Type-Options` اور `Referrer-Policy`۔ دیگر سیٹ کریں، جیسے کہ `Content-Security-Policy`، ایک `middleware.py` میں۔ دیکھیں [سیکیورٹی](../reference/security.md)۔

## `c.html` اور ہونو جے ایس ایکس

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

ایک `.nexy` صفحہ سرور پر Python اور Jinja2 سے HTML پیش کرتا ہے:

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

انٹرایکٹو JSX JSX رہتا ہے: a React، Preact یا Solid جزو صفحہ کے جزیرے کے طور پر پیش کرتا ہے۔ دیکھیں [جزیرے](../rendering/islands.md)۔

## `c.redirect`

```ts filename="src/index.ts"
app.get("/old", (c) => c.redirect("/new", 301));
```

```python filename="src/routes/old.py"
from nexy.http import RedirectResponse


async def GET():
    return RedirectResponse("/new", status_code=301)
```

## کوکیز

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

## `HTTPException`، `notFound` اور `onError`

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

لکھنے کے لیے کچھ نہیں: `public/` `/` پر پیش کیا جاتا ہے۔

## ویب ساکٹس

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

## `hc` RPC کلائنٹ

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

ایک ایکشن سرور فنکشن ہے اور ایک میں ٹائپ کردہ کلائنٹ۔ Nexy سے TypeScript اقسام لکھتا ہے۔ Python دستخط:

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

## کے ساتھ ٹیسٹ `app.request`

```ts filename="src/index.test.ts"
test("says hello", async () => {
  const res = await app.request("/api/hello");
  expect(await res.json()).toEqual({ message: "Hello" });
});
```

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## چل رہا ہے۔

| ہونو | نیکسی |
|---|---|
| `npm create hono@latest` | `nx new` |
| `bun run --hot src/index.ts` یا `wrangler dev` | `nx dev` |
| `wrangler deploy` (مزدور) | `nx build`، پھر `nx start` سرور یا کنٹینر پر |
| `bun test` / `vitest` | `nx test` |

Nexy ایک Python سرور پر چلتا ہے، ایک کنارے کے رن ٹائم پر نہیں: دیکھیں [تعینات](../deployment/README.md)۔

## اگلے اقدامات

- [ایکسپریس سے Nexy تک](express.md)
- [Elysia سے Nexy تک](elysia.md)
- [اعمال](../guides/actions.md)
- [روٹ ہینڈلر](../routing/fbr/handlers/README.md)
