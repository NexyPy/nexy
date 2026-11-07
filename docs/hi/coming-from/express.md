# एक्सप्रेस से नेक्सी तक

नेक्सी में एक एक्सप्रेस रूट `src/routes/` के अंतर्गत एक Python फ़ाइल बन जाता है: `app.get` एक `GET` फ़ंक्शन है, `req` टाइप किए गए पैरामीटर में बदल जाता है, `res.json` रिटर्न वैल्यू में, और `app.use` कॉन्फ़िगरेशन फ़ील्ड या `middleware.py` में बदल जाता है।

नीचे प्रत्येक अनुभाग एक एक्सप्रेस आदत दिखाता है, फिर नेक्सी में भी वही चीज़।

## एक मार्ग

```js filename="सूचकांक.जे.एस"
import express from "express";

const app = express();

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello" });
});

app.listen(3000);
```

फ़ाइल पथ URL है, फ़ंक्शन नाम विधि है, और लौटाया गया मान JSON बॉडी है:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `req.params`

```js filename="सूचकांक.जे.एस"
app.get("/api/users/:id", (req, res) => {
  const id = Number(req.params.id);
  if (Number.isNaN(id)) return res.status(404).end();
  res.json({ id });
});
```

`:id` एक `[id]` खंड है, और प्रकार एनोटेशन रूपांतरण करता है और `404`:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

एक `*` वाइल्डकार्ड एक `[...rest].py` फ़ाइल है।

## `req.query`

```js filename="सूचकांक.जे.एस"
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

`?page=abc` `NaN` के बजाय विफल पैरामीटर के साथ `422` का उत्तर देता है।

## `req.body` और सत्यापन

```js filename="सूचकांक.जे.एस"
import { z } from "zod";

app.use(express.json());

const NewItem = z.object({ name: z.string(), price: z.number().positive() });

app.post("/api/items", (req, res) => {
  const parsed = NewItem.safeParse(req.body);
  if (!parsed.success) return res.status(422).json(parsed.error);
  res.status(201).json(parsed.data);
});
```

फ़ंक्शन चलने से पहले बॉडी को Pydantic मॉडल के विरुद्ध पार्स और मान्य किया जाता है:

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

```js filename="मार्ग/व्यवस्थापक.js"
const admin = express.Router();

admin.get("/stats", (req, res) => res.json({ users: 3 }));

app.use("/admin", admin);
```

फ़ोल्डर माउंट पथ है:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## रूट मिडलवेयर

```js filename="मार्ग/व्यवस्थापक.js"
function requireAdmin(req, res, next) {
  if (req.get("x-role") !== "admin") return res.status(403).json({ error: "Admins only" });
  next();
}

admin.use(requireAdmin);
```

एक `dependencies.py` अपने फ़ोल्डर के प्रत्येक रूट से पहले चलता है। बढ़ाने से अनुरोध रुक जाता है, जैसा कि `next()` को कॉल न करने से होता है:

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `app.use` मिडलवेयर

```js filename="सूचकांक.जे.एस"
app.use((req, res, next) => {
  const start = Date.now();
  res.on("finish", () => console.log(req.method, req.url, Date.now() - start));
  next();
});
```

रूट रूट पर एक `middleware.py` प्रत्येक अनुरोध को लपेटता है; `call_next` है `next()`:

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## `cors`, `compression`, `helmet`-शैली के मेजबान

```js filename="सूचकांक.जे.एस"
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

## कुकीज़

```js filename="सूचकांक.जे.एस"
import cookieParser from "cookie-parser";

app.use(cookieParser());

app.post("/api/theme", (req, res) => {
  res.cookie("theme", "dark").json({ theme: "dark" });
});

app.get("/api/theme", (req, res) => res.json({ theme: req.cookies.theme ?? "light" }));
```

कुकी पढ़ने के लिए एक पैरामीटर है, और लिखने के लिए प्रतिक्रिया की एक विधि है:

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

