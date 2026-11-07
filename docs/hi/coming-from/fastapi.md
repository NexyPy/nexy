# FastAPI से नेक्सी तक

नेक्सी एक फ़ाइल के रूप में लिखे गए रूट के साथ FastAPI है: एक फ़ंक्शन जो `@app.get("/x")` के तहत उत्तर देता है `src/routes/x.py` में `GET` के रूप में उत्तर देता है, और आपका बाकी कोड वही रहता है।

## क्या रहता है, क्या बदलता है

नेक्सी आपके हैंडलर को FastAPI से ही सेवा प्रदान करता है, इसलिए हैंडलर के अंदर सब कुछ अपरिवर्तित काम करता है:

| वैसा ही रहता है | परिवर्तन |
|---|---|
| Pydantic मॉडल, अनुरोध निकाय और प्रतिक्रियाएं | `@app.get("/x")` `async def GET()` के साथ `src/routes/x.py` बन जाता है |
| `Depends`, `Query`, `Header`, `Cookie`, `Form`, `File` | `{id}` पथ में एक `[id].py` फ़ाइल या `[id]/` फ़ोल्डर बन जाता है |
| `HTTPException`, `status`, `JSONResponse`, `RedirectResponse` | `APIRouter(prefix="/users")` फ़ोल्डर बन जाता है `users/` |
| `Request`, `BackgroundTasks`, `UploadFile`, वेबसॉकेट | `dependencies=[...]` राउटर पर एक `dependencies.py` फ़ाइल बन जाती है |
| मिडलवेयर क्लासेस, `/docs`, `TestClient` | `app.add_middleware(...)` `nexyconfig.py` का एक क्षेत्र बन जाता है: `useCORS`, `useGZip`, `useMiddlewares` |

उन्हें पहले की तरह `fastapi` से आयात करें, या `nexy.http` से, जो उन्हीं वस्तुओं को फिर से निर्यात करता है।

नीचे प्रत्येक अनुभाग एक FastAPI आदत दिखाता है, फिर नेक्सी में भी वही चीज़।

## एक समापन बिंदु

FastAPI एक डेकोरेटर के साथ एक ऐप पर एक फ़ंक्शन पंजीकृत करता है:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/hello")
async def hello():
    return {"message": "Hello"}
```

नेक्सी फ़ाइल पथ से यूआरएल और फ़ंक्शन नाम से विधि पढ़ता है:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## पथ और क्वेरी पैरामीटर

```python filename="main.py"
@app.get("/api/users/{id}")
async def get_user(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

पथ पैरामीटर फ़ाइल नाम का `[id]` खंड बन जाता है। क्वेरी पैरामीटर नहीं चलता है:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str | None = None):
    return {"id": id, "fields": fields}
```

`/api/users/abc` उत्तर देता है `404`, क्योंकि `abc` एक `int` नहीं है।

## एक अनुरोध निकाय

```python filename="main.py"
from pydantic import BaseModel


class NewItem(BaseModel):
    name: str
    price: float


@app.post("/api/items", status_code=201)
async def create_item(item: NewItem):
    return item
```

Pydantic मॉडल वही है। स्थिति कोड प्रतिक्रिया में चला जाता है:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

एक निकाय जो मॉडल उत्तर से मेल नहीं खाता है `422`, जैसा कि FastAPI में है।

## एक यूआरएल पर कई विधियाँ

```python filename="main.py"
@app.get("/api/notes/{id}")
async def read_note(id: int): ...


@app.delete("/api/notes/{id}")
async def delete_note(id: int): ...
```

एक फ़ाइल में URL की प्रत्येक विधि होती है:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## राउटर और उपसर्ग

```python filename="main.py"
from fastapi import APIRouter

admin = APIRouter(prefix="/admin")


@admin.get("/stats")
async def stats():
    return {"users": 3}


