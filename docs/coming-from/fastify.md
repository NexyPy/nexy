# From Fastify to Nexy

In Nexy a Fastify route becomes a Python file under `src/routes/`: JSON schemas become Pydantic
models, plugins with a `prefix` become folders, and hooks become `dependencies.py` and
`middleware.py` files.

Each section below shows a Fastify habit, then the same thing in Nexy.

## A route

```js filename="server.js"
import Fastify from "fastify";

const app = Fastify({ logger: true });

app.get("/api/hello", async () => ({ message: "Hello" }));

await app.listen({ port: 3000 });
```

The file path is the URL, and the function name is the method:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

Every request is logged with its method, path, status and time, with no logger to set up.

## Params and querystring schemas

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

The schema is the signature: `[id]` in the file name, types on the parameters:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## Body schemas

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

A body that fails answers `422`, where Fastify answers `400`.

## Response schemas

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

The return type does what the response schema does: fields it does not declare are left out.

```python filename="src/routes/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## Plugins with a prefix

```js filename="routes/admin.js"
export default async function admin(app) {
  app.get("/stats", async () => ({ users: 3 }));
}
```

```js filename="server.js"
app.register(admin, { prefix: "/admin" });
```

The folder is the prefix, and nothing is registered:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `preHandler` and `onRequest` hooks

```js filename="routes/admin.js"
export default async function admin(app) {
  app.addHook("preHandler", async (request, reply) => {
    if (request.headers["x-role"] !== "admin") {
      return reply.code(403).send({ error: "Admins only" });
    }
  });
}
```

A hook scoped to a plugin is a `dependencies.py` in its folder:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `onSend` and `onResponse` hooks

```js filename="server.js"
app.addHook("onSend", async (request, reply, payload) => {
  reply.header("x-app", "demo");
  return payload;
});
```

Code after `call_next` in a `middleware.py` runs on the way out:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `decorate` and `decorateRequest`

```js filename="server.js"
app.decorate("db", { users: () => [{ name: "Ada" }] });

app.get("/api/users", async function () {
  return this.db.users();
});
```

A shared object is a function that returns it, and a handler asks for it with `Depends`:

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

A test swaps it with `app.dependency_overrides[get_db]`.

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

A cookie needs no plugin: read it with a `Cookie` parameter, set it with `response.set_cookie`.

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## `setErrorHandler` and `setNotFoundHandler`

```js filename="server.js"
app.setNotFoundHandler((request, reply) => reply.code(404).type("text/html").send("<h1>Not found</h1>"));
```

Browsers get `notfound.nexy`, API clients `{"detail": "Not Found"}`:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

A handler that knows what went wrong raises it:

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

Nothing to write: `public/` is served at `/`.

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

Nothing to register: the OpenAPI schema is built from the type annotations and served at `/docs`.

## Tests with `inject`

```js filename="server.test.js"
const response = await app.inject({ method: "GET", url: "/api/hello" });
expect(response.json()).toEqual({ message: "Hello" });
```

`TestClient` calls the application in memory too, with no port:

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Running

| Fastify | Nexy |
|---|---|
| `npm init fastify` | `nx new` |
| `fastify start -w app.js` | `nx dev` |
| `node server.js` in production | `nx build`, then `nx start` |
| `npm test` | `nx test` |

## Next steps

- [From Express to Nexy](express.md)
- [Route handlers](../routing/fbr/handlers/README.md)
- [Validation and errors](../routing/fbr/handlers/validation-and-errors.md)
- [Dependencies and guards](../routing/fbr/dependencies/README.md)
