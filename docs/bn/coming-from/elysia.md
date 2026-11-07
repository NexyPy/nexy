# এলিসিয়া থেকে নেক্সি পর্যন্ত

নেক্সিতে একটি এলিসিয়া রুট `src/routes/` এর অধীনে একটি Python ফাইল হয়ে যায়: `t.Object` স্কিমাগুলি Pydantic মডেলে পরিণত হয়, `.group` একটি ফোল্ডারে পরিণত হয়, `beforeHandle` একটি `dependencies.py` এবং ইডেনের টাইপ করা ক্লায়েন্ট টাইপ করা অ্যাকশনে পরিণত হয়।

নীচের প্রতিটি বিভাগ একটি Elysia অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস।

## একটি রুট

```ts filename="src/index.ts"
import { Elysia } from "elysia";

new Elysia().get("/api/hello", () => ({ message: "Hello" })).listen(3000);
```

ফাইল পাথ হল URL, ফাংশনের নাম হল পদ্ধতি:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## পরম এবং প্রশ্ন সহ `t`

```ts filename="src/index.ts"
import { Elysia, t } from "elysia";

new Elysia().get("/api/users/:id", ({ params, query }) => ({ id: params.id, fields: query.fields }), {
  params: t.Object({ id: t.Numeric() }),
  query: t.Object({ fields: t.Optional(t.String()) }),
});
```

প্রকারগুলি পরামিতিগুলিতে যায় এবং `:id` একটি `[id]` সেগমেন্ট:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## একটি শরীর যার সাথে `t.Object`

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

## `response` স্কিমা

```ts filename="src/index.ts"
app.get("/api/me", () => ({ name: "Ada" }), {
  response: t.Object({ name: t.String() }),
});
```

রিটার্ন টাইপ হল রেসপন্স স্কিমা: অঘোষিত ক্ষেত্র উত্তরের বাইরে থাকে।

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

ফোল্ডারটি হল গ্রুপ:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `beforeHandle` এবং `guard`

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

একটি `dependencies.py` তার ফোল্ডারের প্রতিটি রুট রক্ষা করে:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `derive`, `decorate` এবং `state`

```ts filename="src/index.ts"
app
  .derive(({ headers }) => ({ token: headers.authorization?.replace("Bearer ", "") }))
  .get("/api/whoami", ({ token }) => ({ token }));
```

যা `derive` প্রসঙ্গে যোগ করে তা হল একটি নির্ভরতা, যা হ্যান্ডলার দ্বারা চাওয়া হয়েছে:

```python filename="src/routes/api/whoami.py"
from nexy.http import Depends, Header


def token(authorization: str = Header("")) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(token: str = Depends(token)):
    return {"token": token}
```

`decorate` এবং `state` হল প্লেইন মডিউল-স্তরের বস্তু, যেখানে তাদের প্রয়োজন সেখানে আমদানি করা হয়।

## `onAfterHandle` এবং `mapResponse`

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

## `error()` এবং `onError`

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

একটি `notfound.nexy` রুট রুট একটি অজানা URL এ ব্রাউজার উত্তর দেয়।

## কুকিজ

```ts filename="src/index.ts"
app.get("/api/theme", ({ cookie: { theme } }) => ({ theme: theme.value ?? "light" }));
```

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## ইডেন চুক্তি

```ts filename="src/index.ts"
const app = new Elysia().post("/todos", ({ body }) => ({ title: body.title, done: false }), {
  body: t.Object({ title: t.String() }),
});

export type App = typeof app;
```

```ts filename="client.ts"
import { treaty } from "@elysiajs/eden";
import type { App } from "./src/index";

const api = treaty<App>("localhost:3000");
const { data } = await api.todos.post({ title: "Write the docs" });
```

একটি অ্যাকশন হল Python ফাংশন এবং তার টাইপ করা ক্লায়েন্ট একবারে। নেক্সি Python স্বাক্ষর থেকে TypeScript প্রকারগুলি তৈরি করে:

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

দেখুন [কর্ম](../guides/actions.md)।

## প্লাগইন: `cors`, `swagger`, `static`

```ts filename="src/index.ts"
import { cors } from "@elysiajs/cors";
import { staticPlugin } from "@elysiajs/static";
import { swagger } from "@elysiajs/swagger";

app.use(cors({ origin: "https://example.com" })).use(swagger()).use(staticPlugin());
```

| এলিসিয়া প্লাগইন | নেক্সি |
|---|---|
| `@elysiajs/cors` | `useCORS = {"allow_origins": [...]}` `nexyconfig.py` মধ্যে |
| `@elysiajs/swagger` | কিছুই না: `/docs` ডিফল্টরূপে চালু থাকে |
| `@elysiajs/static` | কিছুই না: `public/` `/` এ পরিবেশিত হয় |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## ওয়েবসকেট

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

## সঙ্গে পরীক্ষা `app.handle`

```ts filename="test/index.test.ts"
import { describe, expect, it } from "bun:test";

it("says hello", async () => {
  const response = await app.handle(new Request("http://localhost/api/hello"));
  expect(await response.json()).toEqual({ message: "Hello" });
});
```

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## চলছে

| এলিসিয়া | নেক্সি |
|---|---|
| `bun create elysia app` | `nx new` |
| `bun dev` | `nx dev` |
| `bun build --compile` | `nx build`, তারপর `nx start` |
| `bun test` | `nx test` |

নেক্সি চলে Python। নোড শুধুমাত্র তখনই প্রয়োজন যখন প্রকল্পে ক্লায়েন্ট উপাদান থাকে: Vite সেগুলি তৈরি করে, এবং `nx start` এটি ছাড়াই চলে।

## পরবর্তী পদক্ষেপ

- [এক্সপ্রেস থেকে নেক্সি ](express.md)
- [ফাস্টফাই থেকে নেক্সি পর্যন্ত](fastify.md)
- [কর্ম](../guides/actions.md)
- [রুট হ্যান্ডলার ](../routing/fbr/handlers/README.md)
