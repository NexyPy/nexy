# Von Fastify bis Nexy

In Nexy wird eine Fastify-Route zu einer Python-Datei unter `src/routes/`: JSON-Schemas werden zu Pydantic-Modellen, Plugins mit einem `prefix` werden zu Ordnern und Hooks werden zu `dependencies.py`- und `middleware.py`-Dateien.

Jeder Abschnitt unten zeigt eine Fastify-Gewohnheit, dann dasselbe in Nexy.

## Eine Route

```js filename="server.js"
import Fastify from "fastify";

const app = Fastify({ logger: true });

app.get("/api/hello", async () => ({ message: "Hello" }));

await app.listen({ port: 3000 });
```

Der Dateipfad ist die URL und der Funktionsname ist die Methode:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

Jede Anfrage wird mit Methode, Pfad, Status und Zeit protokolliert, ohne dass ein Logger eingerichtet werden muss.

## Parameter und Abfragezeichenfolgeschemata

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

Das Schema ist die Signatur: `[id]` im Dateinamen, Typen auf den Parametern:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## Körperschemata

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

Ein Körper, der versagt, antwortet `422`, während Fastify antwortet `400`.

## Antwortschemata

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

Der Rückgabetyp macht das, was das Antwortschema tut: Felder, die er nicht deklariert, werden weggelassen.

```python filename="src/routes/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## Plugins mit einem Präfix

```js filename="Routen/admin.js"
export default async function admin(app) {
  app.get("/stats", async () => ({ users: 3 }));
}
```

```js filename="server.js"
app.register(admin, { prefix: "/admin" });
```

Der Ordner ist das Präfix und es ist nichts registriert:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `preHandler`- und `onRequest`-Haken

```js filename="Routen/admin.js"
export default async function admin(app) {
  app.addHook("preHandler", async (request, reply) => {
    if (request.headers["x-role"] !== "admin") {
      return reply.code(403).send({ error: "Admins only" });
    }
  });
}
```

Ein Hook, der sich auf ein Plugin bezieht, ist ein `dependencies.py` in seinem Ordner:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `onSend`- und `onResponse`-Haken

```js filename="server.js"
app.addHook("onSend", async (request, reply, payload) => {
  reply.header("x-app", "demo");
  return payload;
});
```

Code nach `call_next` in einem `middleware.py` läuft auf dem Weg nach draußen:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `decorate` und `decorateRequest`

```js filename="server.js"
app.decorate("db", { users: () => [{ name: "Ada" }] });

app.get("/api/users", async function () {
  return this.db.users();
});
```

Ein Shared Object ist eine Funktion, die es zurückgibt, und ein Handler fragt danach mit `Depends`:

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

Ein Test tauscht es mit `app.dependency_overrides[get_db]` aus.

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

Ein Cookie benötigt kein Plugin: Lesen Sie es mit einem `Cookie`-Parameter und setzen Sie es mit `response.set_cookie`.

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## `setErrorHandler` und `setNotFoundHandler`

```js filename="server.js"
app.setNotFoundHandler((request, reply) => reply.code(404).type("text/html").send("<h1>Not found</h1>"));
```

Browser erhalten `notfound.nexy`, API-Clients `{"detail": "Not Found"}`:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

Ein Handler, der weiß, was schief gelaufen ist, meldet Folgendes:

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

Nichts zu schreiben: `public/` wird um `/` serviert.

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

Nichts zu registrieren: Das OpenAPI-Schema wird aus den Typanmerkungen erstellt und unter `/docs` bereitgestellt.

## Tests mit `inject`

```js filename="server.test.js"
const response = await app.inject({ method: "GET", url: "/api/hello" });
expect(response.json()).toEqual({ message: "Hello" });
```

`TestClient` ruft die Anwendung auch im Speicher auf, ohne Port:

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Laufen

| Fasten | Nexy |
|---|---|
| `npm init fastify` | `nx new` |
| `fastify start -w app.js` | `nx dev` |
| `node server.js` in der Produktion | `nx build`, dann `nx start` |
| `npm test` | `nx test` |

## Nächste Schritte

- [Von Express zu Nexy](express.md)
- [Routenhandler](../routing/fbr/handlers/README.md)
- [Validierung und Fehler](../routing/fbr/handlers/validation-and-errors.md)
- [Abhängigkeiten und Wachen](../routing/fbr/dependencies/README.md)
