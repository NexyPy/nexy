# ফাস্টফাই থেকে নেক্সি পর্যন্ত

নেক্সিতে একটি ফাস্টফাই রুট `src/routes/` এর অধীনে একটি Python ফাইল হয়ে যায়: JSON স্কিমাগুলি Pydantic মডেলে পরিণত হয়, একটি `prefix` সহ প্লাগইনগুলি ফোল্ডারে পরিণত হয় এবং হুকগুলি `dependencies.py` এবং `middleware.py` ফাইলে পরিণত হয়।

নীচের প্রতিটি বিভাগ একটি Fastify অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস।

## একটি রুট

```js filename="server.js"
import Fastify from "fastify";

const app = Fastify({ logger: true });

app.get("/api/hello", async () => ({ message: "Hello" }));

await app.listen({ port: 3000 });
```

ফাইল পাথ হল URL, এবং ফাংশনের নাম হল পদ্ধতি:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

প্রতিটি অনুরোধ তার পদ্ধতি, পথ, স্থিতি এবং সময় দিয়ে লগ করা হয়, সেট আপ করার জন্য কোন লগার ছাড়াই।

## প্যারাম এবং কোয়েরিস্ট্রিং স্কিমা

```js filename="server.js"
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

স্কিমা হল স্বাক্ষর: `[id]` ফাইলের নামে, পরামিতিগুলিতে প্রকারগুলি:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## বডি স্কিমা

```js filename="server.js"
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

একটি শরীর যা উত্তর দেয় `422`, যেখানে ফাস্টফাই উত্তর দেয় `400`।

## প্রতিক্রিয়া স্কিম

```js filename="server.js"
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

রিটার্ন টাইপ রেসপন্স স্কিমা যা করে তা করে: যে ক্ষেত্রগুলি এটি ঘোষণা করে না তা বাদ দেওয়া হয়।

```python filename="src/routes/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## একটি উপসর্গ সহ প্লাগইন

```js filename="routes/admin.js"
export default async function admin(app) {
  app.get("/stats", async () => ({ users: 3 }));
}
```

```js filename="server.js"
app.register(admin, { prefix: "/admin" });
```

ফোল্ডারটি উপসর্গ, এবং কিছুই নিবন্ধিত নেই:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `preHandler` এবং `onRequest` হুক

```js filename="routes/admin.js"
export default async function admin(app) {
  app.addHook("preHandler", async (request, reply) => {
    if (request.headers["x-role"] !== "admin") {
      return reply.code(403).send({ error: "Admins only" });
    }
  });
}
```

একটি প্লাগইন স্কোপ করা একটি হুক হল তার ফোল্ডারে একটি `dependencies.py`:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `onSend` এবং `onResponse` হুক

```js filename="server.js"
app.addHook("onSend", async (request, reply, payload) => {
  reply.header("x-app", "demo");
  return payload;
});
```

কোড পরে `call_next` আউট হওয়ার পথে একটি `middleware.py` রানে:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `decorate` এবং `decorateRequest`

```js filename="server.js"
app.decorate("db", { users: () => [{ name: "Ada" }] });

app.get("/api/users", async function () {
  return this.db.users();
});
```

একটি ভাগ করা অবজেক্ট হল একটি ফাংশন যা এটি ফেরত দেয় এবং একজন হ্যান্ডলার `Depends` এর সাথে এটির জন্য জিজ্ঞাসা করে:

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

একটি পরীক্ষা এটি `app.dependency_overrides[get_db]` এর সাথে অদলবদল করে।

## `@fastify/cors`, `@fastify/compress`, `@fastify/cookie`

```js filename="server.js"
await app.register(import("@fastify/cors"), { origin: "https://example.com" });
await app.register(import("@fastify/compress"));
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

একটি কুকির কোনো প্লাগইন লাগে না: এটি একটি `Cookie` প্যারামিটার দিয়ে পড়ুন, `response.set_cookie` দিয়ে সেট করুন।

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## `setErrorHandler` এবং `setNotFoundHandler`

```js filename="server.js"
app.setNotFoundHandler((request, reply) => reply.code(404).type("text/html").send("<h1>Not found</h1>"));
```

ব্রাউজার পায় `notfound.nexy`, API ক্লায়েন্ট `{"detail": "Not Found"}`:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

একজন হ্যান্ডলার যে জানে কি ভুল হয়েছে তা উত্থাপন করে:

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id}
```

## `@fastify/static`

```js filename="server.js"
await app.register(import("@fastify/static"), { root: path.join(__dirname, "public") });
```

লেখার কিছু নেই: `public/` `/` এ পরিবেশিত হয়।

## `@fastify/websocket`

```js filename="server.js"
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

```js filename="server.js"
await app.register(import("@fastify/swagger"));
await app.register(import("@fastify/swagger-ui"), { routePrefix: "/docs" });
```

নিবন্ধন করার জন্য কিছুই নেই: OpenAPI স্কিমা টাইপ টীকা থেকে তৈরি করা হয় এবং `/docs` এ পরিবেশিত হয়।

## সঙ্গে পরীক্ষা `inject`

```js filename="server.test.js"
const response = await app.inject({ method: "GET", url: "/api/hello" });
expect(response.json()).toEqual({ message: "Hello" });
```

`TestClient` অ্যাপ্লিকেশনটিকে মেমরিতেও কল করে, কোনো পোর্ট ছাড়াই:

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## চলছে

| দৃঢ় করা | নেক্সি |
|---|---|
| `npm init fastify` | `nx new` |
| `fastify start -w app.js` | `nx dev` |
| `node server.js` উৎপাদনে | `nx build`, তারপর `nx start` |
| `npm test` | `nx test` |

## পরবর্তী পদক্ষেপ

- [এক্সপ্রেস থেকে নেক্সি পর্যন্ত](express.md)
- [রুট হ্যান্ডলার](../routing/fbr/handlers/README.md)
- [বৈধতা এবং ত্রুটি](../routing/fbr/handlers/validation-and-errors.md)
- [নির্ভরতা এবং প্রহরী](../routing/fbr/dependencies/README.md)
