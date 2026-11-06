# De Hono a Nexy

En Nexy, una ruta Hono se convierte en un archivo Python en `src/routes/`: `c.req` se convierte en parámetros escritos, `zValidator` en un modelo Pydantic, `app.route` en una carpeta y el cliente RPC `hc` en acciones escritas.

Cada sección a continuación muestra un hábito de Hono, luego lo mismo en Nexy.

## una ruta

```ts filename="src/index.ts"
import { Hono } from "hono";

const app = new Hono();

app.get("/api/hello", (c) => c.json({ message: "Hello" }));

export default app;
```

La ruta del archivo es la URL, el nombre de la función es el método y un `dict` devuelto es `c.json`:

```python filename="src/rutas/api/hola.py"
async def GET():
    return {"message": "Hello"}
```

## `c.req.param` y `c.req.query`

```ts filename="src/index.ts"
app.get("/api/users/:id", (c) => {
  const id = Number(c.req.param("id"));
  const fields = c.req.query("fields");
  return c.json({ id, fields });
});
```

```python filename="src/rutas/api/usuarios/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` responde `404`: `abc` no es un `int`.

## `zValidator`

```ts filename="src/index.ts"
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";

const NewItem = z.object({ name: z.string(), price: z.number().positive() });

app.post("/api/items", zValidator("json", NewItem), (c) => c.json(c.req.valid("json"), 201));
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

## `app.route` y `basePath`

```ts filename="src/admin.ts"
export const admin = new Hono();

admin.get("/stats", (c) => c.json({ users: 3 }));
```

```ts filename="src/index.ts"
app.route("/admin", admin);
```

La carpeta es la ruta base:

```python filename="src/rutas/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Middleware en un camino

```ts filename="src/index.ts"
import { createMiddleware } from "hono/factory";
import { HTTPException } from "hono/http-exception";

const requireAdmin = createMiddleware(async (c, next) => {
  if (c.req.header("x-role") !== "admin") throw new HTTPException(403, { message: "Admins only" });
  await next();
});

app.use("/admin/*", requireAdmin);
```

`/admin/*` es la carpeta: un `dependencies.py` se ejecuta antes de cada ruta debajo de ella.

```python filename="src/rutas/admin/dependencias.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## Middleware en torno a cada solicitud

```ts filename="src/index.ts"
app.use("*", async (c, next) => {
  await next();
  c.header("x-app", "demo");
});
```

```python filename="src/rutas/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `c.set` y `c.get`

```ts filename="src/index.ts"
app.use("/api/*", async (c, next) => {
  c.set("token", c.req.header("authorization")?.replace("Bearer ", ""));
  await next();
});

app.get("/api/whoami", (c) => c.json({ token: c.get("token") }));
```

Un valor calculado para el controlador es una dependencia, solicitada por su nombre:

```python filename="src/rutas/api/whoami.py"
from nexy.http import Depends, Header


def token(authorization: str = Header("")) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(token: str = Depends(token)):
    return {"token": token}
```

## Middleware incorporado

```ts filename="src/index.ts"
import { compress } from "hono/compress";
import { cors } from "hono/cors";
import { secureHeaders } from "hono/secure-headers";

app.use("*", cors({ origin: "https://example.com" }), compress(), secureHeaders());
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

De los conjuntos de encabezados `secureHeaders`, `nx start` agrega dos por sí solo: `X-Content-Type-Options` y `Referrer-Policy`. Configure los demás, como un `Content-Security-Policy`, en un `middleware.py`. Consulte [Seguridad](../reference/security.md).

## `c.html` y Honor JSX

```tsx filename="src/index.tsx"
app.get("/users", (c) => {
  const users = [{ name: "Ada" }, { name: "Alan" }];
  return c.html(
    <ul>
      {users.map((user) => (
        <li>{user.name}</li>
      ))}
    </ul>,
  );
});
```

Una página `.nexy` representa HTML en el servidor de Python y Jinja2:

```nexy filename="src/rutas/usuarios.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

