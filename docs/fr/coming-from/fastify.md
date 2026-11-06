# De Fastify à Nexy

Dans Nexy, une route Fastify devient un fichier Python sous `src/routes/` : les schémas JSON deviennent des modèles Pydantic, les plugins avec un `prefix` deviennent des dossiers et les hooks deviennent des fichiers `dependencies.py` et `middleware.py`.

Chaque section ci-dessous montre une habitude Fastify, puis la même chose dans Nexy.

## Un itinéraire

```js filename="serveur.js"
import Fastify from "fastify";

const app = Fastify({ logger: true });

app.get("/api/hello", async () => ({ message: "Hello" }));

await app.listen({ port: 3000 });
```

Le chemin du fichier est l'URL et le nom de la fonction est la méthode :

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

Chaque requête est journalisée avec sa méthode, son chemin, son statut et son heure, sans aucun enregistreur à configurer.

## Paramètres et schémas de chaîne de requête

```js filename="serveur.js"
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

Le schéma est la signature : `[id]` dans le nom du fichier, tape sur les paramètres :

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## Schémas corporels

```js filename="serveur.js"
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

Un corps qui échoue répond `422`, où Fastify répond `400`.

## Schémas de réponse

```js filename="serveur.js"
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

Le type de retour fait ce que fait le schéma de réponse : les champs qu'il ne déclare pas sont laissés de côté.

```python filename="src/routes/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## Plugins avec un préfixe

```js filename="routes/admin.js"
export default async function admin(app) {
  app.get("/stats", async () => ({ users: 3 }));
}
```

```js filename="serveur.js"
app.register(admin, { prefix: "/admin" });
```

Le dossier est le préfixe, et rien n'est enregistré :

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Crochets `preHandler` et `onRequest`

```js filename="routes/admin.js"
export default async function admin(app) {
  app.addHook("preHandler", async (request, reply) => {
    if (request.headers["x-role"] !== "admin") {
      return reply.code(403).send({ error: "Admins only" });
    }
  });
}
```

Un hook limité à un plugin est un `dependencies.py` dans son dossier :

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## Crochets `onSend` et `onResponse`

```js filename="serveur.js"
app.addHook("onSend", async (request, reply, payload) => {
  reply.header("x-app", "demo");
  return payload;
});
```

Le code après `call_next` dans un `middleware.py` s'exécute à la sortie :

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `decorate` et `decorateRequest`

```js filename="serveur.js"
app.decorate("db", { users: () => [{ name: "Ada" }] });

app.get("/api/users", async function () {
  return this.db.users();
});
```

Un objet partagé est une fonction qui le renvoie, et un gestionnaire le demande avec `Depends` :

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

Un test l'échange avec `app.dependency_overrides[get_db]`.

## `@fastify/cors`, `@fastify/compress`, `@fastify/cookie`

```js filename="serveur.js"
await app.register(import("@fastify/cors"), { origin: "https://example.com" });
await app.register(import("@fastify/compress"));
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

Un cookie n'a pas besoin de plugin : lisez-le avec un paramètre `Cookie`, paramétrez-le avec `response.set_cookie`.

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## `setErrorHandler` et `setNotFoundHandler`

```js filename="serveur.js"
app.setNotFoundHandler((request, reply) => reply.code(404).type("text/html").send("<h1>Not found</h1>"));
```

Les navigateurs obtiennent `notfound.nexy`, les clients API `{"detail": "Not Found"}` :

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

Un gestionnaire qui sait ce qui n'a pas fonctionné le signale :

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id}
```

## `@fastify/static`

```js filename="serveur.js"
await app.register(import("@fastify/static"), { root: path.join(__dirname, "public") });
```

Rien à écrire : `public/` est servi à `/`.

## `@fastify/websocket`

```js filename="serveur.js"
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

```js filename="serveur.js"
await app.register(import("@fastify/swagger"));
await app.register(import("@fastify/swagger-ui"), { routePrefix: "/docs" });
```

Rien à enregistrer : le schéma OpenAPI est construit à partir des annotations de type et servi dans `/docs`.

## Tests avec `inject`

```js filename="serveur.test.js"
const response = await app.inject({ method: "GET", url: "/api/hello" });
expect(response.json()).toEqual({ message: "Hello" });
```

`TestClient` appelle également l'application en mémoire, sans port :

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Courir

| Fastifier | Nexy |
|---|---|
| `npm init fastify` | `nx new` |
| `fastify start -w app.js` | `nx dev` |
| `node server.js` en production | `nx build`, puis `nx start` |
| `npm test` | `nx test` |

## Prochaines étapes

- [De l’Express à Nexy](express.md)
- [Gestionnaires de routes](../routing/fbr/handlers/README.md)
- [Validation et erreurs](../routing/fbr/handlers/validation-and-errors.md)
- [Dépendances et gardiens](../routing/fbr/dependencies/README.md)
