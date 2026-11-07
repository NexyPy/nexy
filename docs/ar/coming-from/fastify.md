# من Fastify إلى Nexy

في Nexy، يتحول مسار Fastify إلى ملف Python ضمن `src/routes/`: تصبح مخططات JSON نماذج Pydantic، والمكونات الإضافية التي تحتوي على `prefix` تصبح مجلدات، والخطافات تصبح ملفات `dependencies.py` و `middleware.py`.

يعرض كل قسم أدناه عادة Fastify، ثم نفس الشيء في Nexy.

## طريق

```js filename="server.js"
import Fastify from "fastify";

const app = Fastify({ logger: true });

app.get("/api/hello", async () => ({ message: "Hello" }));

await app.listen({ port: 3000 });
```

مسار الملف هو عنوان URL، واسم الوظيفة هو الطريقة:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

يتم تسجيل كل طلب بطريقته ومساره وحالته ووقته، دون الحاجة إلى إعداد مسجل.

## المعلمات ومخططات سلسلة الاستعلام

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

المخطط هو التوقيع: `[id]` في اسم الملف، ويكتب على المعلمات:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## مخططات الجسم

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

الجسم الذي يفشل يجيب `422`، حيث يجيب فاستيفي `400`.

## مخططات الاستجابة

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

يفعل نوع الإرجاع ما يفعله مخطط الاستجابة: يتم استبعاد الحقول التي لم يعلن عنها.

```python filename="src/routes/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## الإضافات مع البادئة

```js filename="الطرق/admin.js"
export default async function admin(app) {
  app.get("/stats", async () => ({ users: 3 }));
}
```

```js filename="server.js"
app.register(admin, { prefix: "/admin" });
```

المجلد هو البادئة، ولم يتم تسجيل أي شيء:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `preHandler` و `onRequest` خطافات

```js filename="الطرق/admin.js"
export default async function admin(app) {
  app.addHook("preHandler", async (request, reply) => {
    if (request.headers["x-role"] !== "admin") {
      return reply.code(403).send({ error: "Admins only" });
    }
  });
}
```

الخطاف الذي تم تحديده للمكون الإضافي هو `dependencies.py` في المجلد الخاص به:

```python filename="src/routes/admin/dependeency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `onSend` و `onResponse` خطافات

```js filename="server.js"
app.addHook("onSend", async (request, reply, payload) => {
  reply.header("x-app", "demo");
  return payload;
});
```

الكود بعد `call_next` في `middleware.py` يعمل في المخرج:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `decorate` و `decorateRequest`

```js filename="server.js"
app.decorate("db", { users: () => [{ name: "Ada" }] });

app.get("/api/users", async function () {
  return this.db.users();
});
```

الكائن المشترك هو دالة تُرجعه، ويطلبه المعالج باستخدام `Depends`:

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

اختبار يبدله بـ `app.dependency_overrides[get_db]`.

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

لا يحتاج ملف تعريف الارتباط إلى مكون إضافي: اقرأه باستخدام المعلمة `Cookie`، وقم بتعيينه باستخدام `response.set_cookie`.

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## `setErrorHandler` و `setNotFoundHandler`

```js filename="server.js"
app.setNotFoundHandler((request, reply) => reply.code(404).type("text/html").send("<h1>Not found</h1>"));
```

تحصل المتصفحات على `notfound.nexy`، عملاء API `{"detail": "Not Found"}`:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

المعالج الذي يعرف الخطأ الذي حدث يرفعه:

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

لا يوجد شيء للكتابة: `public/` يتم تقديمه في `/`.

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

لا يوجد شيء للتسجيل: تم إنشاء مخطط OpenAPI من التعليقات التوضيحية للنوع ويتم تقديمه في `/docs`.

## الاختبارات مع `inject`

```js filename="server.test.js"
const response = await app.inject({ method: "GET", url: "/api/hello" });
expect(response.json()).toEqual({ message: "Hello" });
```

`TestClient` يستدعي التطبيق في الذاكرة أيضًا، بدون منفذ:

```python filename="الاختبارات/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## الجري

| يصوم | نكسي |
|---|---|
| `npm init fastify` | `nx new` |
| `fastify start -w app.js` | `nx dev` |
| `node server.js` في الإنتاج | `nx build`، ثم `nx start` |
| `npm test` | `nx test` |

## الخطوات التالية

- [من إكسبريس إلى نيكسي](express.md)
- [معالجات الطريق](../routing/fbr/handlers/README.md)
- [التحقق من الصحة والأخطاء](../routing/fbr/handlers/validation-and-errors.md)
- [التبعيات والحراس](../routing/fbr/dependencies/README.md)
