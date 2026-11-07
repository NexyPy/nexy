# এক্সপ্রেস থেকে নেক্সি পর্যন্ত

নেক্সিতে একটি এক্সপ্রেস রুট `src/routes/` এর অধীনে একটি Python ফাইল হয়ে যায়: `app.get` একটি `GET` ফাংশন, `req` টাইপ করা প্যারামিটারে পরিণত হয়, `res.json` একটি রিটার্ন মান এবং `app.use` কনফিগার ক্ষেত্র বা `middleware.py`।

নীচের প্রতিটি বিভাগ একটি এক্সপ্রেস অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস।

## একটি রুট

```js filename="index.js"
import express from "express";

const app = express();

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello" });
});

app.listen(3000);
```

ফাইল পাথ হল ইউআরএল, ফাংশনের নাম হল পদ্ধতি, এবং প্রত্যাবর্তিত মান হল JSON বডি:

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

`:id` একটি `[id]` সেগমেন্ট, এবং টাইপ টীকা রূপান্তর করে এবং `404`:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

একটি `*` ওয়াইল্ডকার্ড একটি `[...rest].py` ফাইল।

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

`?page=abc` উত্তর দেয় `422` প্যারামিটার সহ যা ব্যর্থ হয়েছে, `NaN` এর পরিবর্তে।

## `req.body` এবং বৈধতা

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

ফাংশনটি চালানোর আগে একটি Pydantic মডেলের বিরুদ্ধে বডি পার্স এবং যাচাই করা হয়:

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

ফোল্ডারটি মাউন্ট পাথ:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## রুট মিডলওয়্যার

```js filename="routes/admin.js"
function requireAdmin(req, res, next) {
  if (req.get("x-role") !== "admin") return res.status(403).json({ error: "Admins only" });
  next();
}

admin.use(requireAdmin);
```

একটি `dependencies.py` এর ফোল্ডারের প্রতিটি রুটের আগে চলে। উত্থাপন অনুরোধটি বন্ধ করে দেয়, যেমন কল না করা `next()` করে:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `app.use` মিডলওয়্যার

```js filename="index.js"
app.use((req, res, next) => {
  const start = Date.now();
  res.on("finish", () => console.log(req.method, req.url, Date.now() - start));
  next();
});
```

রুট রুটে একটি `middleware.py` প্রতিটি অনুরোধ মোড়ানো হয়; `call_next` হল `next()`:

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## `cors`, `compression`, `helmet`-স্টাইল হোস্ট

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

## কুকিজ

```js filename="index.js"
import cookieParser from "cookie-parser";

app.use(cookieParser());

app.post("/api/theme", (req, res) => {
  res.cookie("theme", "dark").json({ theme: "dark" });
});

app.get("/api/theme", (req, res) => res.json({ theme: req.cookies.theme ?? "light" }));
```

একটি কুকি পড়ার জন্য একটি প্যারামিটার এবং লেখার প্রতিক্রিয়ার একটি পদ্ধতি:

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

`useSession` `nexyconfig.py` (উপরে) সেশন চালু করে; `request.session` একটি আদেশ:

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

## `multer` এর সাথে ফাইল আপলোড

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

## EJS বা Pug সহ ভিউ

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

একটি `.nexy` পৃষ্ঠা হল রুট এবং একবারে ভিউ:

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

`<%= %>` পালিয়ে যায় এবং `{{ }}` করে না: একজন দর্শক `{{ value | e }}` দিয়ে যা টাইপ করেন তা এড়িয়ে যান।

## `express.static`

```js filename="index.js"
app.use(express.static("public"));
```

লেখার কিছু নেই: `public/` `/` এ পরিবেশিত হয়।

## 404 হ্যান্ডলার এবং ত্রুটি হ্যান্ডলার

```js filename="index.js"
app.use((req, res) => res.status(404).send("<h1>Not found</h1>"));

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send("<h1>Something broke</h1>");
});
```

রুট রুটে দুটি ফাইল। API ক্লায়েন্টরা এখনও JSON পায়, ব্রাউজাররা পৃষ্ঠা পায়:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

```nexy filename="src/routes/errors.nexy"
<h1>Something broke</h1>
```

## ওয়েবসকেট সহ `ws`

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

## জেস্ট এবং সুপারটেস্ট সহ পরীক্ষা

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

## চলছে

| এক্সপ্রেস | নেক্সি |
|---|---|
| `npm init` + `npm i express` | `nx new` |
| `nodemon index.js` | `nx dev` |
| `NODE_ENV=production node index.js` | `nx build`, তারপর `nx start` |
| `npm test` | `nx test` |
| কোনো API ডক্স নেই | `/docs`, প্রতিটি `.py` রুটের তালিকা করা |

## আপনার React সামনের প্রান্তটি রাখা

যদি এক্সপ্রেস অ্যাপটি একটি React এসপিএ পরিবেশন করে, তবে উপাদানগুলি `src/components/` এ চলে যায় এবং একটি `.nexy` পৃষ্ঠার দ্বীপ হিসাবে রেন্ডার হয়, অথবা পুরো সাইটটি `useCSR = True` এর সাথে ক্লায়েন্ট রাউটিংয়ে চলে যায়। [দ্বীপ](../rendering/islands.md) এবং [CSR](../rendering/csr.md) দেখুন।

## পরবর্তী পদক্ষেপ

- [অন্য কাঠামো থেকে আসছে](../getting-started/coming-from-other-frameworks.md)
- [রুট হ্যান্ডলার](../routing/fbr/handlers/README.md)
- [মিডলওয়্যার ফাইল](../routing/fbr/middleware/README.md)
- [রেসিপি ](../guides/recipes.md)
