# Dari Fastify hingga Nexy

Di Nexy, rute Fastify menjadi file Python di bawah `src/routes/`: skema JSON menjadi model Pydantic, plugin dengan `prefix` menjadi folder, dan kait menjadi file `dependencies.py` dan `middleware.py`.

Setiap bagian di bawah ini menunjukkan kebiasaan Fastify, lalu hal yang sama di Nexy.

## Sebuah rute

```js filename="server.js"
import Fastify from "fastify";

const app = Fastify({ logger: true });

app.get("/api/hello", async () => ({ message: "Hello" }));

await app.listen({ port: 3000 });
```

Jalur file adalah URL, dan nama fungsinya adalah metodenya:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

Setiap permintaan dicatat dengan metode, jalur, status dan waktunya, tanpa logger yang harus diatur.

## Param dan skema string kueri

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

Skemanya adalah tanda tangan: `[id]` pada nama file, ketikkan parameter:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## Skema tubuh

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

Badan yang gagal menjawab `422`, sedangkan Fastify menjawab `400`.

## Skema respons

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

Tipe pengembalian melakukan apa yang dilakukan skema respons: bidang yang tidak dideklarasikan akan ditinggalkan.

```python filename="src/routes/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## Plugin dengan awalan

```js filename="rute/admin.js"
export default async function admin(app) {
  app.get("/stats", async () => ({ users: 3 }));
}
```

```js filename="server.js"
app.register(admin, { prefix: "/admin" });
```

Foldernya adalah awalan, dan tidak ada yang terdaftar:

```python filename="src/route/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `preHandler` dan `onRequest` kait

```js filename="rute/admin.js"
export default async function admin(app) {
  app.addHook("preHandler", async (request, reply) => {
    if (request.headers["x-role"] !== "admin") {
      return reply.code(403).send({ error: "Admins only" });
    }
  });
}
```

Kait yang dicakup ke plugin adalah `dependencies.py` di foldernya:

```python filename="src/rute/admin/dependensi.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## kait `onSend` dan `onResponse`

```js filename="server.js"
app.addHook("onSend", async (request, reply, payload) => {
  reply.header("x-app", "demo");
  return payload;
});
```

Kode setelah `call_next` di `middleware.py` dijalankan saat keluar:

```python filename="src/rute/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `decorate` dan `decorateRequest`

```js filename="server.js"
app.decorate("db", { users: () => [{ name: "Ada" }] });

app.get("/api/users", async function () {
  return this.db.users();
});
```

Objek bersama adalah fungsi yang mengembalikannya, dan pengendali memintanya dengan `Depends`:

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

Sebuah tes menukarnya dengan `app.dependency_overrides[get_db]`.

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

Cookie tidak memerlukan plugin: membacanya dengan parameter `Cookie`, mengaturnya dengan `response.set_cookie`.

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## `setErrorHandler` dan `setNotFoundHandler`

```js filename="server.js"
app.setNotFoundHandler((request, reply) => reply.code(404).type("text/html").send("<h1>Not found</h1>"));
```

Browser mendapatkan `notfound.nexy`, klien API `{"detail": "Not Found"}`:

```nexy filename="src/rute/tidak ditemukan.nexy"
<h1>Not found</h1>
```

Seorang pawang yang mengetahui apa yang salah akan memunculkannya:

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

Tidak ada yang perlu ditulis: `public/` disajikan di `/`.

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

Tidak ada yang perlu didaftarkan: skema OpenAPI dibuat dari anotasi tipe dan disajikan di `/docs`.

## Tes dengan `inject`

```js filename="server.test.js"
const response = await app.inject({ method: "GET", url: "/api/hello" });
expect(response.json()).toEqual({ message: "Hello" });
```

`TestClient` memanggil aplikasi di memori juga, tanpa port:

```python filename="tes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Berlari

| Kencangkan | Nexy |
|---|---|
| `npm init fastify` | `nx new` |
| `fastify start -w app.js` | `nx dev` |
| `node server.js` dalam produksi | `nx build`, lalu `nx start` |
| `npm test` | `nx test` |

## Langkah selanjutnya

- [Dari Ekspres ke Nexy](express.md)
- [Pengendali rute](../routing/fbr/handlers/README.md)
- [Validasi dan kesalahan](../routing/fbr/handlers/validation-and-errors.md)
- [Ketergantungan dan penjaga](../routing/fbr/dependencies/README.md)
