# От Элизии до Некси

В Nexy маршрут Elysia становится Python файлом в `src/routes/`: схемы `t.Object` становятся Pydantic моделями, `.group` становится папкой, `beforeHandle` - `dependencies.py`, а типизированный клиент Идена становится типизированными действиями.

В каждом разделе ниже показаны привычки Элизии, а затем то же самое в Некси.

## Маршрут

```ts filename="источник/index.ts"
import { Elysia } from "elysia";

new Elysia().get("/api/hello", () => ({ message: "Hello" })).listen(3000);
```

Путь к файлу - это URL-адрес, имя функции - это метод:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Параметры и запрос с помощью `t`

```ts filename="источник/index.ts"
import { Elysia, t } from "elysia";

new Elysia().get("/api/users/:id", ({ params, query }) => ({ id: params.id, fields: query.fields }), {
  params: t.Object({ id: t.Numeric() }),
  query: t.Object({ fields: t.Optional(t.String()) }),
});
```

Типы идут по параметрам, а `:id` - это сегмент `[id]`:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## Тело с `t.Object`

```ts filename="источник/index.ts"
app.post("/api/items", ({ body, set }) => {
  set.status = 201;
  return body;
}, {
  body: t.Object({ name: t.String(), price: t.Number({ exclusiveMinimum: 0 }) }),
});
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

## `response` схемы

```ts filename="источник/index.ts"
app.get("/api/me", () => ({ name: "Ada" }), {
  response: t.Object({ name: t.String() }),
});
```

Тип возвращаемого значения - это схема ответа: необъявленные поля исключаются из ответа.

```python filename="src/routes/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## `.group`

```ts filename="источник/index.ts"
app.group("/admin", (admin) => admin.get("/stats", () => ({ users: 3 })));
```

Папка представляет собой группу:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `beforeHandle` и `guard`

```ts filename="источник/index.ts"
app.group("/admin", (admin) =>
  admin
    .guard({
      beforeHandle({ headers, error }) {
        if (headers["x-role"] !== "admin") return error(403, "Admins only");
      },
    })
    .get("/stats", () => ({ users: 3 })),
);
```

`dependencies.py` охраняет каждый маршрут своей папки:

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `derive`, `decorate` и `state`

```ts filename="источник/index.ts"
app
  .derive(({ headers }) => ({ token: headers.authorization?.replace("Bearer ", "") }))
  .get("/api/whoami", ({ token }) => ({ token }));
```

То, что `derive` добавляет в контекст, - это зависимость, запрошенная обработчиком:

```python filename="src/routes/api/whoami.py"
from nexy.http import Depends, Header


def token(authorization: str = Header("")) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(token: str = Depends(token)):
    return {"token": token}
```

`decorate` и `state` - это простые объекты уровня модуля, импортированные туда, где они необходимы.

## `onAfterHandle` и `mapResponse`

```ts filename="источник/index.ts"
app.onAfterHandle(({ set }) => {
  set.headers["x-app"] = "demo";
});
```

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `error()` и `onError`

```ts filename="источник/index.ts"
app.get("/api/orders/:id", ({ params, error }) => {
  if (Number(params.id) > 100) return error(404, "No such order");
  return { id: params.id };
});
```

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id}
```

`notfound.nexy` в корне маршрутов отвечает браузерам на неизвестный URL-адрес.

## Файлы cookie

```ts filename="источник/index.ts"
app.get("/api/theme", ({ cookie: { theme } }) => ({ theme: theme.value ?? "light" }));
```

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## Эдемский договор

```ts filename="источник/index.ts"
const app = new Elysia().post("/todos", ({ body }) => ({ title: body.title, done: false }), {
  body: t.Object({ title: t.String() }),
});

export type App = typeof app;
```

```ts filename="клиент.ц"
import { treaty } from "@elysiajs/eden";
import type { App } from "./src/index";

const api = treaty<App>("localhost:3000");
const { data } = await api.todos.post({ title: "Write the docs" });
```

Действие - это функция Python и ее типизированный клиент одновременно. Nexy генерирует типы TypeScript из сигнатуры Python:

```python filename="src/actions/todos.py"
from pydantic import BaseModel

from nexy.decorators import Action


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    return Todo(title=title)
```

```tsx filename="источник/компоненты/AddTodo.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export function AddTodo() {
  const { run, pending, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```

См. [Действия](../guides/actions.md).

## Плагины: `cors`, `swagger`, `static`

```ts filename="источник/index.ts"
import { cors } from "@elysiajs/cors";
import { staticPlugin } from "@elysiajs/static";
import { swagger } from "@elysiajs/swagger";

app.use(cors({ origin: "https://example.com" })).use(swagger()).use(staticPlugin());
```

| Плагин Элизии | Некси |
|---|---|
| `@elysiajs/cors` | `useCORS = {"allow_origins": [...]}` в `nexyconfig.py` |
| `@elysiajs/swagger` | ничего: `/docs` включено по умолчанию |
| `@elysiajs/static` | ничего: `public/` обслуживается в `/` |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## Вебсокеты

```ts filename="источник/index.ts"
app.ws("/ws/echo", {
  message(ws, message) {
    ws.send(message);
  },
});
```

```python filename="src/routes/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## Тесты с `app.handle`

```ts filename="тест/index.test.ts"
import { describe, expect, it } from "bun:test";

it("says hello", async () => {
  const response = await app.handle(new Request("http://localhost/api/hello"));
  expect(await response.json()).toEqual({ message: "Hello" });
});
```

```python filename="тесты/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Бег

| Элизия | Некси |
|---|---|
| `bun create elysia app` | `nx new` |
| `bun dev` | `nx dev` |
| `bun build --compile` | `nx build`, затем `nx start` |
| `bun test` | `nx test` |

Nexy работает на Python. Node необходим только в том случае, если в проекте есть клиентские компоненты: Vite собирает их, а `nx start` запускается без него.

## Следующие шаги

- [От Экспресса до Некси](express.md)
- [От Fastify до Nexy](fastify.md)
- [Действия](../guides/actions.md)
- [Обработчики маршрутов](../routing/fbr/handlers/README.md)
