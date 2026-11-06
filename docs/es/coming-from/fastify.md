# De Fastify a Nexy

En Nexy, una ruta Fastify se convierte en un archivo Python en `src/routes/`: los esquemas JSON se convierten en modelos Pydantic, los complementos con un `prefix` se convierten en carpetas y los ganchos se convierten en archivos `dependencies.py` y `middleware.py`.

Cada sección a continuación muestra un hábito de Fastify, luego lo mismo en Nexy.

## una ruta

```js filename="servidor.js"
import Fastify from "fastify";

const app = Fastify({ logger: true });

app.get("/api/hello", async () => ({ message: "Hello" }));

await app.listen({ port: 3000 });
```

La ruta del archivo es la URL y el nombre de la función es el método:

```python filename="src/rutas/api/hola.py"
async def GET():
    return {"message": "Hello"}
```

Cada solicitud se registra con su método, ruta, estado y hora, sin necesidad de configurar un registrador.

## Parámetros y esquemas de cadena de consulta.

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

El esquema es la firma: `[id]` en el nombre del archivo, escribe los parámetros:

```python filename="src/rutas/api/usuarios/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## Esquemas corporales

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

```python filename="src/rutas/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

Un cuerpo que falla responde `422`, donde Fastify responde `400`.

## Esquemas de respuesta

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

El tipo de retorno hace lo que hace el esquema de respuesta: los campos que no declara quedan fuera.

```python filename="src/rutas/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## Complementos con prefijo

```js filename="rutas/admin.js"
export default async function admin(app) {
  app.get("/stats", async () => ({ users: 3 }));
}
```

```js filename="servidor.js"
app.register(admin, { prefix: "/admin" });
```

La carpeta es el prefijo y no hay nada registrado:

```python filename="src/rutas/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `preHandler` y `onRequest` ganchos

```js filename="rutas/admin.js"
export default async function admin(app) {
  app.addHook("preHandler", async (request, reply) => {
    if (request.headers["x-role"] !== "admin") {
      return reply.code(403).send({ error: "Admins only" });
    }
  });
}
```

Un gancho con alcance para un complemento es un `dependencies.py` en su carpeta:

```python filename="src/rutas/admin/dependencias.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `onSend` y `onResponse` ganchos

```js filename="servidor.js"
app.addHook("onSend", async (request, reply, payload) => {
  reply.header("x-app", "demo");
  return payload;
});
```

El código después de `call_next` en `middleware.py` se ejecuta al salir:

```python filename="src/rutas/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `decorate` y `decorateRequest`

```js filename="servidor.js"
app.decorate("db", { users: () => [{ name: "Ada" }] });

app.get("/api/users", async function () {
  return this.db.users();
});
```

Un objeto compartido es una función que lo devuelve y un controlador lo solicita con `Depends`:

```python filename="src/db.py"
class Db:
    def users(self) -> list[dict]:
        return [{"name": "Ada"}]


db = Db()


def get_db() -> Db:
    return db
```

```python filename="src/rutas/api/users/index.py"
from nexy.http import Depends

from src.db import Db, get_db


async def GET(db: Db = Depends(get_db)):
    return db.users()
```

Una prueba lo intercambia con `app.dependency_overrides[get_db]`.

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

Una cookie no necesita complemento: léala con un parámetro `Cookie`, configúrela con `response.set_cookie`.

```python filename="src/rutas/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## `setErrorHandler` y `setNotFoundHandler`

```js filename="servidor.js"
app.setNotFoundHandler((request, reply) => reply.code(404).type("text/html").send("<h1>Not found</h1>"));
```

Los navegadores obtienen `notfound.nexy`, clientes API `{"detail": "Not Found"}`:

```nexy filename="src/rutas/notfound.nexy"
<h1>Not found</h1>
```

Un controlador que sabe qué salió mal lo plantea:

```python filename="src/routes/api/orders/[id].py"
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

Nada que escribir: `public/` se sirve en `/`.

## `@fastify/websocket`

```js filename="servidor.js"
await app.register(import("@fastify/websocket"));

app.get("/ws/echo", { websocket: true }, (socket) => {
  socket.on("message", (message) => socket.send(message));
});
```

```python filename="src/rutas/ws/echo.py"
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

No hay nada que registrar: el esquema OpenAPI se construye a partir de las anotaciones de tipo y se sirve en `/docs`.

## Pruebas con `inject`

```js filename="servidor.test.js"
const response = await app.inject({ method: "GET", url: "/api/hello" });
expect(response.json()).toEqual({ message: "Hello" });
```

`TestClient` también llama a la aplicación en memoria, sin puerto:

```python filename="pruebas/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## corriendo

| Fastificar | nexy |
|---|---|
| `npm init fastify` | `nx new` |
| `fastify start -w app.js` | `nx dev` |
| `node server.js` en producción | `nx build`, luego `nx start` |
| `npm test` | `nx test` |

## Próximos pasos

- [De Express a Nexy](express.md)
- [Controladores de ruta](../routing/fbr/handlers/README.md)
- [Validación y errores](../routing/fbr/handlers/validation-and-errors.md)
- [Dependencias y guardias](../routing/fbr/dependencies/README.md)
