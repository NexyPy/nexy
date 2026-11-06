# De l’Express à Nexy

Dans Nexy, une route Express devient un fichier Python sous `src/routes/` : `app.get` est une fonction `GET`, `req` se transforme en paramètres tapés, `res.json` en une valeur de retour et `app.use` en champs de configuration ou en `middleware.py`.

Chaque section ci-dessous montre une habitude Express, puis la même chose dans Nexy.

## Un itinéraire

```js filename="index.js"
import express from "express";

const app = express();

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello" });
});

app.listen(3000);
```

Le chemin du fichier est l'URL, le nom de la fonction est la méthode et la valeur renvoyée est le corps JSON :

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

`:id` est un segment `[id]`, et l'annotation de type effectue la conversion et le `404` :

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

Un caractère générique `*` est un fichier `[...rest].py`.

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

`?page=abc` répond à `422` avec le paramètre qui a échoué, au lieu de `NaN`.

## `req.body` et validation

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

Le corps est analysé et validé par rapport à un modèle Pydantic avant l'exécution de la fonction :

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

Le dossier est le chemin de montage :

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Middleware de routage

```js filename="routes/admin.js"
function requireAdmin(req, res, next) {
  if (req.get("x-role") !== "admin") return res.status(403).json({ error: "Admins only" });
  next();
}

admin.use(requireAdmin);
```

Un `dependencies.py` s'exécute avant chaque route de son dossier. L'augmentation arrête la demande, comme le fait de ne pas appeler `next()` :

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `app.use` intergiciel

```js filename="index.js"
app.use((req, res, next) => {
  const start = Date.now();
  res.on("finish", () => console.log(req.method, req.url, Date.now() - start));
  next();
});
```

Un `middleware.py` à la racine des routes enveloppe chaque requête ; `call_next` est `next()` :

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## Hôtes de style `cors`, `compression`, `helmet`

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

## Biscuits

```js filename="index.js"
import cookieParser from "cookie-parser";

app.use(cookieParser());

app.post("/api/theme", (req, res) => {
  res.cookie("theme", "dark").json({ theme: "dark" });
});

app.get("/api/theme", (req, res) => res.json({ theme: req.cookies.theme ?? "light" }));
```

Un cookie est un paramètre à lire, et une méthode de réponse à écrire :

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

`useSession` dans `nexyconfig.py` (ci-dessus) active les sessions ; `request.session` est un dicton :

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

## Téléchargements de fichiers avec `multer`

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

## Vues avec EJS ou Pug

```js filename="index.js"
app.set("view engine", "ejs");

app.get("/users", (req, res) => {
  res.render("users", { users: [{ name: "Ada" }, { name: "Alan" }] });
});
```

```html filename="vues/utilisateurs.ejs"
<ul>
  <% users.forEach((user) => { %>
  <li><%= user.name %></li>
  <% }) %>
</ul>
```

Une page `.nexy` est à la fois l'itinéraire et la vue :

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

`<%= %>` s'échappe et `{{ }}` ne le fait pas : échappe à ce qu'un visiteur a tapé avec `{{ value | e }}`.

## `express.static`

```js filename="index.js"
app.use(express.static("public"));
```

Rien à écrire : `public/` est servi à `/`.

## Le gestionnaire 404 et le gestionnaire d'erreurs

```js filename="index.js"
app.use((req, res) => res.status(404).send("<h1>Not found</h1>"));

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send("<h1>Something broke</h1>");
});
```

Deux fichiers à la racine des routes. Les clients API obtiennent toujours JSON, les navigateurs obtiennent la page :

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

```nexy filename="src/routes/erreurs.nexy"
<h1>Something broke</h1>
```

## WebSockets avec `ws`

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

## Tests avec Jest et Supertest

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

## Courir

| Exprimer | Nexy |
|---|---|
| `npm init` + `npm i express` | `nx new` |
| `nodemon index.js` | `nx dev` |
| `NODE_ENV=production node index.js` | `nx build`, puis `nx start` |
| `npm test` | `nx test` |
| pas de documentation API | `/docs`, répertoriant chaque `.py` itinéraire |

## Conserver votre frontal React

Si l'application Express dessert un SPA React, les composants sont déplacés vers `src/components/` et s'affichent sous forme d'îlots d'une page `.nexy`, ou l'ensemble du site passe au routage client avec `useCSR = True`. Voir [Îles](../rendering/islands.md) et [CSR](../rendering/csr.md).

## Prochaines étapes

- [Venant d'un autre cadre](../getting-started/coming-from-other-frameworks.md)
- [Gestionnaires de routes](../routing/fbr/handlers/README.md)
- [Fichiers middleware](../routing/fbr/middleware/README.md)
- [Recettes](../guides/recipes.md)
