# D’Elysia à Nexy

Dans Nexy, une route Elysia devient un fichier Python sous `src/routes/` : les schémas `t.Object` deviennent des modèles Pydantic, `.group` devient un dossier, `beforeHandle` un `dependencies.py`, et le client typé d'Eden devient des actions typées.

Chaque section ci-dessous montre une habitude d'Elysia, puis la même chose chez Nexy.

## Un itinéraire

```ts filename="src/index.ts"
import { Elysia } from "elysia";

new Elysia().get("/api/hello", () => ({ message: "Hello" })).listen(3000);
```

Le chemin du fichier est l'URL, le nom de la fonction est la méthode :

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Paramètres et requête avec `t`

```ts filename="src/index.ts"
import { Elysia, t } from "elysia";

new Elysia().get("/api/users/:id", ({ params, query }) => ({ id: params.id, fields: query.fields }), {
  params: t.Object({ id: t.Numeric() }),
  query: t.Object({ fields: t.Optional(t.String()) }),
});
```

Les types vont sur les paramètres, et `:id` est un segment `[id]` :

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## Un corps avec `t.Object`

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

## `response` schémas

```ts filename="src/index.ts"
app.get("/api/me", () => ({ name: "Ada" }), {
  response: t.Object({ name: t.String() }),
});
```

Le type de retour est le schéma de réponse : les champs non déclarés sont exclus de la réponse.

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

Le dossier est le groupe :

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `beforeHandle` et `guard`

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

Un `dependencies.py` garde chaque itinéraire de son dossier :

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `derive`, `decorate` et `state`

```ts filename="src/index.ts"
app
  .derive(({ headers }) => ({ token: headers.authorization?.replace("Bearer ", "") }))
  .get("/api/whoami", ({ token }) => ({ token }));
```

Ce que `derive` ajoute au contexte est une dépendance demandée par le gestionnaire :

```python filename="src/routes/api/whoami.py"
from nexy.http import Depends, Header


def token(authorization: str = Header("")) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(token: str = Depends(token)):
    return {"token": token}
```

`decorate` et `state` sont des objets simples au niveau du module, importés là où ils sont nécessaires.

## `onAfterHandle` et `mapResponse`

```ts filename="src/index.ts"
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

## `error()` et `onError`

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

Un `notfound.nexy` à la racine des routes répond aux navigateurs sur une URL inconnue.

## Biscuits

```ts filename="src/index.ts"
app.get("/api/theme", ({ cookie: { theme } }) => ({ theme: theme.value ?? "light" }));
```

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## Traité d'Eden

```ts filename="src/index.ts"
const app = new Elysia().post("/todos", ({ body }) => ({ title: body.title, done: false }), {
  body: t.Object({ title: t.String() }),
});

export type App = typeof app;
```

```ts filename="client.ts"
import { treaty } from "@elysiajs/eden";
import type { App } from "./src/index";

const api = treaty<App>("localhost:3000");
const { data } = await api.todos.post({ title: "Write the docs" });
```

Une action est à la fois la fonction Python et son client typé. Nexy génère les types TypeScript à partir de la signature Python :

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

Voir [Actions](../guides/actions.md).

## Plugins : `cors`, `swagger`, `static`

```ts filename="src/index.ts"
import { cors } from "@elysiajs/cors";
import { staticPlugin } from "@elysiajs/static";
import { swagger } from "@elysiajs/swagger";

app.use(cors({ origin: "https://example.com" })).use(swagger()).use(staticPlugin());
```

| Plugin Elysia | Nexy |
|---|---|
| `@elysiajs/cors` | `useCORS = {"allow_origins": [...]}` dans `nexyconfig.py` |
| `@elysiajs/swagger` | rien : `/docs` est activé par défaut |
| `@elysiajs/static` | rien : `public/` est servi à `/` |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## WebSockets

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

## Tests avec `app.handle`

```ts filename="test/index.test.ts"
import { describe, expect, it } from "bun:test";

it("says hello", async () => {
  const response = await app.handle(new Request("http://localhost/api/hello"));
  expect(await response.json()).toEqual({ message: "Hello" });
});
```

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Courir

| Élysie | Nexy |
|---|---|
| `bun create elysia app` | `nx new` |
| `bun dev` | `nx dev` |
| `bun build --compile` | `nx build`, puis `nx start` |
| `bun test` | `nx test` |

Nexy fonctionne sur Python. Node n'est nécessaire que lorsque le projet comporte des composants clients : Vite les construit et `nx start` s'exécute sans lui.

## Prochaines étapes

- [De l’Express à Nexy](express.md)
- [De Fastify à Nexy](fastify.md)
- [Actions](../guides/actions.md)
- [Gestionnaires de routes](../routing/fbr/handlers/README.md)
