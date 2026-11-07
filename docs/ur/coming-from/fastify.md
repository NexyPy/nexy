# Fastify سے Nexy تک

Nexy میں Fastify روٹ `src/routes/` کے تحت ایک Python فائل بن جاتا ہے: JSON اسکیماز Pydantic ماڈل بن جاتے ہیں، `prefix` والے پلگ ان فولڈر بن جاتے ہیں، اور ہکس `dependencies.py` اور `middleware.py` فائلیں بن جاتے ہیں۔

نیچے دیا گیا ہر سیکشن فاسٹیفائی کی عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔

## ایک راستہ

```js filename="server.js"
import Fastify from "fastify";

const app = Fastify({ logger: true });

app.get("/api/hello", async () => ({ message: "Hello" }));

await app.listen({ port: 3000 });
```

فائل کا راستہ URL ہے، اور فنکشن کا نام طریقہ ہے:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

ہر درخواست کو اس کے طریقہ کار، راستے، حیثیت اور وقت کے ساتھ لاگ ان کیا جاتا ہے، جس میں کوئی لاگر نہیں ہوتا ہے۔

## پیرامز اور استفسار کے اسکیمے۔

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

اسکیما دستخط ہے: فائل کے نام میں `[id]`، پیرامیٹرز پر قسمیں:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## باڈی اسکیماس

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

ایک جسم جو جوابات میں ناکام ہوتا ہے `422`، جہاں فاسٹائف جواب دیتا ہے `400`۔

## جوابی اسکیمے۔

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

واپسی کی قسم وہی کرتی ہے جو جوابی اسکیما کرتا ہے: وہ فیلڈز جن کا اعلان نہیں کرتا ہے چھوڑ دیا جاتا ہے۔

```python filename="src/routes/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## ایک سابقہ کے ساتھ پلگ انز

```js filename="routes/admin.js"
export default async function admin(app) {
  app.get("/stats", async () => ({ users: 3 }));
}
```

```js filename="server.js"
app.register(admin, { prefix: "/admin" });
```

فولڈر سابقہ ہے، اور کچھ بھی رجسٹرڈ نہیں ہے:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `preHandler` اور `onRequest` ہکس

```js filename="routes/admin.js"
export default async function admin(app) {
  app.addHook("preHandler", async (request, reply) => {
    if (request.headers["x-role"] !== "admin") {
      return reply.code(403).send({ error: "Admins only" });
    }
  });
}
```

ایک پلگ ان کا دائرہ کار اس کے فولڈر میں `dependencies.py` ہے:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `onSend` اور `onResponse` ہکس

```js filename="server.js"
app.addHook("onSend", async (request, reply, payload) => {
  reply.header("x-app", "demo");
  return payload;
});
```

ایک `middleware.py` میں `call_next` کے بعد کوڈ باہر کے راستے پر چلتا ہے:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `decorate` اور `decorateRequest`

```js filename="server.js"
app.decorate("db", { users: () => [{ name: "Ada" }] });

app.get("/api/users", async function () {
  return this.db.users();
});
```

مشترکہ آبجیکٹ ایک فنکشن ہے جو اسے واپس کرتا ہے، اور ایک ہینڈلر اسے `Depends` کے ساتھ مانگتا ہے:

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

ایک ٹیسٹ اسے `app.dependency_overrides[get_db]` کے ساتھ تبدیل کرتا ہے۔

## `@fastify/cors`، `@fastify/compress`، `@fastify/cookie`

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

کوکی کو پلگ ان کی ضرورت نہیں ہے: اسے `Cookie` پیرامیٹر کے ساتھ پڑھیں، `response.set_cookie` کے ساتھ سیٹ کریں۔

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## `setErrorHandler` اور `setNotFoundHandler`

```js filename="server.js"
app.setNotFoundHandler((request, reply) => reply.code(404).type("text/html").send("<h1>Not found</h1>"));
```

براؤزرز کو `notfound.nexy`، API کلائنٹس `{"detail": "Not Found"}` ملتے ہیں:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

ایک ہینڈلر جو جانتا ہے کہ کیا غلط ہوا ہے اسے اٹھاتا ہے:

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

لکھنے کے لیے کچھ نہیں: `public/` `/` پر پیش کیا جاتا ہے۔

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

رجسٹر کرنے کے لیے کچھ نہیں: OpenAPI اسکیما ٹائپ تشریحات سے بنایا گیا ہے اور `/docs` پر پیش کیا گیا ہے۔

## کے ساتھ ٹیسٹ `inject`

```js filename="server.test.js"
const response = await app.inject({ method: "GET", url: "/api/hello" });
expect(response.json()).toEqual({ message: "Hello" });
```

`TestClient` ایپلی کیشن کو میموری میں بھی کال کرتا ہے، بغیر کسی پورٹ کے:

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## چل رہا ہے۔

| تیز کرنا | نیکسی |
|---|---|
| `npm init fastify` | `nx new` |
| `fastify start -w app.js` | `nx dev` |
| پیداوار میں `node server.js` | `nx build`، پھر `nx start` |
| `npm test` | `nx test` |

## اگلے اقدامات

- [ایکسپریس سے Nexy تک](express.md)
- [روٹ ہینڈلر](../routing/fbr/handlers/README.md)
- [توثیق اور غلطیاں](../routing/fbr/handlers/validation-and-errors.md)
- [انحصار اور محافظ ](../routing/fbr/dependencies/README.md)
