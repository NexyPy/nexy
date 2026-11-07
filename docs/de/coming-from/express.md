# Von Express bis Nexy

In Nexy wird eine Express-Route zu einer Python-Datei unter `src/routes/`: `app.get` ist eine `GET`-Funktion, `req` wird zu typisierten Parametern, `res.json` zu einem Rückgabewert und `app.use` zu Konfigurationsfeldern oder einem `middleware.py`.

Jeder Abschnitt unten zeigt eine Express-Gewohnheit, dann dasselbe in Nexy.

## Eine Route

```js filename="index.js"
import express from "express";

const app = express();

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello" });
});

app.listen(3000);
```

Der Dateipfad ist die URL, der Funktionsname ist die Methode und der zurückgegebene Wert ist der JSON-Body:

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

`:id` ist ein `[id]`-Segment, und die Typanmerkung übernimmt die Konvertierung und `404`:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

Ein `*`-Platzhalter ist eine `[...rest].py`-Datei.

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

`?page=abc` antwortet `422` mit dem Parameter, der fehlgeschlagen ist, anstelle von `NaN`.

## `req.body` und Validierung

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

Der Körper wird analysiert und anhand eines Pydantic-Modells validiert, bevor die Funktion ausgeführt wird:

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

```js filename="Routen/admin.js"
const admin = express.Router();

admin.get("/stats", (req, res) => res.json({ users: 3 }));

app.use("/admin", admin);
```

Der Ordner ist der Mount-Pfad:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Route-Middleware

```js filename="Routen/admin.js"
function requireAdmin(req, res, next) {
  if (req.get("x-role") !== "admin") return res.status(403).json({ error: "Admins only" });
  next();
}

admin.use(requireAdmin);
```

Ein `dependencies.py` wird vor jeder Route seines Ordners ausgeführt. Das Erhöhen stoppt die Anfrage, da das Nichtaufrufen von `next()` Folgendes bewirkt:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `app.use` Middleware

```js filename="index.js"
app.use((req, res, next) => {
  const start = Date.now();
  res.on("finish", () => console.log(req.method, req.url, Date.now() - start));
  next();
});
```

Ein `middleware.py` am Routenstamm umschließt jede Anfrage; `call_next` ist `next()`:

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## `cors`-, `compression`-, `helmet`-artige Hosts

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

## Kekse

```js filename="index.js"
import cookieParser from "cookie-parser";

app.use(cookieParser());

app.post("/api/theme", (req, res) => {
  res.cookie("theme", "dark").json({ theme: "dark" });
});

app.get("/api/theme", (req, res) => res.json({ theme: req.cookies.theme ?? "light" }));
```

Ein Cookie ist ein zu lesender Parameter und eine zu schreibende Antwortmethode:

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

`useSession` in `nexyconfig.py` (oben) schaltet Sitzungen ein; `request.session` ist ein Diktat:

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

## Datei-Uploads mit `multer`

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

## Ansichten mit EJS oder Pug

```js filename="index.js"
app.set("view engine", "ejs");

app.get("/users", (req, res) => {
  res.render("users", { users: [{ name: "Ada" }, { name: "Alan" }] });
});
```

```html filename="view/users.ejs"
<ul>
  <% users.forEach((user) => { %>
  <li><%= user.name %></li>
  <% }) %>
</ul>
```

Eine `.nexy`-Seite ist Route und Ansicht zugleich:

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

`<%= %>` entgeht und `{{ }}` nicht: entkommt, was ein Besucher mit `{{ value | e }}` eingegeben hat.

## `express.static`

```js filename="index.js"
app.use(express.static("public"));
```

Nichts zu schreiben: `public/` wird um `/` serviert.

## Der 404-Handler und der Fehlerhandler

```js filename="index.js"
app.use((req, res) => res.status(404).send("<h1>Not found</h1>"));

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send("<h1>Something broke</h1>");
});
```

Zwei Dateien im Routenstammverzeichnis. API-Clients erhalten weiterhin JSON, Browser erhalten die Seite:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

```nexy filename="src/routes/errors.nexy"
<h1>Something broke</h1>
```

## WebSockets mit `ws`

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

## Tests mit Jest und Supertest

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

## Laufen

| Express | Nexy |
|---|---|
| `npm init` + `npm i express` | `nx new` |
| `nodemon index.js` | `nx dev` |
| `NODE_ENV=production node index.js` | `nx build`, dann `nx start` |
| `npm test` | `nx test` |
| Keine API-Dokumente | `/docs`, Auflistung aller `.py` Routen |

## Behalten Sie Ihr React Frontend

Wenn die Express-App eine React SPA bereitstellt, werden die Komponenten nach `src/components/` verschoben und als Inseln einer `.nexy`-Seite gerendert, oder die gesamte Site wechselt mit `useCSR = True` zum Client-Routing. Siehe [Inseln](../rendering/islands.md) und [CSR](../rendering/csr.md).

## Nächste Schritte

- [Aus einem anderen Rahmen kommend](../getting-started/coming-from-other-frameworks.md)
- [Routenhandler](../routing/fbr/handlers/README.md)
- [Middleware-Dateien](../routing/fbr/middleware/README.md)
- [Rezepte](../guides/recipes.md)
