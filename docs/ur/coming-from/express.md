# ایکسپریس سے Nexy تک

Nexy میں ایک ایکسپریس روٹ `src/routes/` کے تحت ایک Python فائل بن جاتا ہے: `app.get` ایک `GET` فنکشن ہے، `req` ٹائپ شدہ پیرامیٹرز میں، `res.json` کو واپسی کی قدر میں، اور `app.use` کنفیگ فیلڈز یا `middleware.py` میں بدل جاتا ہے۔

ذیل میں ہر سیکشن ایکسپریس عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔

## ایک راستہ

```js filename="index.js"
import express from "express";

const app = express();

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello" });
});

app.listen(3000);
```

فائل کا راستہ یو آر ایل ہے، فنکشن کا نام طریقہ ہے، اور واپس کی گئی قدر JSON باڈی ہے:

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

`:id` ایک `[id]` طبقہ ہے، اور قسم کی تشریح تبدیلی کرتی ہے اور `404`:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

ایک `*` وائلڈ کارڈ ایک `[...rest].py` فائل ہے۔

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

`?page=abc` جوابات `422` کے پیرامیٹر کے ساتھ جو ناکام ہوئے، `NaN` کے بجائے۔

## `req.body` اور توثیق

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

فنکشن چلنے سے پہلے باڈی کو Pydantic ماڈل کے خلاف پارس اور توثیق کیا جاتا ہے:

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

فولڈر ماؤنٹ پاتھ ہے:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## روٹ مڈل ویئر

```js filename="routes/admin.js"
function requireAdmin(req, res, next) {
  if (req.get("x-role") !== "admin") return res.status(403).json({ error: "Admins only" });
  next();
}

admin.use(requireAdmin);
```

اس کے فولڈر کے ہر روٹ سے پہلے ایک `dependencies.py` چلتا ہے۔ اٹھانے سے درخواست رک جاتی ہے، جیسا کہ کال نہ کرنا `next()` کرتا ہے:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `app.use` مڈل ویئر

```js filename="index.js"
app.use((req, res, next) => {
  const start = Date.now();
  res.on("finish", () => console.log(req.method, req.url, Date.now() - start));
  next();
});
```

روٹس پر ایک `middleware.py` ہر درخواست کو سمیٹتا ہے۔ `call_next` ہے `next()`:

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## `cors`، `compression`، `helmet` طرز کے میزبان

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

## کوکیز

```js filename="index.js"
import cookieParser from "cookie-parser";

app.use(cookieParser());

app.post("/api/theme", (req, res) => {
  res.cookie("theme", "dark").json({ theme: "dark" });
});

app.get("/api/theme", (req, res) => res.json({ theme: req.cookies.theme ?? "light" }));
```

کوکی پڑھنے کا ایک پیرامیٹر ہے، اور لکھنے کے جواب کا ایک طریقہ ہے:

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

`useSession` `nexyconfig.py` میں (اوپر) سیشن کو آن کرتا ہے۔ `request.session` ایک فرمان ہے:

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

## `multer` کے ساتھ فائل اپ لوڈ

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

## EJS یا Pug کے ساتھ مناظر

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

ایک `.nexy` صفحہ ایک ساتھ راستہ اور منظر ہے:

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

`<%= %>` فرار ہوتا ہے اور `{{ }}` نہیں کرتا: فرار جو ایک وزیٹر `{{ value | e }}` کے ساتھ ٹائپ کرتا ہے۔

## `express.static`

```js filename="index.js"
app.use(express.static("public"));
```

لکھنے کے لیے کچھ نہیں: `public/` `/` پر پیش کیا جاتا ہے۔

## 404 ہینڈلر اور ایرر ہینڈلر

```js filename="index.js"
app.use((req, res) => res.status(404).send("<h1>Not found</h1>"));

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send("<h1>Something broke</h1>");
});
```

روٹس روٹ پر دو فائلیں۔ API کلائنٹس اب بھی JSON حاصل کرتے ہیں، براؤزر کو صفحہ ملتا ہے:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

```nexy filename="src/routes/errors.nexy"
<h1>Something broke</h1>
```

## ویب ساکٹس کے ساتھ `ws`

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

## جیسٹ اور سپرٹیسٹ کے ساتھ ٹیسٹ

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

## چل رہا ہے۔

| ایکسپریس | نیکسی |
|---|---|
| `npm init` + `npm i express` | `nx new` |
| `nodemon index.js` | `nx dev` |
| `NODE_ENV=production node index.js` | `nx build`، پھر `nx start` |
| `npm test` | `nx test` |
| کوئی API دستاویزات نہیں ہیں۔ | `/docs`، ہر `.py` راستے کی فہرست |

## اپنے React کو سامنے رکھنا

اگر ایکسپریس ایپ نے ایک React SPA پیش کیا، تو اجزاء `src/components/` میں چلے جاتے ہیں اور `.nexy` صفحہ کے جزیروں کے طور پر پیش کرتے ہیں، یا پوری سائٹ `useCSR = True` کے ساتھ کلائنٹ روٹنگ میں منتقل ہوجاتی ہے۔ دیکھیں [جزیرے](../rendering/islands.md) اور [CSR](../rendering/csr.md)۔

## اگلے اقدامات

- [دوسرے فریم ورک سے آرہا ہے](../getting-started/coming-from-other-frameworks.md)
- [روٹ ہینڈلر](../routing/fbr/handlers/README.md)
- [مڈل ویئر فائلیں](../routing/fbr/middleware/README.md)
- [ترکیبیں](../guides/recipes.md)
