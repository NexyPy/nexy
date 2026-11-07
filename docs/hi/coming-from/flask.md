# Flask से नेक्सी तक

नेक्सी में एक Flask दृश्य `src/routes/` के अंतर्गत एक फ़ाइल बन जाता है: JSON के लिए एक `.py` फ़ाइल, HTML के लिए एक `.nexy` फ़ाइल, जिसमें Jinja2 रखा जाता है और डेकोरेटर, ब्लूप्रिंट और `request` वैश्विक चला जाता है।

नीचे प्रत्येक अनुभाग एक Flask आदत दिखाता है, फिर नेक्सी में भी वही चीज़।

## एक मार्ग

```python filename="ऐप.पी.ई"
from flask import Flask

app = Flask(__name__)


@app.get("/api/hello")
def hello():
    return {"message": "Hello"}
```

फ़ाइल पथ URL है और फ़ंक्शन नाम विधि है:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## यूआरएल चर

```python filename="ऐप.पी.ई"
@app.get("/api/users/<int:id>")
def get_user(id):
    return {"id": id}
```

कनवर्टर एक प्रकार का एनोटेशन बन जाता है, और वेरिएबल एक `[id]` खंड बन जाता है:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` एक कैच-ऑल सेगमेंट है, `[...rest].py`।

## क्वेरी स्ट्रिंग्स

```python filename="ऐप.पी.ई"
from flask import request


@app.get("/api/search")
def search():
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    return {"q": q, "page": page}
```

कोई `request` वैश्विक नहीं है: एक क्वेरी पैरामीटर एक फ़ंक्शन पैरामीटर है, परिवर्तित और मान्य:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## एक JSON बॉडी

```python filename="ऐप.पी.ई"
@app.post("/api/items")
def create_item():
    data = request.get_json()
    if "name" not in data:
        return {"error": "name is required"}, 400
    return {"created": data["name"]}, 201
```

एक Pydantic मॉडल शरीर को मान्य करता है, और एक खराब मॉडल `422` अपने आप उत्तर देता है:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## एक यूआरएल पर कई विधियाँ

```python filename="ऐप.पी.ई"
@app.route("/api/notes/<int:id>", methods=["GET", "DELETE"])
def note(id):
    if request.method == "DELETE":
        return {"deleted": id}
    return {"id": id}
```

प्रति विधि एक फ़ंक्शन, एक ही फ़ाइल में:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## टेम्पलेट्स

```python filename="ऐप.पी.ई"
from flask import render_template


@app.get("/users")
def users():
    return render_template("users.html", users=[{"name": "Ada"}, {"name": "Alan"}])
```

दृश्य और उसका टेम्पलेट एक `.nexy` फ़ाइल हैं: Python `---` लाइन के ऊपर, वही Jinja2 नीचे:

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

## एक आधार टेम्पलेट

```html filename="टेम्प्लेट/बेस.एचटीएमएल"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

एक `layout.nexy` अपने फ़ोल्डर के प्रत्येक पृष्ठ को लपेटता है और नीचे; पेज यह `{% extends %}` नहीं करते:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## मैक्रोज़ और शामिल हैं

```html filename="टेम्पलेट्स/मैक्रोज़.एचटीएमएल"
{% macro card(title) %}
<article><h2>{{ title }}</h2>{{ caller() }}</article>
{% endmacro %}
```

एक घटक प्रॉप्स के साथ एक `.nexy` फ़ाइल है, जिसे फ्रंटमैटर में आयात किया जाता है:

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
---
<article>
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>Everything published this week.</p>
</Card>
```

`@` है `src/`: `nx new` `nexyconfig.py` में `useAliases = {"@": "src"}` लिखता है।

## ब्लूप्रिंट

```python filename="admin.py"
from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.get("/stats")
def stats():
    return {"users": 3}


