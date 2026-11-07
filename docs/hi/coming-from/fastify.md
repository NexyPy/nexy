# फास्टिफाइ से नेक्सी तक

नेक्सी में एक फास्टिफ़ाई रूट `src/routes/` के अंतर्गत एक Python फ़ाइल बन जाता है: JSON स्कीमा Pydantic मॉडल बन जाते हैं, `prefix` वाले प्लगइन्स फ़ोल्डर बन जाते हैं, और हुक `dependencies.py` और `middleware.py` फ़ाइलें बन जाते हैं।

नीचे दिया गया प्रत्येक अनुभाग एक फास्टिफ़ाई आदत दिखाता है, फिर नेक्सी में भी यही चीज़।

## एक मार्ग

```js filename="सर्वर.जे.एस"
import Fastify from "fastify";

const app = Fastify({ logger: true });

app.get("/api/hello", async () => ({ message: "Hello" }));

await app.listen({ port: 3000 });
```

फ़ाइल पथ URL है, और फ़ंक्शन नाम विधि है:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

प्रत्येक अनुरोध को उसकी विधि, पथ, स्थिति और समय के साथ लॉग किया जाता है, जिसमें कोई लॉगर सेट अप नहीं होता है।

## पैराम्स और क्वेरीस्ट्रिंग स्कीमा

```js filename="सर्वर.जे.एस"
app.get(
  "/api/users/:id",
  {
    schema: {
      params: { type: "object", properties: { id: { type: "integer" } } },
      querystring: { type: "object", properties: { fields: { type: "string" } } },
    },
  },
  async (request) => ({ id: request.params.id, fields: request.query.fields }),
);
```

स्कीमा हस्ताक्षर है: `[id]` फ़ाइल नाम में, पैरामीटर पर प्रकार:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

## शारीरिक स्कीमा

```js filename="सर्वर.जे.एस"
app.post(
  "/api/items",
  {
    schema: {
      body: {
        type: "object",
        required: ["name", "price"],
        properties: { name: { type: "string" }, price: { type: "number", exclusiveMinimum: 0 } },
      },
    },
  },
  async (request, reply) => reply.code(201).send(request.body),
);
```

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

एक निकाय जो उत्तर देने में विफल रहता है `422`, जहां फास्टिफाई उत्तर `400` देता है।

## प्रतिक्रिया स्कीमा

```js filename="सर्वर.जे.एस"
app.get(
  "/api/me",
  {
    schema: {
      response: {
        200: { type: "object", properties: { name: { type: "string" } } },
      },
    },
  },
  async () => ({ name: "Ada", passwordHash: "x" }),
);
```

रिटर्न प्रकार वही करता है जो प्रतिक्रिया स्कीमा करती है: जिन फ़ील्ड को यह घोषित नहीं करता है उन्हें छोड़ दिया जाता है।

```python filename="src/routes/api/me.py"
from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


async def GET() -> PublicUser:
    return {"name": "Ada", "password_hash": "x"}
```

## उपसर्ग के साथ प्लगइन्स

```js filename="मार्ग/व्यवस्थापक.js"
export default async function admin(app) {
  app.get("/stats", async () => ({ users: 3 }));
}
```

```js filename="सर्वर.जे.एस"
app.register(admin, { prefix: "/admin" });
```

फ़ोल्डर उपसर्ग है, और कुछ भी पंजीकृत नहीं है:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `preHandler` और `onRequest` हुक

```js filename="मार्ग/व्यवस्थापक.js"
export default async function admin(app) {
  app.addHook("preHandler", async (request, reply) => {
    if (request.headers["x-role"] !== "admin") {
      return reply.code(403).send({ error: "Admins only" });
    }
  });
}
```

एक प्लगइन के दायरे वाला हुक उसके फ़ोल्डर में एक `dependencies.py` है:

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `onSend` और `onResponse` हुक

```js filename="सर्वर.जे.एस"
app.addHook("onSend", async (request, reply, payload) => {
  reply.header("x-app", "demo");
  return payload;
});
```

