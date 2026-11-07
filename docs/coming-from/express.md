# From Express to Nexy

In Nexy an Express route becomes a Python file under `src/routes/`: `app.get` is a `GET` function,
`req` turns into typed parameters, `res.json` into a return value, and `app.use` into config fields
or a `middleware.py`.

Each section below shows an Express habit, then the same thing in Nexy.

## A route

```js filename="index.js"
import express from "express";

const app = express();

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello" });
});

app.listen(3000);
```

The file path is the URL, the function name is the method, and the returned value is the JSON body:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `req.params`

```js filename="index.js"
app.get("/api/users/:id", (req, res) => {
  const id = Number(req.params.id);
  if (Number.isNaN(id)) return res.status(404).end();
  res.json({ id });
});
```

`:id` is a `[id]` segment, and the type annotation does the conversion and the `404`:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

A `*` wildcard is a `[...rest].py` file.

## `req.query`

```js filename="index.js"
app.get("/api/search", (req, res) => {
  const q = req.query.q ?? "";
  const page = Number(req.query.page ?? 1);
  res.json({ q, page });
});
```

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

`?page=abc` answers `422` with the parameter that failed, instead of `NaN`.

## `req.body` and validation

```js filename="index.js"
import { z } from "zod";

app.use(express.json());

const NewItem = z.object({ name: z.string(), price: z.number().positive() });

app.post("/api/items", (req, res) => {
  const parsed = NewItem.safeParse(req.body);
  if (!parsed.success) return res.status(422).json(parsed.error);
  res.status(201).json(parsed.data);
});
```

The body is parsed and validated against a Pydantic model before the function runs:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## `express.Router()`

```js filename="routes/admin.js"
const admin = express.Router();

admin.get("/stats", (req, res) => res.json({ users: 3 }));

app.use("/admin", admin);
```

The folder is the mount path:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Route middleware

```js filename="routes/admin.js"
function requireAdmin(req, res, next) {
  if (req.get("x-role") !== "admin") return res.status(403).json({ error: "Admins only" });
  next();
}

admin.use(requireAdmin);
```

A `dependencies.py` runs before every route of its folder. Raising stops the request, as not
calling `next()` does:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `app.use` middleware

```js filename="index.js"
app.use((req, res, next) => {
  const start = Date.now();
  res.on("finish", () => console.log(req.method, req.url, Date.now() - start));
  next();
});
```

A `middleware.py` at the routes root wraps every request; `call_next` is `next()`:

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## `cors`, `compression`, `helmet`-style hosts

```js filename="index.js"
import compression from "compression";
import cors from "cors";

app.use(cors({ origin: "https://example.com" }));
app.use(compression());
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
    useTrustedHost = {"allowed_hosts": ["example.com", "*.example.com"]}
    useSession = {"secret_key": "change-me"}
```

## Cookies

```js filename="index.js"
import cookieParser from "cookie-parser";

app.use(cookieParser());

app.post("/api/theme", (req, res) => {
  res.cookie("theme", "dark").json({ theme: "dark" });
});

app.get("/api/theme", (req, res) => res.json({ theme: req.cookies.theme ?? "light" }));
```

A cookie is a parameter to read, and a method of the response to write:

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie, JSONResponse


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}


async def POST():
    response = JSONResponse({"theme": "dark"})
    response.set_cookie("theme", "dark")
    return response
```

## `express-session`

```js filename="index.js"
import session from "express-session";

app.use(session({ secret: "change-me" }));

app.post("/api/login", (req, res) => {
  req.session.user = req.body.name;
  res.json({ user: req.session.user });
});
```

`useSession` in `nexyconfig.py` (above) switches sessions on; `request.session` is a dict:

```python filename="src/routes/api/login.py"
from pydantic import BaseModel

from nexy.http import Request


class Login(BaseModel):
    name: str


async def POST(request: Request, body: Login):
    request.session["user"] = body.name
    return {"user": body.name}
```

## `res.redirect`

```js filename="index.js"
app.get("/old", (req, res) => res.redirect(301, "/new"));
```

```python filename="src/routes/old.py"
from nexy.http import RedirectResponse


async def GET():
    return RedirectResponse("/new", status_code=301)
```

## File uploads with `multer`

```js filename="index.js"
import multer from "multer";

const upload = multer({ limits: { fileSize: 1_000_000 } });

app.post("/api/upload", upload.single("file"), (req, res) => {
  res.json({ name: req.file.originalname, size: req.file.size });
});
```

```python filename="src/routes/api/upload.py"
from nexy.http import HTTPException, UploadFile


async def POST(file: UploadFile):
    data = await file.read()
    if len(data) > 1_000_000:
        raise HTTPException(status_code=413, detail="File too large")
    return {"name": file.filename, "size": len(data)}
```

## Views with EJS or Pug

```js filename="index.js"
app.set("view engine", "ejs");

app.get("/users", (req, res) => {
  res.render("users", { users: [{ name: "Ada" }, { name: "Alan" }] });
});
```

```html filename="views/users.ejs"
<ul>
  <% users.forEach((user) => { %>
  <li><%= user.name %></li>
  <% }) %>
</ul>
```

A `.nexy` page is the route and the view at once:

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

`<%= %>` escapes and `{{ }}` does not: escape what a visitor typed with `{{ value | e }}`.

## `express.static`

```js filename="index.js"
app.use(express.static("public"));
```

Nothing to write: `public/` is served at `/`.

## The 404 handler and the error handler

```js filename="index.js"
app.use((req, res) => res.status(404).send("<h1>Not found</h1>"));

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send("<h1>Something broke</h1>");
});
```

Two files at the routes root. API clients still get JSON, browsers get the page:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

```nexy filename="src/routes/errors.nexy"
<h1>Something broke</h1>
```

## WebSockets with `ws`

```js filename="index.js"
import { WebSocketServer } from "ws";

const wss = new WebSocketServer({ server, path: "/ws/echo" });
wss.on("connection", (socket) => socket.on("message", (data) => socket.send(data)));
```

```python filename="src/routes/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## Tests with Jest and Supertest

```js filename="index.test.js"
import request from "supertest";
import { app } from "./app.js";

test("hello", async () => {
  const res = await request(app).get("/api/hello");
  expect(res.body).toEqual({ message: "Hello" });
});
```

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Running

| Express | Nexy |
|---|---|
| `npm init` + `npm i express` | `nx new` |
| `nodemon index.js` | `nx dev` |
| `NODE_ENV=production node index.js` | `nx build`, then `nx start` |
| `npm test` | `nx test` |
| no API docs | `/docs`, listing every `.py` route |

## Keeping your React front end

If the Express app served a React SPA, the components move to `src/components/` and render as
islands of a `.nexy` page, or the whole site moves to client routing with `useCSR = True`. See
[Islands](../rendering/islands.md) and [CSR](../rendering/csr.md).

## Next steps

- [Coming from another framework](../getting-started/coming-from-other-frameworks.md)
- [Route handlers](../routing/fbr/handlers/README.md)
- [Middleware files](../routing/fbr/middleware/README.md)
- [Recipes](../guides/recipes.md)
