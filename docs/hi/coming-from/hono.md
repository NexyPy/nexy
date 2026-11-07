# होनो से नेक्सी तक

नेक्सी में एक होनो रूट `src/routes/` के अंतर्गत एक Python फ़ाइल बन जाता है: `c.req` टाइप किए गए पैरामीटर में बदल जाता है, `zValidator` एक Pydantic मॉडल में, `app.route` एक फ़ोल्डर में, और `hc` आरपीसी क्लाइंट टाइप की गई क्रियाओं में बदल जाता है।

नीचे प्रत्येक अनुभाग एक होनो आदत दिखाता है, फिर नेक्सी में भी वही चीज़।

## एक मार्ग

```ts filename="src/index.ts"
import { Hono } from "hono";

const app = new Hono();

app.get("/api/hello", (c) => c.json({ message: "Hello" }));

export default app;
```

फ़ाइल पथ URL है, फ़ंक्शन नाम विधि है, और लौटाया गया `dict` `c.json` है:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `c.req.param` और `c.req.query`

```ts filename="src/index.ts"
app.get("/api/users/:id", (c) => {
  const id = Number(c.req.param("id"));
  const fields = c.req.query("fields");
  return c.json({ id, fields });
});
```

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` उत्तर `404`: `abc` एक `int` नहीं है।

## `zValidator`

```ts filename="src/index.ts"
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";

const NewItem = z.object({ name: z.string(), price: z.number().positive() });

app.post("/api/items", zValidator("json", NewItem), (c) => c.json(c.req.valid("json"), 201));
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

## `app.route` और `basePath`

```ts filename="src/admin.ts"
export const admin = new Hono();

admin.get("/stats", (c) => c.json({ users: 3 }));
```

```ts filename="src/index.ts"
app.route("/admin", admin);
```

फ़ोल्डर आधार पथ है:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## एक पथ पर मिडलवेयर

```ts filename="src/index.ts"
import { createMiddleware } from "hono/factory";
import { HTTPException } from "hono/http-exception";

const requireAdmin = createMiddleware(async (c, next) => {
  if (c.req.header("x-role") !== "admin") throw new HTTPException(403, { message: "Admins only" });
  await next();
});

app.use("/admin/*", requireAdmin);
```

`/admin/*` फ़ोल्डर है: एक `dependencies.py` इसके नीचे प्रत्येक मार्ग से पहले चलता है।

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## हर अनुरोध के आसपास मिडलवेयर

```ts filename="src/index.ts"
app.use("*", async (c, next) => {
  await next();
  c.header("x-app", "demo");
});
```

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `c.set` और `c.get`

```ts filename="src/index.ts"
app.use("/api/*", async (c, next) => {
  c.set("token", c.req.header("authorization")?.replace("Bearer ", ""));
  await next();
});

app.get("/api/whoami", (c) => c.json({ token: c.get("token") }));
```

हैंडलर के लिए गणना किया गया मान एक निर्भरता है, जिसे नाम से पूछा जाता है:

```python filename="src/routes/api/whoami.py"
from nexy.http import Depends, Header


def token(authorization: str = Header("")) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(token: str = Depends(token)):
    return {"token": token}
```

## अंतर्निर्मित मिडलवेयर

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

हेडर `secureHeaders` सेट में से, `nx start` अपने आप दो जोड़ता है: `X-Content-Type-Options` और `Referrer-Policy`। अन्य को, जैसे कि `Content-Security-Policy`, को `middleware.py` में सेट करें। [सुरक्षा](../reference/security.md) देखें।

## `c.html` और होनो जेएसएक्स

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

एक `.nexy` पृष्ठ सर्वर पर Python और Jinja2 से HTML प्रस्तुत करता है:

```nexy filename="src/routes/users.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

इंटरएक्टिव JSX JSX ही रहता है: एक React, Preact या Solid घटक पृष्ठ के एक द्वीप के रूप में प्रस्तुत होता है। देखें [द्वीप](../rendering/islands.md)।

## `c.redirect`

```ts filename="src/index.ts"
app.get("/old", (c) => c.redirect("/new", 301));
```

```python filename="src/routes/old.py"
from nexy.http import RedirectResponse


async def GET():
    return RedirectResponse("/new", status_code=301)
```

## कुकीज़

```ts filename="src/index.ts"
import { getCookie, setCookie } from "hono/cookie";

app.get("/api/theme", (c) => c.json({ theme: getCookie(c, "theme") ?? "light" }));
app.post("/api/theme", (c) => {
  setCookie(c, "theme", "dark");
  return c.json({ theme: "dark" });
});
```

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie, JSONResponse


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}


async def POST():
    response = JSONResponse({"theme": "dark"})
    response.set_cookie("theme", "dark")
    return response
```

## `HTTPException`, `notFound` और `onError`

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

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

## `serveStatic`

```ts filename="src/index.ts"
import { serveStatic } from "hono/bun";

app.use("/*", serveStatic({ root: "./public" }));
```

लिखने के लिए कुछ भी नहीं: `public/` `/` पर परोसा जाता है।

## वेबसॉकेट

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

```python filename="src/routes/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## `hc` आरपीसी क्लाइंट

```ts filename="src/index.ts"
const routes = app.post("/todos", zValidator("json", z.object({ title: z.string() })), (c) =>
  c.json({ title: c.req.valid("json").title, done: false }),
);

export type AppType = typeof routes;
```

```ts filename="client.ts"
import { hc } from "hono/client";
import type { AppType } from "./src/index";

const client = hc<AppType>("http://localhost:3000");
const todo = await (await client.todos.$post({ json: { title: "Write the docs" } })).json();
```

एक क्रिया सर्वर फ़ंक्शन और टाइप किया गया क्लाइंट एक में है। नेक्सी Python हस्ताक्षर से TypeScript प्रकार लिखता है:

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
  const { run, data } = useAction(add_todo);
  return <button onClick={() => run({ title: "Write the docs" })}>{data?.title ?? "Add"}</button>;
}
```

## `app.request` के साथ परीक्षण

```ts filename="src/index.test.ts"
test("says hello", async () => {
  const res = await app.request("/api/hello");
  expect(await res.json()).toEqual({ message: "Hello" });
});
```

```python filename="परीक्षण/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## चल रहा है

| होनो | नेक्सी |
|---|---|
| `npm create hono@latest` | `nx new` |
| `bun run --hot src/index.ts` या `wrangler dev` | `nx dev` |
| `wrangler deploy` (श्रमिक) | `nx build`, फिर `nx start` किसी सर्वर या कंटेनर पर |
| `bun test` / `vitest` | `nx test` |

नेक्सी एक Python सर्वर पर चलता है, एज रनटाइम पर नहीं: [परिनियोजन](../deployment/README.md) देखें।

## अगले चरण

- [एक्सप्रेस से नेक्सी तक](express.md)
- [एलिसिया से नेक्सी तक](elysia.md)
- [क्रियाएँ](../guides/actions.md)
- [मार्ग संचालक](../routing/fbr/handlers/README.md)
