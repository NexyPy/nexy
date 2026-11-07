# হোনো থেকে নেক্সি পর্যন্ত

Nexy-এ একটি Hono রুট `src/routes/` এর অধীনে একটি Python ফাইল হয়ে যায়: `c.req` টাইপ করা প্যারামিটারে পরিণত হয়, `zValidator` একটি Pydantic মডেলে, `app.route` একটি ফোল্ডারে পরিণত হয় এবং `hc` RPC ক্লায়েন্ট টাইপ করা অ্যাকশনে পরিণত হয়।

নীচের প্রতিটি বিভাগ একটি Hono অভ্যাস দেখায়, তারপর Nexy একই জিনিস.

## একটি রুট

```ts filename="src/index.ts"
import { Hono } from "hono";

const app = new Hono();

app.get("/api/hello", (c) => c.json({ message: "Hello" }));

export default app;
```

ফাইলের পাথ হল URL, ফাংশনের নাম হল পদ্ধতি, এবং একটি ফেরত `dict` হল `c.json`:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `c.req.param` এবং `c.req.query`

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

`/api/users/abc` উত্তর দেয় `404`: `abc` একটি `int` নয়।

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

## `app.route` এবং `basePath`

```ts filename="src/admin.ts"
export const admin = new Hono();

admin.get("/stats", (c) => c.json({ users: 3 }));
```

```ts filename="src/index.ts"
app.route("/admin", admin);
```

ফোল্ডারটি বেস পাথ:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## একটি পথে মিডলওয়্যার

```ts filename="src/index.ts"
import { createMiddleware } from "hono/factory";
import { HTTPException } from "hono/http-exception";

const requireAdmin = createMiddleware(async (c, next) => {
  if (c.req.header("x-role") !== "admin") throw new HTTPException(403, { message: "Admins only" });
  await next();
});

app.use("/admin/*", requireAdmin);
```

`/admin/*` হল ফোল্ডার: একটি `dependencies.py` এর নিচের প্রতিটি রুটের আগে চলে।

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## প্রতিটি অনুরোধের চারপাশে মিডলওয়্যার

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

## `c.set` এবং `c.get`

```ts filename="src/index.ts"
app.use("/api/*", async (c, next) => {
  c.set("token", c.req.header("authorization")?.replace("Bearer ", ""));
  await next();
});

app.get("/api/whoami", (c) => c.json({ token: c.get("token") }));
```

হ্যান্ডলারের জন্য গণনা করা মান হল একটি নির্ভরতা, নাম দ্বারা চাওয়া হয়েছে:

```python filename="src/routes/api/whoami.py"
from nexy.http import Depends, Header


def token(authorization: str = Header("")) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(token: str = Depends(token)):
    return {"token": token}
```

## অন্তর্নির্মিত মিডলওয়্যার

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

হেডার `secureHeaders` সেটগুলির মধ্যে, `nx start` তার নিজের থেকে দুটি যোগ করে: `X-Content-Type-Options` এবং `Referrer-Policy`। অন্যগুলিকে সেট করুন, যেমন একটি `Content-Security-Policy`, একটি `middleware.py` এ। দেখুন [নিরাপত্তা](../reference/security.md)।

## `c.html` এবং Hono JSX

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

একটি `.nexy` পৃষ্ঠা Python এবং Jinja2 থেকে সার্ভারে HTML রেন্ডার করে:

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

ইন্টারেক্টিভ জেএসএক্স জেএসএক্স থাকে: একটি React, Preact বা Solid উপাদান পৃষ্ঠার একটি দ্বীপ হিসাবে রেন্ডার করে। [দ্বীপগুলি](../rendering/islands.md) দেখুন।

## `c.redirect`

```ts filename="src/index.ts"
app.get("/old", (c) => c.redirect("/new", 301));
```

```python filename="src/routes/old.py"
from nexy.http import RedirectResponse


async def GET():
    return RedirectResponse("/new", status_code=301)
```

## কুকিজ

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

## `HTTPException`, `notFound` এবং `onError`

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

লেখার কিছু নেই: `public/` `/` এ পরিবেশিত হয়।

## ওয়েবসকেট

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

## `hc` RPC ক্লায়েন্ট

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

একটি অ্যাকশন হল সার্ভার ফাংশন এবং একটিতে টাইপ করা ক্লায়েন্ট। নেক্সি Python স্বাক্ষর থেকে TypeScript প্রকারগুলি লিখেছেন:

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

## সঙ্গে পরীক্ষা `app.request`

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

## চলছে

| হোনো | নেক্সি |
|---|---|
| `npm create hono@latest` | `nx new` |
| `bun run --hot src/index.ts` বা `wrangler dev` | `nx dev` |
| `wrangler deploy` (শ্রমিক) | `nx build`, তারপর `nx start` একটি সার্ভার বা একটি পাত্রে |
| `bun test` / `vitest` | `nx test` |

Nexy একটি Python সার্ভারে চলে, এজ রানটাইমে নয়: [ডিপ্লয়](../deployment/README.md) দেখুন।

## পরবর্তী পদক্ষেপ

- [এক্সপ্রেস থেকে নেক্সি ](express.md)
- [এলিসিয়া থেকে নেক্সি পর্যন্ত ](elysia.md)
- [কর্ম](../guides/actions.md)
- [রুট হ্যান্ডলার ](../routing/fbr/handlers/README.md)
