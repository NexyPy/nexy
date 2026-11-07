# От Fastify до Nexy

В Nexy маршрут Fastify становится файлом Python в `src/routes/`: схемы JSON становятся моделями Pydantic, плагины с `prefix` становятся папками, а перехватчики становятся файлами `dependencies.py` и `middleware.py`.

В каждом разделе ниже показаны привычки Fastify, а затем то же самое в Nexy.

## Маршрут

```js filename="сервер.js"
import Fastify from "fastify";

const app = Fastify({ logger: true });

app.get("/api/hello", async () => ({ message: "Hello" }));

await app.listen({ port: 3000 });
```

Путь к файлу - это URL-адрес, а имя функции - это метод:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

Каждый запрос регистрируется с указанием его метода, пути, статуса и времени, без необходимости настройки регистратора.

## Схемы параметров и строк запроса

```js filename="сервер.js"
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

Схема представляет собой подпись: `[id]` в имени файла, в параметрах введите:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## Схемы тела

```js filename="сервер.js"
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

Тело, которое не прошло проверку, отвечает `422`, а Fastify отвечает `400`.

## Схемы ответов

```js filename="сервер.js"
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

Тип возвращаемого значения делает то же, что и схема ответа: поля, которые он не объявляет, опускаются.

```python filename="src/routes/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## Плагины с префиксом

```js filename="маршруты/admin.js"
export default async function admin(app) {
  app.get("/stats", async () => ({ users: 3 }));
}
```

```js filename="сервер.js"
app.register(admin, { prefix: "/admin" });
```

Папка стоит префикс, и ничего не прописано:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Крючки `preHandler` и `onRequest`

```js filename="маршруты/admin.js"
export default async function admin(app) {
  app.addHook("preHandler", async (request, reply) => {
    if (request.headers["x-role"] !== "admin") {
      return reply.code(403).send({ error: "Admins only" });
    }
  });
}
```

Хук, привязанный к плагину, - это `dependencies.py` в его папке:

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## Крючки `onSend` и `onResponse`

```js filename="сервер.js"
app.addHook("onSend", async (request, reply, payload) => {
  reply.header("x-app", "demo");
  return payload;
});
```

Код после `call_next` в `middleware.py` выполняется на выходе:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `decorate` и `decorateRequest`

```js filename="сервер.js"
app.decorate("db", { users: () => [{ name: "Ada" }] });

app.get("/api/users", async function () {
  return this.db.users();
});
```

Общий объект - это функция, которая возвращает его, а обработчик запрашивает его с помощью `Depends`:

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

Тест заменяет его на `app.dependency_overrides[get_db]`.

## `@fastify/cors`, `@fastify/compress`, `@fastify/cookie`

```js filename="сервер.js"
await app.register(import("@fastify/cors"), { origin: "https://example.com" });
await app.register(import("@fastify/compress"));
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

Файл cookie не нуждается в плагине: прочитайте его с помощью параметра `Cookie`, установите его с помощью `response.set_cookie`.

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## `setErrorHandler` и `setNotFoundHandler`

```js filename="сервер.js"
app.setNotFoundHandler((request, reply) => reply.code(404).type("text/html").send("<h1>Not found</h1>"));
```

Браузеры получают `notfound.nexy`, API-клиенты `{"detail": "Not Found"}`:

```nexy filename="источник/маршруты/notfound.nexy"
<h1>Not found</h1>
```

Обработчик, который знает, что пошло не так, вызывает его:

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id}
```

## `@fastify/static`

```js filename="сервер.js"
await app.register(import("@fastify/static"), { root: path.join(__dirname, "public") });
```

Писать нечего: `public/` обслуживается в `/`.

## `@fastify/websocket`

```js filename="сервер.js"
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

```js filename="сервер.js"
await app.register(import("@fastify/swagger"));
await app.register(import("@fastify/swagger-ui"), { routePrefix: "/docs" });
```

Регистрировать нечего: схема OpenAPI построена на основе аннотаций типов и обслуживается в `/docs`.

## Тесты с `inject`

```js filename="сервер.test.js"
const response = await app.inject({ method: "GET", url: "/api/hello" });
expect(response.json()).toEqual({ message: "Hello" });
```

`TestClient` также вызывает приложение в памяти, без порта:

```python filename="тесты/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Бег

| Фиксировать | Некси |
|---|---|
| `npm init fastify` | `nx new` |
| `fastify start -w app.js` | `nx dev` |
| `node server.js` в производстве | `nx build`, затем `nx start` |
| `npm test` | `nx test` |

## Следующие шаги

- [От Экспресса до Некси](express.md)
- [Обработчики маршрутов](../routing/fbr/handlers/README.md)
- [Проверка и ошибки](../routing/fbr/handlers/validation-and-errors.md)
- [Зависимости и меры защиты](../routing/fbr/dependencies/README.md)
