# De Express a Nexy

En Nexy, una ruta Express se convierte en un archivo Python en `src/routes/`: `app.get` es una función `GET`, `req` se convierte en parámetros escritos, `res.json` en un valor de retorno y `app.use` en campos de configuración o un `middleware.py`.

Cada sección a continuación muestra un hábito Express, luego lo mismo en Nexy.

## una ruta

```js filename="index.js"
import express from "express";

const app = express();

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello" });
});

app.listen(3000);
```

La ruta del archivo es la URL, el nombre de la función es el método y el valor devuelto es el cuerpo JSON:

```python filename="src/rutas/api/hola.py"
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

`:id` es un segmento `[id]`, y la anotación de tipo realiza la conversión y el `404`:

```python filename="src/rutas/api/usuarios/[id].py"
async def GET(id: int):
    return {"id": id}
```

Un comodín `*` es un archivo `[...rest].py`.

## `req.query`

```js filename="index.js"
app.get("/api/search", (req, res) => {
  const q = req.query.q ?? "";
  const page = Number(req.query.page ?? 1);
  res.json({ q, page });
});
```

```python filename="src/rutas/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

`?page=abc` responde a `422` con el parámetro que falló, en lugar de `NaN`.

## `req.body` y validación

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

El cuerpo se analiza y valida con un modelo Pydantic antes de que se ejecute la función:

```python filename="src/rutas/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## `express.Router()`

```js filename="rutas/admin.js"
const admin = express.Router();

admin.get("/stats", (req, res) => res.json({ users: 3 }));

app.use("/admin", admin);
```

La carpeta es la ruta de montaje:

```python filename="src/rutas/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Middleware de ruta

```js filename="rutas/admin.js"
function requireAdmin(req, res, next) {
  if (req.get("x-role") !== "admin") return res.status(403).json({ error: "Admins only" });
  next();
}

admin.use(requireAdmin);
```

Un `dependencies.py` se ejecuta antes de cada ruta de su carpeta. Aumentar detiene la solicitud, al igual que no llamar a `next()`:

```python filename="src/rutas/admin/dependencias.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `app.use` software intermedio

```js filename="index.js"
app.use((req, res, next) => {
  const start = Date.now();
  res.on("finish", () => console.log(req.method, req.url, Date.now() - start));
  next();
});
```

Un `middleware.py` en la raíz de las rutas envuelve cada solicitud; `call_next` es `next()`:

```python filename="src/rutas/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## Presentadores de estilo `cors`, `compression`, `helmet`

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

## galletas

```js filename="index.js"
import cookieParser from "cookie-parser";

app.use(cookieParser());

app.post("/api/theme", (req, res) => {
  res.cookie("theme", "dark").json({ theme: "dark" });
});

app.get("/api/theme", (req, res) => res.json({ theme: req.cookies.theme ?? "light" }));
```

Una cookie es un parámetro para leer y un método de respuesta para escribir:

```python filename="src/rutas/api/theme.py"
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

`useSession` en `nexyconfig.py` (arriba) activa las sesiones; `request.session` es un dictado:

```python filename="src/rutas/api/login.py"
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

```python filename="src/rutas/old.py"
from nexy.http import RedirectResponse


async def GET():
    return RedirectResponse("/new", status_code=301)
```

## Carga de archivos con `multer`

```js filename="index.js"
import multer from "multer";

const upload = multer({ limits: { fileSize: 1_000_000 } });

app.post("/api/upload", upload.single("file"), (req, res) => {
  res.json({ name: req.file.originalname, size: req.file.size });
});
```

```python filename="src/rutas/api/upload.py"
from nexy.http import HTTPException, UploadFile


async def POST(file: UploadFile):
    data = await file.read()
    if len(data) > 1_000_000:
        raise HTTPException(status_code=413, detail="File too large")
    return {"name": file.filename, "size": len(data)}
```

## Vistas con EJS o Pug

```js filename="index.js"
app.set("view engine", "ejs");

app.get("/users", (req, res) => {
  res.render("users", { users: [{ name: "Ada" }, { name: "Alan" }] });
});
```

```html filename="vistas/usuarios.ejs"
<ul>
  <% users.forEach((user) => { %>
  <li><%= user.name %></li>
  <% }) %>
</ul>
```

Una página `.nexy` es la ruta y la vista a la vez:

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

`<%= %>` escapa y `{{ }}` no: escapa de lo que un visitante escribió con `{{ value | e }}`.

## `express.static`

```js filename="index.js"
app.use(express.static("public"));
```

Nada que escribir: `public/` se sirve en `/`.

## El controlador 404 y el controlador de errores.

```js filename="index.js"
app.use((req, res) => res.status(404).send("<h1>Not found</h1>"));

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send("<h1>Something broke</h1>");
});
```

Dos archivos en la raíz de las rutas. Los clientes API todavía obtienen JSON, los navegadores obtienen la página:

```nexy filename="src/rutas/notfound.nexy"
<h1>Not found</h1>
```

```nexy filename="src/rutas/errores.nexy"
<h1>Something broke</h1>
```

## WebSockets con `ws`

```js filename="index.js"
import { WebSocketServer } from "ws";

const wss = new WebSocketServer({ server, path: "/ws/echo" });
wss.on("connection", (socket) => socket.on("message", (data) => socket.send(data)));
```

```python filename="src/rutas/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## Pruebas con Jest y Supertest

```js filename="index.prueba.js"
import request from "supertest";
import { app } from "./app.js";

test("hello", async () => {
  const res = await request(app).get("/api/hello");
  expect(res.body).toEqual({ message: "Hello" });
});
```

```python filename="pruebas/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## corriendo

| expreso | nexy |
|---|---|
| `npm init` + `npm i express` | `nx new` |
| `nodemon index.js` | `nx dev` |
| `NODE_ENV=production node index.js` | `nx build`, luego `nx start` |
| `npm test` | `nx test` |
| sin documentos API | `/docs`, enumerando cada `.py` ruta |

## Manteniendo su React interfaz

Si la aplicación Express sirvió un React SPA, los componentes se mueven a `src/components/` y se representan como islas de una página `.nexy`, o todo el sitio se mueve al enrutamiento del cliente con `useCSR = True`. Ver [Islas](../rendering/islands.md) y [RSE](../rendering/csr.md).

## Próximos pasos

- [Procedente de otro marco](../getting-started/coming-from-other-frameworks.md)
- [Controladores de ruta](../routing/fbr/handlers/README.md)
- [Archivos de middleware](../routing/fbr/middleware/README.md)
- [Recetas](../guides/recipes.md)