app.include_router(admin)
```

फ़ोल्डर उपसर्ग है, और इसमें शामिल करने के लिए कुछ भी नहीं है:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## मार्गों के समूह पर निर्भरता

```python filename="main.py"
from fastapi import Depends, Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
```

फ़ोल्डर में एक `dependencies.py` उसके नीचे प्रत्येक रूट से पहले चलता है:

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

एक हैंडलर के लिए एक निर्भरता अभी भी `Depends` है, उसके हस्ताक्षर में:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header


def current_user(authorization: str = Header(...)) -> str:
    return authorization.removeprefix("Bearer ")


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## मिडलवेयर

```python filename="main.py"
from fastapi import Request


@app.middleware("http")
async def add_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

एक `middleware.py` अपने फ़ोल्डर के मार्गों को लपेटता है, रूट उन सभी को लपेटता है:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## CORS, GZip और अन्य ऐप-वाइड मिडलवेयर

```python filename="main.py"
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["https://example.com"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

प्रत्येक एक `nexyconfig.py` का एक क्षेत्र है, समान तर्कों के साथ:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## HTML पृष्ठ

```python filename="main.py"
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


@app.get("/users")
async def users_page(request: Request):
    users = [{"name": "Ada"}, {"name": "Alan"}]
    return templates.TemplateResponse(request, "users.html", {"users": users})
```

एक `.nexy` पेज में Python को `---` लाइन के ऊपर और Jinja2 को एक फ़ाइल में रखा जाता है:

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

## टेम्पलेट विरासत

```html filename="टेम्प्लेट/बेस.एचटीएमएल"
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

एक `layout.nexy` अपने फ़ोल्डर के प्रत्येक पृष्ठ को लपेटता है, पृष्ठों में कोई `{% extends %}` नहीं है:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## स्थैतिक फ़ाइलें

```python filename="main.py"
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

`public/` में फ़ाइलें रूट से परोसी जाती हैं: `public/robots.txt` `/robots.txt` है।

```text
public/
├─ robots.txt     /robots.txt
└─ logo.png       /logo.png
```

## नहीं मिले पन्ने

```python filename="main.py"
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def not_found(request: Request, exc: StarletteHTTPException):
    return HTMLResponse("<h1>Not found</h1>", status_code=exc.status_code)
```

ए `notfound.nexy` ब्राउज़रों को उत्तर देता है, और एपीआई क्लाइंट को अभी भी `{"detail": ...}` मिलता है:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## वेबसॉकेट

```python filename="main.py"
from fastapi import WebSocket


@app.websocket("/ws/echo")
async def echo(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

```python filename="src/routes/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## परीक्षण

```python filename="परीक्षण/test_main.py"
from fastapi.testclient import TestClient

from main import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

ग्राहक वही है; ऐप नेक्सी से आता है:

```python filename="परीक्षण/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## चल रहा है

| FastAPI | नेक्सी |
|---|---|
| `uvicorn main:app --reload` | `nx dev` |
| `uvicorn main:app --workers 4` | `nx build`, फिर `nx start` |
| `/docs` से `FastAPI()` | `/docs`, प्रत्येक `.py` मार्ग को सूचीबद्ध करते हुए |

## मौजूदा ऐप रखना

आपको हर रास्ते पर एक साथ चलने की ज़रूरत नहीं है. एक `APIRouter` आपके पास पहले से ही माउंट हैं:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

आपके पुराने मार्ग और `src/routes/` की फ़ाइलें साथ-साथ उत्तर देती हैं। जबकि `useRouter` सेट है, `.nexy` पृष्ठ `layout.nexy` द्वारा लपेटे नहीं जाते हैं: पहले एपीआई को स्थानांतरित करें, फिर पृष्ठों को, फिर फ़ील्ड को हटा दें। [कस्टम राउटर एकीकरण](../routing/custom/README.md) देखें।

## अगले चरण

- [मार्ग संचालक](../routing/fbr/handlers/README.md)
- [निर्भरताएँ और रक्षक](../routing/fbr/dependencies/README.md)
- [.nexy फ़ाइलें](../views/nexy/README.md)
- [किसी अन्य ढाँचे से आ रहा है](../getting-started/coming-from-other-frameworks.md)
