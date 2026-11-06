# Do Fastify ao Nexy

No Nexy, uma rota Fastify se torna um arquivo Python em `src/routes/`: esquemas JSON se tornam modelos Pydantic, plug-ins com `prefix` se tornam pastas e ganchos se tornam arquivos `dependencies.py` e `middleware.py`.

Cada seção abaixo mostra um hábito do Fastify e a mesma coisa no Nexy.

## Uma rota

```js filename="servidor.js"
import Fastify from "fastify";

const app = Fastify({ logger: true });

app.get("/api/hello", async () => ({ message: "Hello" }));

await app.listen({ port: 3000 });
```

O caminho do arquivo é o URL e o nome da função é o método:

```python filename="src/rotas/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

Cada solicitação é registrada com seu método, caminho, status e hora, sem nenhum registrador para configurar.

## Parâmetros e esquemas de querystring

```js filename="servidor.js"
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

O esquema é a assinatura: `[id]` no nome do arquivo, digite os parâmetros:

```python filename="src/rotas/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## Esquemas corporais

```js filename="servidor.js"
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

Um corpo que falha responde `422`, onde Fastify responde `400`.

## Esquemas de resposta

```js filename="servidor.js"
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

O tipo de retorno faz o que o esquema de resposta faz: os campos que ele não declara são deixados de fora.

```python filename="src/rotas/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## Plug-ins com prefixo

```js filename="rotas/admin.js"
export default async function admin(app) {
  app.get("/stats", async () => ({ users: 3 }));
}
```

```js filename="servidor.js"
app.register(admin, { prefix: "/admin" });
```

A pasta é o prefixo e nada está registrado:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `preHandler` e `onRequest` ganchos

```js filename="rotas/admin.js"
export default async function admin(app) {
  app.addHook("preHandler", async (request, reply) => {
    if (request.headers["x-role"] !== "admin") {
      return reply.code(403).send({ error: "Admins only" });
    }
  });
}
```

Um gancho com escopo para um plugin é um `dependencies.py` em sua pasta:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `onSend` e `onResponse` ganchos

```js filename="servidor.js"
app.addHook("onSend", async (request, reply, payload) => {
  reply.header("x-app", "demo");
  return payload;
});
```

O código após `call_next` em um `middleware.py` é executado na saída:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `decorate` e `decorateRequest`

```js filename="servidor.js"
app.decorate("db", { users: () => [{ name: "Ada" }] });

app.get("/api/users", async function () {
  return this.db.users();
});
```

Um objeto compartilhado é uma função que o retorna, e um manipulador solicita isso com `Depends`:

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

Um teste troca por `app.dependency_overrides[get_db]`.

## `@fastify/cors`, `@fastify/compress`, `@fastify/cookie`

```js filename="servidor.js"
await app.register(import("@fastify/cors"), { origin: "https://example.com" });
await app.register(import("@fastify/compress"));
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

Um cookie não precisa de plugin: leia-o com um parâmetro `Cookie`, configure-o com `response.set_cookie`.

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## `setErrorHandler` e `setNotFoundHandler`

```js filename="servidor.js"
app.setNotFoundHandler((request, reply) => reply.code(404).type("text/html").send("<h1>Not found</h1>"));
```

Os navegadores obtêm `notfound.nexy`, clientes API `{"detail": "Not Found"}`:

```nexy filename="src/rotas/notfound.nexy"
<h1>Not found</h1>
```

Um manipulador que sabe o que deu errado aumenta:

```python filename="src/rotas/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id}
```

## `@fastify/static`

```js filename="servidor.js"
await app.register(import("@fastify/static"), { root: path.join(__dirname, "public") });
```

Nada a escrever: `public/` é servido em `/`.

## `@fastify/websocket`

```js filename="servidor.js"
await app.register(import("@fastify/websocket"));

app.get("/ws/echo", { websocket: true }, (socket) => {
  socket.on("message", (message) => socket.send(message));
});
```

```python filename="src/rotas/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## `@fastify/swagger`

```js filename="servidor.js"
await app.register(import("@fastify/swagger"));
await app.register(import("@fastify/swagger-ui"), { routePrefix: "/docs" });
```

Nada a registrar: o esquema OpenAPI é construído a partir das anotações de tipo e servido em `/docs`.

## Testes com `inject`

```js filename="servidor.test.js"
const response = await app.inject({ method: "GET", url: "/api/hello" });
expect(response.json()).toEqual({ message: "Hello" });
```

`TestClient` chama a aplicação na memória também, sem porta:

```python filename="testes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Correndo

| Fastificar | Nexy |
|---|---|
| `npm init fastify` | `nx new` |
| `fastify start -w app.js` | `nx dev` |
| `node server.js` em produção | `nx build`, então `nx start` |
| `npm test` | `nx test` |

## Próximas etapas

- [Do Expresso ao Nexy](express.md)
- [Manipuladores de rota](../routing/fbr/handlers/README.md)
- [Validação e erros](../routing/fbr/handlers/validation-and-errors.md)
- [Dependências e guardas](../routing/fbr/dependencies/README.md)
