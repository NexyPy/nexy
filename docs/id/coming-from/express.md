# Dari Ekspres hingga Nexy

Di Nexy, rute Ekspres menjadi file Python di bawah `src/routes/`: `app.get` adalah fungsi `GET`, `req` berubah menjadi parameter yang diketik, `res.json` menjadi nilai kembalian, dan `app.use` menjadi kolom konfigurasi atau `middleware.py`.

Setiap bagian di bawah menunjukkan kebiasaan Express, lalu hal yang sama di Nexy.

## Sebuah rute

```js filename="indeks.js"
import express from "express";

const app = express();

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello" });
});

app.listen(3000);
```

Jalur file adalah URL, nama fungsinya adalah metode, dan nilai yang dikembalikan adalah isi JSON:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `req.params`

```js filename="indeks.js"
app.get("/api/users/:id", (req, res) => {
  const id = Number(req.params.id);
  if (Number.isNaN(id)) return res.status(404).end();
  res.json({ id });
});
```

`:id` adalah segmen `[id]`, dan anotasi jenis melakukan konversi dan `404`:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

Wildcard `*` adalah file `[...rest].py`.

## `req.query`

```js filename="indeks.js"
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

`?page=abc` menjawab `422` dengan parameter yang gagal, bukan `NaN`.

## `req.body` dan validasi

```js filename="indeks.js"
import { z } from "zod";

app.use(express.json());

const NewItem = z.object({ name: z.string(), price: z.number().positive() });

app.post("/api/items", (req, res) => {
  const parsed = NewItem.safeParse(req.body);
  if (!parsed.success) return res.status(422).json(parsed.error);
  res.status(201).json(parsed.data);
});
```

Isinya diurai dan divalidasi terhadap model Pydantic sebelum fungsi berjalan:

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

```js filename="rute/admin.js"
const admin = express.Router();

admin.get("/stats", (req, res) => res.json({ users: 3 }));

app.use("/admin", admin);
```

Folder tersebut adalah jalur pemasangan:

```python filename="src/route/admin/stats.py"
async def GET():
    return {"users": 3}
```

## Middleware rute

```js filename="rute/admin.js"
function requireAdmin(req, res, next) {
  if (req.get("x-role") !== "admin") return res.status(403).json({ error: "Admins only" });
  next();
}

admin.use(requireAdmin);
```

`dependencies.py` berjalan sebelum setiap rute foldernya. Menaikkan akan menghentikan permintaan, seperti halnya tidak memanggil `next()`:

```python filename="src/rute/admin/dependensi.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `app.use` perangkat tengah

```js filename="indeks.js"
app.use((req, res, next) => {
  const start = Date.now();
  res.on("finish", () => console.log(req.method, req.url, Date.now() - start));
  next();
});
```

A `middleware.py` di root rute membungkus setiap permintaan; `call_next` adalah `next()`:

```python filename="src/rute/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## `cors`, `compression`, `helmet`host bergaya

```js filename="indeks.js"
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

## kue

```js filename="indeks.js"
import cookieParser from "cookie-parser";

app.use(cookieParser());

app.post("/api/theme", (req, res) => {
  res.cookie("theme", "dark").json({ theme: "dark" });
});

app.get("/api/theme", (req, res) => res.json({ theme: req.cookies.theme ?? "light" }));
```

Cookie adalah parameter untuk dibaca, dan metode respons untuk ditulis:

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

```js filename="indeks.js"
import session from "express-session";

app.use(session({ secret: "change-me" }));

app.post("/api/login", (req, res) => {
  req.session.user = req.body.name;
  res.json({ user: req.session.user });
});
```

`useSession` di `nexyconfig.py` (di atas) mengaktifkan sesi; `request.session` adalah dikt:

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

```js filename="indeks.js"
app.get("/old", (req, res) => res.redirect(301, "/new"));
```

```python filename="src/rute/lama.py"
from nexy.http import RedirectResponse


async def GET():
    return RedirectResponse("/new", status_code=301)
```

## Unggah file dengan `multer`

```js filename="indeks.js"
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

## Tampilan dengan EJS atau Pug

```js filename="indeks.js"
app.set("view engine", "ejs");

app.get("/users", (req, res) => {
  res.render("users", { users: [{ name: "Ada" }, { name: "Alan" }] });
});
```

```html filename="tampilan/pengguna.ejs"
<ul>
  <% users.forEach((user) => { %>
  <li><%= user.name %></li>
  <% }) %>
</ul>
```

Halaman `.nexy` adalah rute dan tampilan sekaligus:

```nexy filename="src/rute/pengguna.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

`<%= %>` lolos dan `{{ }}` tidak: lolos dari apa yang diketik pengunjung dengan `{{ value | e }}`.

## `express.static`

```js filename="indeks.js"
app.use(express.static("public"));
```

Tidak ada yang perlu ditulis: `public/` disajikan di `/`.

## Pengendali 404 dan pengendali kesalahan

```js filename="indeks.js"
app.use((req, res) => res.status(404).send("<h1>Not found</h1>"));

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send("<h1>Something broke</h1>");
});
```

Dua file di root rute. Klien API masih mendapatkan JSON, browser mendapatkan halaman:

```nexy filename="src/rute/tidak ditemukan.nexy"
<h1>Not found</h1>
```

```nexy filename="src/route/errors.nexy"
<h1>Something broke</h1>
```

## WebSockets dengan `ws`

```js filename="indeks.js"
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

## Tes dengan Jest dan Supertest

```js filename="indeks.test.js"
import request from "supertest";
import { app } from "./app.js";

test("hello", async () => {
  const res = await request(app).get("/api/hello");
  expect(res.body).toEqual({ message: "Hello" });
});
```

```python filename="tes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Berlari

| Ekspres | Nexy |
|---|---|
| `npm init` + `npm i express` | `nx new` |
| `nodemon index.js` | `nx dev` |
| `NODE_ENV=production node index.js` | `nx build`, lalu `nx start` |
| `npm test` | `nx test` |
| tidak ada dokumen API | `/docs`, mencantumkan setiap `.py` rute |

## Mempertahankan bagian depan React Anda

Jika aplikasi Express menyajikan React SPA, komponen akan berpindah ke `src/components/` dan dirender sebagai pulau pada halaman `.nexy`, atau seluruh situs berpindah ke perutean klien dengan `useCSR = True`. Lihat [Pulau](../rendering/islands.md) dan [CSR](../rendering/csr.md).

## Langkah selanjutnya

- [Berasal dari kerangka lain](../getting-started/coming-from-other-frameworks.md)
- [Pengendali rute](../routing/fbr/handlers/README.md)
- [File middleware](../routing/fbr/middleware/README.md)
- [Resep](../guides/recipes.md)
