# एलिसिया से नेक्सी तक

नेक्सी में एक एलिसिया मार्ग `src/routes/` के अंतर्गत एक Python फ़ाइल बन जाता है: `t.Object` स्कीमा Pydantic मॉडल बन जाता है, `.group` एक फ़ोल्डर बन जाता है, `beforeHandle` एक `dependencies.py`, और ईडन का टाइप किया गया क्लाइंट टाइप की गई क्रियाएं बन जाता है।

नीचे प्रत्येक अनुभाग एलिसिया की आदत दिखाता है, फिर नेक्सी में भी यही चीज़।

## एक मार्ग

```ts filename="src/index.ts"
import { Elysia } from "elysia";

new Elysia().get("/api/hello", () => ({ message: "Hello" })).listen(3000);
```

फ़ाइल पथ URL है, फ़ंक्शन नाम विधि है:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `t` के साथ पैरामीटर और क्वेरी

```ts filename="src/index.ts"
import { Elysia, t } from "elysia";

new Elysia().get("/api/users/:id", ({ params, query }) => ({ id: params.id, fields: query.fields }), {
  params: t.Object({ id: t.Numeric() }),
  query: t.Object({ fields: t.Optional(t.String()) }),
});
```

प्रकार पैरामीटर पर चलते हैं, और `:id` एक `[id]` खंड है:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## `t.Object` वाला एक शरीर

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

## `response` स्कीमा

```ts filename="src/index.ts"
app.get("/api/me", () => ({ name: "Ada" }), {
  response: t.Object({ name: t.String() }),
});
```

रिटर्न प्रकार प्रतिक्रिया स्कीमा है: अघोषित फ़ील्ड उत्तर से बाहर रह जाते हैं।

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

फ़ोल्डर समूह है:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `beforeHandle` और `guard`

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

एक `dependencies.py` अपने फ़ोल्डर के हर रूट की सुरक्षा करता है:

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `derive`, `decorate` और `state`

```ts filename="src/index.ts"
app
  .derive(({ headers }) => ({ token: headers.authorization?.replace("Bearer ", "") }))
  .get("/api/whoami", ({ token }) => ({ token }));
```

`derive` संदर्भ में जो जोड़ता है वह एक निर्भरता है, जो हैंडलर द्वारा मांगी गई है:

```python filename="src/routes/api/whoami.py"
from nexy.http import Depends, Header


def token(authorization: str = Header("")) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(token: str = Depends(token)):
    return {"token": token}
```

`decorate` और `state` सादे मॉड्यूल-स्तरीय ऑब्जेक्ट हैं, जहां उनकी आवश्यकता होती है वहां आयात किया जाता है।

## `onAfterHandle` और `mapResponse`

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

## `error()` और `onError`

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

रूट रूट पर एक `notfound.nexy` एक अज्ञात यूआरएल पर ब्राउज़र का उत्तर देता है।

## कुकीज़

```ts filename="src/index.ts"
app.get("/api/theme", ({ cookie: { theme } }) => ({ theme: theme.value ?? "light" }));
```

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## ईडन संधि

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

एक क्रिया एक ही समय में Python फ़ंक्शन और उसका टाइप किया गया क्लाइंट है। नेक्सी Python हस्ताक्षर से TypeScript प्रकार उत्पन्न करता है:

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

[क्रियाएँ](../guides/actions.md) देखें।

## प्लगइन्स: `cors`, `swagger`, `static`

```ts filename="src/index.ts"
import { cors } from "@elysiajs/cors";
import { staticPlugin } from "@elysiajs/static";
import { swagger } from "@elysiajs/swagger";

app.use(cors({ origin: "https://example.com" })).use(swagger()).use(staticPlugin());
```

| एलिसिया प्लगइन | नेक्सी |
|---|---|
| `@elysiajs/cors` | `useCORS = {"allow_origins": [...]}` में `nexyconfig.py` |
| `@elysiajs/swagger` | कुछ नहीं: `/docs` डिफ़ॉल्ट रूप से चालू है |
| `@elysiajs/static` | कुछ भी नहीं: `public/` `/` पर परोसा जाता है |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## वेबसॉकेट

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

## `app.handle` के साथ परीक्षण

```ts filename="test/index.test.ts"
import { describe, expect, it } from "bun:test";

it("says hello", async () => {
  const response = await app.handle(new Request("http://localhost/api/hello"));
  expect(await response.json()).toEqual({ message: "Hello" });
});
```

```python filename="परीक्षण/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## चल रहा है

| एलिसिया | नेक्सी |
|---|---|
| `bun create elysia app` | `nx new` |
| `bun dev` | `nx dev` |
| `bun build --compile` | `nx build`, फिर `nx start` |
| `bun test` | `nx test` |

नेक्सी Python पर चलती है। नोड की आवश्यकता केवल तभी होती है जब प्रोजेक्ट में क्लाइंट घटक होते हैं: Vite उन्हें बनाता है, और `nx start` इसके बिना चलता है।

## अगले चरण

- [एक्सप्रेस से नेक्सी तक](express.md)
- [फास्टिफाइ से नेक्सी तक](fastify.md)
- [क्रियाएँ](../guides/actions.md)
- [मार्ग संचालक](../routing/fbr/handlers/README.md)