JSX interactivo sigue siendo JSX: un componente React, Preact o Solid se representa como una isla de la página. Ver [Islas](../rendering/islands.md).

## `c.redirect`

```ts filename="src/index.ts"
app.get("/old", (c) => c.redirect("/new", 301));
```

```python filename="src/rutas/old.py"
from nexy.http import RedirectResponse


async def GET():
    return RedirectResponse("/new", status_code=301)
```

## galletas

```ts filename="src/index.ts"
import { getCookie, setCookie } from "hono/cookie";

app.get("/api/theme", (c) => c.json({ theme: getCookie(c, "theme") ?? "light" }));
app.post("/api/theme", (c) => {
  setCookie(c, "theme", "dark");
  return c.json({ theme: "dark" });
});
```

```python filename="src/rutas/api/theme.py"
from nexy.http import Cookie, JSONResponse


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}


async def POST():
    response = JSONResponse({"theme": "dark"})
    response.set_cookie("theme", "dark")
    return response
```

## `HTTPException`, `notFound` y `onError`

```ts filename="src/index.ts"
app.get("/api/orders/:id", (c) => {
  if (Number(c.req.param("id")) > 100) throw new HTTPException(404, { message: "No such order" });
  return c.json({ id: c.req.param("id") });
});

app.notFound((c) => c.html("<h1>Not found</h1>", 404));
```

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id}
```

```nexy filename="src/rutas/notfound.nexy"
<h1>Not found</h1>
```

## `serveStatic`

```ts filename="src/index.ts"
import { serveStatic } from "hono/bun";

app.use("/*", serveStatic({ root: "./public" }));
```

Nada que escribir: `public/` se sirve en `/`.

## WebSockets

```ts filename="src/index.ts"
import { upgradeWebSocket } from "hono/bun";

app.get(
  "/ws/echo",
  upgradeWebSocket(() => ({
    onMessage(event, ws) {
      ws.send(event.data);
    },
  })),
);
```

```python filename="src/rutas/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## El cliente RPC `hc`

```ts filename="src/index.ts"
const routes = app.post("/todos", zValidator("json", z.object({ title: z.string() })), (c) =>
  c.json({ title: c.req.valid("json").title, done: false }),
);

export type AppType = typeof routes;
```

```ts filename="cliente.ts"
import { hc } from "hono/client";
import type { AppType } from "./src/index";

const client = hc<AppType>("http://localhost:3000");
const todo = await (await client.todos.$post({ json: { title: "Write the docs" } })).json();
```

Una acción es la función del servidor y el cliente escrito en uno. Nexy escribe los tipos TypeScript de la firma Python:

```python filename="src/acciones/todos.py"
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
  const { run, data } = useAction(add_todo);
  return <button onClick={() => run({ title: "Write the docs" })}>{data?.title ?? "Add"}</button>;
}
```

## Pruebas con `app.request`

```ts filename="src/index.test.ts"
test("says hello", async () => {
  const res = await app.request("/api/hello");
  expect(await res.json()).toEqual({ message: "Hello" });
});
```

```python filename="pruebas/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## corriendo

| hono | nexy |
|---|---|
| `npm create hono@latest` | `nx new` |
| `bun run --hot src/index.ts` o `wrangler dev` | `nx dev` |
| `wrangler deploy` (Trabajadores) | `nx build`, luego `nx start` en un servidor o contenedor |
| `bun test` / `vitest` | `nx test` |

Nexy se ejecuta en un servidor Python, no en un tiempo de ejecución perimetral: consulte [Implementar](../deployment/README.md).

## Próximos pasos

- [De Express a Nexy](express.md)
- [De Elysia a Nexy](elysia.md)
- [Acciones](../guides/actions.md)
- [Controladores de ruta](../routing/fbr/handlers/README.md)