`middleware.py` में `call_next` के बाद का कोड बाहर की ओर चलता है:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `decorate` और `decorateRequest`

```js filename="सर्वर.जे.एस"
app.decorate("db", { users: () => [{ name: "Ada" }] });

app.get("/api/users", async function () {
  return this.db.users();
});
```

एक साझा ऑब्जेक्ट एक फ़ंक्शन है जो इसे लौटाता है, और एक हैंडलर इसे `Depends` के साथ मांगता है:

```python filename="src/db.py"
class Db:
    def users(self) -> list[dict]:
        return [{"name": "Ada"}]


db = Db()


def get_db() -> Db:
    return db
```

```python filename="src/routes/api/users/index.py"
from nexy.http import Depends

from src.db import Db, get_db


async def GET(db: Db = Depends(get_db)):
    return db.users()
```

एक परीक्षण इसे `app.dependency_overrides[get_db]` से बदल देता है।

## `@fastify/cors`, `@fastify/compress`, `@fastify/cookie`

```js filename="सर्वर.जे.एस"
await app.register(import("@fastify/cors"), { origin: "https://example.com" });
await app.register(import("@fastify/compress"));
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

कुकी को किसी प्लगइन की आवश्यकता नहीं है: इसे `Cookie` पैरामीटर के साथ पढ़ें, इसे `response.set_cookie` के साथ सेट करें।

```python filename="src/routes/api/theme.py"
from nexy.http import Cookie


async def GET(theme: str = Cookie("light")):
    return {"theme": theme}
```

## `setErrorHandler` और `setNotFoundHandler`

```js filename="सर्वर.जे.एस"
app.setNotFoundHandler((request, reply) => reply.code(404).type("text/html").send("<h1>Not found</h1>"));
```

ब्राउज़रों को `notfound.nexy`, एपीआई क्लाइंट `{"detail": "Not Found"}` मिलते हैं:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

एक हैंडलर जो जानता है कि क्या गलत हुआ वह इसे उठाता है:

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id}
```

## `@fastify/static`

```js filename="सर्वर.जे.एस"
await app.register(import("@fastify/static"), { root: path.join(__dirname, "public") });
```

लिखने के लिए कुछ भी नहीं: `public/` `/` पर परोसा जाता है।

## `@fastify/websocket`

```js filename="सर्वर.जे.एस"
await app.register(import("@fastify/websocket"));

app.get("/ws/echo", { websocket: true }, (socket) => {
  socket.on("message", (message) => socket.send(message));
});
```

```python filename="src/routes/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## `@fastify/swagger`

```js filename="सर्वर.जे.एस"
await app.register(import("@fastify/swagger"));
await app.register(import("@fastify/swagger-ui"), { routePrefix: "/docs" });
```

पंजीकृत करने के लिए कुछ भी नहीं: OpenAPI स्कीमा टाइप एनोटेशन से बनाई गई है और `/docs` पर प्रस्तुत की गई है।

## `inject` के साथ परीक्षण

```js filename="सर्वर.टेस्ट.जे.एस"
const response = await app.inject({ method: "GET", url: "/api/hello" });
expect(response.json()).toEqual({ message: "Hello" });
```

`TestClient` बिना किसी पोर्ट के मेमोरी में भी एप्लिकेशन को कॉल करता है:

```python filename="परीक्षण/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## चल रहा है

| उपवास करें | नेक्सी |
|---|---|
| `npm init fastify` | `nx new` |
| `fastify start -w app.js` | `nx dev` |
| `node server.js` उत्पादन में | `nx build`, फिर `nx start` |
| `npm test` | `nx test` |

## अगले चरण

- [एक्सप्रेस से नेक्सी तक](express.md)
- [मार्ग संचालक](../routing/fbr/handlers/README.md)
- [सत्यापन और त्रुटियाँ](../routing/fbr/handlers/validation-and-errors.md)
- [निर्भरताएँ और रक्षक](../routing/fbr/dependencies/README.md)
