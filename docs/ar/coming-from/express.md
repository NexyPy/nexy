# من اكسبرس إلى Nexy

في Nexy، يصبح المسار السريع ملف Python ضمن `src/routes/`: `app.get` هو دالة `GET`، ويتحول `req` إلى معلمات مكتوبة، و `res.json` إلى قيمة إرجاع، و `app.use` إلى حقول التكوين أو `middleware.py`.

يعرض كل قسم أدناه عادة Express، ثم نفس الشيء في Nexy.

## طريق

```js filename="Index.js"
import express from "express";

const app = express();

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello" });
});

app.listen(3000);
```

مسار الملف هو عنوان URL، واسم الوظيفة هو الطريقة، والقيمة التي تم إرجاعها هي نص JSON:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `req.params`

```js filename="Index.js"
app.get("/api/users/:id", (req, res) => {
  const id = Number(req.params.id);
  if (Number.isNaN(id)) return res.status(404).end();
  res.json({ id });
});
```

`:id` هو مقطع `[id]`، والتعليق التوضيحي للنوع يقوم بالتحويل و `404`:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

حرف البدل `*` هو ملف `[...rest].py`.

## `req.query`

```js filename="Index.js"
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

`?page=abc` يجيب `422` بالمعلمة الفاشلة، بدلاً من `NaN`.

## `req.body` والتصديق

```js filename="Index.js"
import { z } from "zod";

app.use(express.json());

const NewItem = z.object({ name: z.string(), price: z.number().positive() });

app.post("/api/items", (req, res) => {
  const parsed = NewItem.safeParse(req.body);
  if (!parsed.success) return res.status(422).json(parsed.error);
  res.status(201).json(parsed.data);
});
```

يتم تحليل النص والتحقق من صحته وفقًا لنموذج Pydantic قبل تشغيل الوظيفة:

```python filename=""
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## `express.Router()`

```js filename="الطرق/admin.js"
const admin = express.Router();

admin.get("/stats", (req, res) => res.json({ users: 3 }));

app.use("/admin", admin);
```

المجلد هو مسار التثبيت:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## طريق الوسيطة

```js filename="الطرق/admin.js"
function requireAdmin(req, res, next) {
  if (req.get("x-role") !== "admin") return res.status(403).json({ error: "Admins only" });
  next();
}

admin.use(requireAdmin);
```

يتم تشغيل `dependencies.py` قبل كل مسار للمجلد الخاص به. الرفع يوقف الطلب، فعدم الاتصال `next()` يفعل:

```python filename="src/routes/admin/dependeency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `app.use` الوسيطة

```js filename="Index.js"
app.use((req, res, next) => {
  const start = Date.now();
  res.on("finish", () => console.log(req.method, req.url, Date.now() - start));
  next();
});
```

A `middleware.py` في جذر المسارات يغلف كل طلب؛ `call_next` هو `next()`:

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## `cors`، `compression`، `helmet` على نمط المضيفين

```js filename="Index.js"
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

## ملفات تعريف الارتباط

```js filename="Index.js"
import cookieParser from "cookie-parser";

app.use(cookieParser());

app.post("/api/theme", (req, res) => {
  res.cookie("theme", "dark").json({ theme: "dark" });
});

app.get("/api/theme", (req, res) => res.json({ theme: req.cookies.theme ?? "light" }));
```

ملف تعريف الارتباط هو معلمة للقراءة وطريقة للرد للكتابة:

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

```js filename="Index.js"
import session from "express-session";

app.use(session({ secret: "change-me" }));

app.post("/api/login", (req, res) => {
  req.session.user = req.body.name;
  res.json({ user: req.session.user });
});
```

`useSession` في `nexyconfig.py` (أعلاه) يقوم بتشغيل الجلسات؛ `request.session` هو القول:

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

```js filename="Index.js"
app.get("/old", (req, res) => res.redirect(301, "/new"));
```

```python filename="src/routes/old.py"
from nexy.http import RedirectResponse


async def GET():
    return RedirectResponse("/new", status_code=301)
```

## تحميل الملفات مع `multer`

```js filename="Index.js"
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

## وجهات النظر مع EJS أو الصلصال

```js filename="Index.js"
app.set("view engine", "ejs");

app.get("/users", (req, res) => {
  res.render("users", { users: [{ name: "Ada" }, { name: "Alan" }] });
});
```

```html filename="وجهات النظر/users.ejs"
<ul>
  <% users.forEach((user) => { %>
  <li><%= user.name %></li>
  <% }) %>
</ul>
```

صفحة `.nexy` هي المسار والعرض في آن واحد:

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

`<%= %>` يهرب و `{{ }}` لا: يهرب مما كتبه الزائر بـ `{{ value | e }}`.

## `express.static`

```js filename="Index.js"
app.use(express.static("public"));
```

لا يوجد شيء للكتابة: `public/` يتم تقديمه في `/`.

## معالج 404 ومعالج الأخطاء

```js filename="Index.js"
app.use((req, res) => res.status(404).send("<h1>Not found</h1>"));

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send("<h1>Something broke</h1>");
});
```

ملفين في جذر الطرق. لا يزال عملاء API يحصلون على JSON، وتحصل المتصفحات على الصفحة:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

```nexy filename="src/routes/errors.nexy"
<h1>Something broke</h1>
```

## WebSockets مع `ws`

```js filename="Index.js"
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

## اختبارات مع Jest وSupertest

```js filename="Index.test.js"
import request from "supertest";
import { app } from "./app.js";

test("hello", async () => {
  const res = await request(app).get("/api/hello");
  expect(res.body).toEqual({ message: "Hello" });
});
```

```python filename="الاختبارات/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## الجري

| صريحة | نكسي |
|---|---|
| `npm init` + `npm i express` | `nx new` |
| `nodemon index.js` | `nx dev` |
| `NODE_ENV=production node index.js` | `nx build`، ثم `nx start` |
| `npm test` | `nx test` |
| لا توجد مستندات API | `/docs`، سرد كل `.py` الطريق |

## الحفاظ على React الواجهة الأمامية

إذا كان تطبيق Express يقدم React SPA، فستنتقل المكونات إلى `src/components/` ويتم عرضها كجزر لصفحة `.nexy`، أو ينتقل الموقع بالكامل إلى توجيه العميل باستخدام `useCSR = True`. انظر [الجزر](../rendering/islands.md) و [المسؤولية الاجتماعية للشركات](../rendering/csr.md).

## الخطوات التالية

- [قادمة من إطار آخر](../getting-started/coming-from-other-frameworks.md)
- [معالجات الطريق](../routing/fbr/handlers/README.md)
- [ملفات الوسيطة](../routing/fbr/middleware/README.md)
- [الوصفات](../guides/recipes.md)
