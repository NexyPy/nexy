# Elysia سے Nexy تک

Nexy میں ایک ایلیسیا روٹ `src/routes/` کے تحت ایک Python فائل بن جاتا ہے: `t.Object` اسکیماس Pydantic ماڈل بن جاتا ہے، `.group` ایک فولڈر بن جاتا ہے، `beforeHandle` ایک `dependencies.py`، اور ایڈن کا ٹائپ شدہ کلائنٹ ٹائپ شدہ ایکشن بن جاتا ہے۔

ذیل میں ہر سیکشن ایلیسیا کی عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔

## ایک راستہ

```ts filename="src/index.ts"
import { Elysia } from "elysia";

new Elysia().get("/api/hello", () => ({ message: "Hello" })).listen(3000);
```

فائل کا راستہ URL ہے، فنکشن کا نام طریقہ ہے:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## پیرامز اور استفسار کے ساتھ `t`

```ts filename="src/index.ts"
import { Elysia, t } from "elysia";

new Elysia().get("/api/users/:id", ({ params, query }) => ({ id: params.id, fields: query.fields }), {
  params: t.Object({ id: t.Numeric() }),
  query: t.Object({ fields: t.Optional(t.String()) }),
});
```

اقسام پیرامیٹرز پر چلتی ہیں، اور `:id` ایک `[id]` سیگمنٹ ہے:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## کے ساتھ ایک جسم `t.Object`

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

## `response` اسکیمے۔

```ts filename="src/index.ts"
app.get("/api/me", () => ({ name: "Ada" }), {
  response: t.Object({ name: t.String() }),
});
```

واپسی کی قسم جوابی اسکیما ہے: غیر اعلانیہ فیلڈز جواب سے باہر رہ گئے ہیں۔

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

فولڈر گروپ ہے:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `beforeHandle` اور `guard`

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

ایک `dependencies.py` اپنے فولڈر کے ہر راستے کی حفاظت کرتا ہے:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `derive`، `decorate` اور `state`

```ts filename="src/index.ts"
app
  .derive(({ headers }) => ({ token: headers.authorization?.replace("Bearer ", "") }))
  .get("/api/whoami", ({ token }) => ({ token }));
```

جو کچھ `derive` سیاق و سباق میں شامل کرتا ہے وہ ایک انحصار ہے، جو ہینڈلر کے ذریعہ طلب کیا گیا ہے:

```python filename="src/routes/api/whoami.py"
from nexy.http import Depends, Header


def token(authorization: str = Header("")) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(token: str = Depends(token)):
    return {"token": token}
```

`decorate` اور `state` سادہ ماڈیول سطح کی اشیاء ہیں، جہاں ان کی ضرورت ہو وہاں درآمد کی جاتی ہے۔

## `onAfterHandle` اور `mapResponse`

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

## `error()` اور `onError`

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

روٹس پر ایک `notfound.nexy` ایک نامعلوم URL پر براؤزر کو روٹ جواب دیتا ہے۔

## کوکیز

```ts filename="src/index.ts"
app.get("/api/theme", ({ cookie: { theme } }) => ({ theme: theme.value ?? "light" }));
```

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## عدن معاہدہ

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

ایک ایکشن Python فنکشن اور اس کا ٹائپ شدہ کلائنٹ ایک ساتھ ہے۔ Nexy دستخط Python سے TypeScript قسمیں تیار کرتا ہے:

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

دیکھیں [اعمال](../guides/actions.md)۔

## پلگ انز: `cors`، `swagger`، `static`

```ts filename="src/index.ts"
import { cors } from "@elysiajs/cors";
import { staticPlugin } from "@elysiajs/static";
import { swagger } from "@elysiajs/swagger";

app.use(cors({ origin: "https://example.com" })).use(swagger()).use(staticPlugin());
```

| ایلیسیا پلگ ان | نیکسی |
|---|---|
| `@elysiajs/cors` | `useCORS = {"allow_origins": [...]}` `nexyconfig.py` میں |
| `@elysiajs/swagger` | کچھ نہیں: `/docs` پہلے سے طے شدہ طور پر آن ہے۔ |
| `@elysiajs/static` | کچھ بھی نہیں: `public/` `/` پر پیش کیا جاتا ہے |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## ویب ساکٹس

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

## کے ساتھ ٹیسٹ `app.handle`

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

## چل رہا ہے۔

| ایلیسیا | نیکسی |
|---|---|
| `bun create elysia app` | `nx new` |
| `bun dev` | `nx dev` |
| `bun build --compile` | `nx build`، پھر `nx start` |
| `bun test` | `nx test` |

Nexy Python پر چلتا ہے۔ نوڈ کی ضرورت صرف اس وقت ہوتی ہے جب پروجیکٹ میں کلائنٹ کے اجزاء ہوں: Vite انہیں بناتا ہے، اور `nx start` اس کے بغیر چلتا ہے۔

## اگلے اقدامات

- [ایکسپریس سے Nexy تک](express.md)
- [Fastify سے Nexy تک](fastify.md)
- [اعمال](../guides/actions.md)
- [روٹ ہینڈلر](../routing/fbr/handlers/README.md)
