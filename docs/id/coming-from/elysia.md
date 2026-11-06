# Dari Elysia hingga Nexy

Di Nexy, rute Elysia menjadi file Python di bawah `src/routes/`: skema `t.Object` menjadi model Pydantic, `.group` menjadi folder, `beforeHandle` menjadi `dependencies.py`, dan klien Eden yang diketik menjadi tindakan yang diketik.

Setiap bagian di bawah menunjukkan kebiasaan Elysia, lalu hal yang sama di Nexy.

## Sebuah rute

```ts filename="src/index.ts"
import { Elysia } from "elysia";

new Elysia().get("/api/hello", () => ({ message: "Hello" })).listen(3000);
```

Jalur file adalah URL, nama fungsinya adalah metodenya:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Param dan kueri dengan `t`

```ts filename="src/index.ts"
import { Elysia, t } from "elysia";

new Elysia().get("/api/users/:id", ({ params, query }) => ({ id: params.id, fields: query.fields }), {
  params: t.Object({ id: t.Numeric() }),
  query: t.Object({ fields: t.Optional(t.String()) }),
});
```

Tipenya berdasarkan parameter, dan `:id` adalah segmen `[id]`:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## Tubuh dengan `t.Object`

```ts filename="src/index.ts"
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

## `response` skema

```ts filename="src/index.ts"
app.get("/api/me", () => ({ name: "Ada" }), {
  response: t.Object({ name: t.String() }),
});
```

Jenis yang dikembalikan adalah skema respons: bidang yang tidak dideklarasikan tidak dimasukkan dalam jawaban.

```python filename="src/routes/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## `.group`

```ts filename="src/index.ts"
app.group("/admin", (admin) => admin.get("/stats", () => ({ users: 3 })));
```

Foldernya adalah grup:

```python filename="src/route/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `beforeHandle` dan `guard`

```ts filename="src/index.ts"
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

A `dependencies.py` menjaga setiap rute foldernya:

```python filename="src/rute/admin/dependensi.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `derive`, `decorate` dan `state`

```ts filename="src/index.ts"
app
  .derive(({ headers }) => ({ token: headers.authorization?.replace("Bearer ", "") }))
  .get("/api/whoami", ({ token }) => ({ token }));
```

Apa yang `derive` tambahkan ke dalam konteks adalah ketergantungan, yang diminta oleh pengendali:

```python filename="src/routes/api/whoami.py"
from nexy.http import Depends, Header


def token(authorization: str = Header("")) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(token: str = Depends(token)):
    return {"token": token}
```

`decorate` dan `state` adalah objek tingkat modul biasa, yang diimpor jika diperlukan.

## `onAfterHandle` dan `mapResponse`

```ts filename="src/index.ts"
app.onAfterHandle(({ set }) => {
  set.headers["x-app"] = "demo";
});
```

```python filename="src/rute/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `error()` dan `onError`

```ts filename="src/index.ts"
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

A `notfound.nexy` di root rute menjawab browser pada URL yang tidak diketahui.

## kue

```ts filename="src/index.ts"
app.get("/api/theme", ({ cookie: { theme } }) => ({ theme: theme.value ?? "light" }));
```

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## Perjanjian Eden

```ts filename="src/index.ts"
const app = new Elysia().post("/todos", ({ body }) => ({ title: body.title, done: false }), {
  body: t.Object({ title: t.String() }),
});

export type App = typeof app;
```

```ts filename="klien.ts"
import { treaty } from "@elysiajs/eden";
import type { App } from "./src/index";

const api = treaty<App>("localhost:3000");
const { data } = await api.todos.post({ title: "Write the docs" });
```

Suatu tindakan adalah fungsi Python dan klien yang diketiknya sekaligus. Nexy menghasilkan tipe TypeScript dari tanda tangan Python:

```python filename="src/aksi/todos.py"
from pydantic import BaseModel

from nexy.decorators import Action


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    return Todo(title=title)
```

```tsx filename="src/components/AddTodo.tsx"
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

Lihat [Tindakan](../guides/actions.md).

## Plugin: `cors`, `swagger`, `static`

```ts filename="src/index.ts"
import { cors } from "@elysiajs/cors";
import { staticPlugin } from "@elysiajs/static";
import { swagger } from "@elysiajs/swagger";

app.use(cors({ origin: "https://example.com" })).use(swagger()).use(staticPlugin());
```

| Plugin Elysia | Nexy |
|---|---|
| `@elysiajs/cors` | `useCORS = {"allow_origins": [...]}` di `nexyconfig.py` |
| `@elysiajs/swagger` | tidak ada: `/docs` diaktifkan secara default |
| `@elysiajs/static` | tidak ada: `public/` disajikan di `/` |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## soket web

```ts filename="src/index.ts"
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

## Tes dengan `app.handle`

```ts filename="tes/index.test.ts"
import { describe, expect, it } from "bun:test";

it("says hello", async () => {
  const response = await app.handle(new Request("http://localhost/api/hello"));
  expect(await response.json()).toEqual({ message: "Hello" });
});
```

```python filename="tes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Berlari

| Elysia | Nexy |
|---|---|
| `bun create elysia app` | `nx new` |
| `bun dev` | `nx dev` |
| `bun build --compile` | `nx build`, lalu `nx start` |
| `bun test` | `nx test` |

Nexy berjalan pada Python. Node hanya diperlukan ketika proyek memiliki komponen klien: Vite membangunnya, dan `nx start` berjalan tanpanya.

## Langkah selanjutnya

- [Dari Ekspres ke Nexy](express.md)
- [Dari Fastify ke Nexy](fastify.md)
- [Tindakan](../guides/actions.md)
- [Pengendali rute](../routing/fbr/handlers/README.md)