```js filename="सूचकांक.जे.एस"
import session from "express-session";

app.use(session({ secret: "change-me" }));

app.post("/api/login", (req, res) => {
  req.session.user = req.body.name;
  res.json({ user: req.session.user });
});
```

`useSession` में `nexyconfig.py` (ऊपर) सत्र चालू करता है; `request.session` एक आदेश है:

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

```js filename="सूचकांक.जे.एस"
app.get("/old", (req, res) => res.redirect(301, "/new"));
```

```python filename="src/routes/old.py"
from nexy.http import RedirectResponse


async def GET():
    return RedirectResponse("/new", status_code=301)
```

## `multer` के साथ फ़ाइल अपलोड

```js filename="सूचकांक.जे.एस"
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

## ईजेएस या पग के साथ दृश्य

```js filename="सूचकांक.जे.एस"
app.set("view engine", "ejs");

app.get("/users", (req, res) => {
  res.render("users", { users: [{ name: "Ada" }, { name: "Alan" }] });
});
```

```html filename="दृश्य/उपयोगकर्ता.ejs"
<ul>
  <% users.forEach((user) => { %>
  <li><%= user.name %></li>
  <% }) %>
</ul>
```

एक `.nexy` पृष्ठ एक साथ मार्ग और दृश्य है:

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

`<%= %>` बच जाता है और `{{ }}` नहीं बचता: विज़िटर ने `{{ value | e }}` के साथ जो टाइप किया है वह बच जाता है।

## `express.static`

```js filename="सूचकांक.जे.एस"
app.use(express.static("public"));
```

लिखने के लिए कुछ भी नहीं: `public/` `/` पर परोसा जाता है।

## 404 हैंडलर और त्रुटि हैंडलर

```js filename="सूचकांक.जे.एस"
app.use((req, res) => res.status(404).send("<h1>Not found</h1>"));

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send("<h1>Something broke</h1>");
});
```

रूट रूट पर दो फ़ाइलें। एपीआई क्लाइंट को अभी भी JSON मिलता है, ब्राउज़र को पेज मिलता है:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

```nexy filename="src/routes/errors.nexy"
<h1>Something broke</h1>
```

## `ws` के साथ वेबसॉकेट

```js filename="सूचकांक.जे.एस"
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

## जेस्ट और सुपरटेस्ट के साथ परीक्षण

```js filename="Index.test.js"
import request from "supertest";
import { app } from "./app.js";

test("hello", async () => {
  const res = await request(app).get("/api/hello");
  expect(res.body).toEqual({ message: "Hello" });
});
```

```python filename="परीक्षण/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## चल रहा है

| एक्सप्रेस | नेक्सी |
|---|---|
| `npm init` + `npm i express` | `nx new` |
| `nodemon index.js` | `nx dev` |
| `NODE_ENV=production node index.js` | `nx build`, फिर `nx start` |
| `npm test` | `nx test` |
| कोई एपीआई दस्तावेज़ नहीं | `/docs`, प्रत्येक `.py` मार्ग को सूचीबद्ध करते हुए |

## अपना React सामने रखें

यदि एक्सप्रेस ऐप एक React एसपीए प्रदान करता है, तो घटक `src/components/` पर चले जाते हैं और `.nexy` पृष्ठ के द्वीपों के रूप में प्रस्तुत होते हैं, या पूरी साइट `useCSR = True` के साथ क्लाइंट रूटिंग पर चली जाती है। [द्वीप](../rendering/islands.md) और [सीएसआर](../rendering/csr.md) देखें।

## अगले चरण

- [किसी अन्य ढाँचे से आ रहा है](../getting-started/coming-from-other-frameworks.md)
- [मार्ग संचालक](../routing/fbr/handlers/README.md)
- [मिडलवेयर फ़ाइलें](../routing/fbr/middleware/README.md)
- [रेसिपी](../guides/recipes.md)