app.register_blueprint(admin)
```

एक फ़ोल्डर उपसर्ग है, और कुछ भी पंजीकृत नहीं है:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `before_request`

```python filename="admin.py"
from flask import abort


@admin.before_request
def require_admin():
    if request.headers.get("X-Role") != "admin":
        abort(403)
```

एक `dependencies.py` अपने फ़ोल्डर के प्रत्येक रूट से पहले और नीचे चलता है:

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `after_request`

```python filename="ऐप.पी.ई"
@app.after_request
def add_header(response):
    response.headers["X-App"] = "demo"
    return response
```

ए `middleware.py` मार्ग से पहले अनुरोध और उसके बाद प्रतिक्रिया देखता है:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## प्रपत्र और पुनर्निर्देशन

```python filename="ऐप.पी.ई"
from flask import redirect, url_for


@app.post("/notes")
def add_note():
    NOTES.append(request.form["title"])
    return redirect(url_for("notes"))
```

एक क्रिया एक Python फ़ंक्शन है जिस पर फ़ॉर्म पोस्ट किया जाता है। नेक्सी इसे एक पथ देता है, फॉर्म फ़ील्ड को इसके पैरामीटर के रूप में पढ़ता है, और विज़िटर को `303` के साथ पृष्ठ पर वापस भेजता है:

```python filename="src/actions/notes.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/routes/notes.nexy"
---
from src.actions.notes import NOTES
---
<form method="post" action="{{ __actions_path['add_note'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
<ul>
  {% for note in NOTES %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

## सत्र

```python filename="ऐप.पी.ई"
from flask import session

app.secret_key = "change-me"


@app.post("/api/login")
def login():
    session["user"] = request.json["name"]
    return {"user": session["user"]}
```

रहस्य `nexyconfig.py` पर चला जाता है, और सत्र अनुरोध को बंद कर देता है:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

```python filename="src/routes/api/login.py"
from pydantic import BaseModel

from nexy.http import Request


class Login(BaseModel):
    name: str


async def POST(request: Request, body: Login):
    request.session["user"] = body.name
    return {"user": body.name}
```

एक पृष्ठ इसे `useSession()` के साथ पढ़ता है:

```nexy filename="src/routes/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Hello {{ user }}</h1>
```

## `abort(404)` और त्रुटि संचालक

```python filename="ऐप.पी.ई"
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.get("/posts/<slug>")
def post(slug):
    if slug not in POSTS:
        abort(404)
    return render_template("post.html", post=POSTS[slug])
```

`notFound()` पृष्ठ रोकता है, और `notfound.nexy` उत्तर निकालता है:

```nexy filename="src/routes/posts/[स्लग].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## स्थैतिक फ़ाइलें

```text
static/logo.png        Flask:  /static/logo.png
public/logo.png        Nexy:   /logo.png
```

## कुप्पी-CORS

```python filename="ऐप.पी.ई"
from flask_cors import CORS

CORS(app, origins=["https://example.com"])
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
```

## परीक्षण

```python filename="परीक्षण/test_app.py"
from app import app


def test_hello():
    assert app.test_client().get("/api/hello").json == {"message": "Hello"}
```

```python filename="परीक्षण/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## चल रहा है

| Flask | नेक्सी |
|---|---|
| `flask run --debug` | `nx dev` |
| `gunicorn app:app` | `nx build`, फिर `nx start` |
| `flask db migrate` (फ्लास्क-माइग्रेट) | `nx migrate -m "message"` |
| कोई एपीआई दस्तावेज़ नहीं | `/docs`, प्रत्येक `.py` मार्ग को सूचीबद्ध करते हुए |

## अगले चरण

- [से FastAPI से नेक्सी](fastapi.md): नेक्सी हैंडलर FastAPI हैंडलर हैं
- [क्रियाएँ](../guides/actions.md)
- [.nexy फ़ाइलें](../views/nexy/README.md)
- [रेसिपी](../guides/recipes.md): साइन-इन, सीआरयूडी और अपलोड
