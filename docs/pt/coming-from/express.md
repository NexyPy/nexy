# Do Expresso ao Nexy

No Nexy, uma rota Express se torna um arquivo Python em `src/routes/`: `app.get` é uma função `GET`, `req` se transforma em parâmetros digitados, `res.json` em um valor de retorno e `app.use` em campos de configuração ou um `middleware.py`.

Cada seção abaixo mostra um hábito Express e a mesma coisa no Nexy.

## Uma rota

```js filename="index.js"
import express from "express";

const app = express();

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello" });
});

app.listen(3000);
```

O caminho do arquivo é a URL, o nome da função é o método e o valor retornado é o corpo JSON:

```python filename="src/rotas/api/hello.py"
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

`:id` é um segmento `[id]`, e a anotação de tipo faz a conversão e o `404`:

```python filename="src/rotas/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

Um curinga `*` é um arquivo `[...rest].py`.

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

`?page=abc` responde `422` com o parâmetro que falhou, em vez de `NaN`.

## `req.body` e validação

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

O corpo é analisado e validado em um modelo Pydantic antes da função ser executada:

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

```js filename="rotas/admin.js"
const admin = express.Router();

admin.get("/stats", (req, res) => res.json({ users: 3 }));

app.use("/admin", admin);
```

A pasta é o caminho de montagem:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Middleware de rota

```js filename="rotas/admin.js"
function requireAdmin(req, res, next) {
  if (req.get("x-role") !== "admin") return res.status(403).json({ error: "Admins only" });
  next();
}

admin.use(requireAdmin);
```

Um `dependencies.py` é executado antes de cada rota de sua pasta. Aumentar interrompe a solicitação, assim como não chamar `next()` faz:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `app.use` intermediário

```js filename="index.js"
app.use((req, res, next) => {
  const start = Date.now();
  res.on("finish", () => console.log(req.method, req.url, Date.now() - start));
  next();
});
```

Um `middleware.py` na raiz das rotas envolve todas as solicitações; `call_next` é `next()`:

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## `cors`, `compression`, `helmet` hosts estilo

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

## Biscoitos

```js filename="index.js"
import cookieParser from "cookie-parser";

app.use(cookieParser());

app.post("/api/theme", (req, res) => {
  res.cookie("theme", "dark").json({ theme: "dark" });
});

app.get("/api/theme", (req, res) => res.json({ theme: req.cookies.theme ?? "light" }));
```

Um cookie é um parâmetro para ler e um método de resposta para escrever:

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

`useSession` em `nexyconfig.py` (acima) ativa as sessões; `request.session` é um ditado:

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

```python filename="src/rotas/old.py"
from nexy.http import RedirectResponse


async def GET():
    return RedirectResponse("/new", status_code=301)
```

## Uploads de arquivos com `multer`

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

## Visualizações com EJS ou Pug

```js filename="index.js"
app.set("view engine", "ejs");

app.get("/users", (req, res) => {
  res.render("users", { users: [{ name: "Ada" }, { name: "Alan" }] });
});
```

```html filename="visualizações/usuários.ejs"
<ul>
  <% users.forEach((user) => { %>
  <li><%= user.name %></li>
  <% }) %>
</ul>
```

Uma página `.nexy` é a rota e a visualização ao mesmo tempo:

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

`<%= %>` escapa e `{{ }}` não: escapa o que um visitante digitou com `{{ value | e }}`.

## `express.static`

```js filename="index.js"
app.use(express.static("public"));
```

Nada a escrever: `public/` é servido em `/`.

## O manipulador 404 e o manipulador de erros

```js filename="index.js"
app.use((req, res) => res.status(404).send("<h1>Not found</h1>"));

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send("<h1>Something broke</h1>");
});
```

Dois arquivos na raiz das rotas. Os clientes da API ainda recebem JSON, os navegadores obtêm a página:

```nexy filename="src/rotas/notfound.nexy"
<h1>Not found</h1>
```

```nexy filename="src/rotas/errors.nexy"
<h1>Something broke</h1>
```

## WebSockets com `ws`

```js filename="index.js"
import { WebSocketServer } from "ws";

const wss = new WebSocketServer({ server, path: "/ws/echo" });
wss.on("connection", (socket) => socket.on("message", (data) => socket.send(data)));
```

```python filename="src/rotas/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## Testes com Jest e Supertest

```js filename="index.test.js"
import request from "supertest";
import { app } from "./app.js";

test("hello", async () => {
  const res = await request(app).get("/api/hello");
  expect(res.body).toEqual({ message: "Hello" });
});
```

```python filename="testes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Correndo

| Expresso | Nexy |
|---|---|
| `npm init` + `npm i express` | `nx new` |
| `nodemon index.js` | `nx dev` |
| `NODE_ENV=production node index.js` | `nx build`, então `nx start` |
| `npm test` | `nx test` |
| sem documentos de API | `/docs`, listando todas as `.py` rotas |

## Mantendo seu React front-end

Se o aplicativo Express atendeu um React SPA, os componentes são movidos para `src/components/` e renderizados como ilhas de uma página `.nexy`, ou todo o site é movido para o roteamento do cliente com `useCSR = True`. Veja [Ilhas](../rendering/islands.md) e [CSR](../rendering/csr.md).

## Próximas etapas

- [Vindo de outra estrutura](../getting-started/coming-from-other-frameworks.md)
- [Manipuladores de rota](../routing/fbr/handlers/README.md)
- [Arquivos de middleware](../routing/fbr/middleware/README.md)
- [Receitas](../guides/recipes.md)
