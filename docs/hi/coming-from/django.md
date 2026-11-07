# Django से नेक्सी तक

नेक्सी में एक Django दृश्य और उसकी `urls.py` लाइन `src/routes/` के अंतर्गत एक फ़ाइल बन जाती है, टेम्पलेट जिंजा2 की तरह रहते हैं, और ओआरएम, फॉर्म और एडमिन बिल्ट-इन के बजाय आपकी पसंद हैं।

नीचे प्रत्येक अनुभाग एक Django आदत दिखाता है, फिर नेक्सी में भी वही चीज़।

## एक दृश्य और उसका URL

```python filename="ब्लॉग/views.py"
from django.http import JsonResponse


def hello(request):
    return JsonResponse({"message": "Hello"})
```

```python filename="ब्लॉग/urls.py"
from django.urls import path

from . import views

urlpatterns = [path("api/hello/", views.hello)]
```

कोई `urls.py` नहीं है: फ़ाइल पथ यूआरएल है, फ़ंक्शन नाम विधि है, और लौटाया गया `dict` JSON है।

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## पथ परिवर्तक

```python filename="ब्लॉग/urls.py"
urlpatterns = [path("api/posts/<int:id>/", views.post_detail)]
```

कनवर्टर `[id]` सेगमेंट पर एक प्रकार का एनोटेशन बन जाता है:

```python filename="src/routes/api/posts/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` बन जाता है `[...rest].py`।

## `request.GET` और `request.POST`

```python filename="ब्लॉग/views.py"
def search(request):
    q = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    return JsonResponse({"q": q, "page": page})
```

एक क्वेरी पैरामीटर एक फ़ंक्शन पैरामीटर है, जिसे परिवर्तित और मान्य किया गया है:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## वर्ग आधारित विचार

```python filename="ब्लॉग/views.py"
from django.views import View


class NoteView(View):
    def get(self, request, id):
        return JsonResponse({"id": id})

    def delete(self, request, id):
        return JsonResponse({"deleted": id})
```

URL की फ़ाइल में, प्रति विधि एक फ़ंक्शन:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## टेम्प्लेट और `render`

```python filename="ब्लॉग/views.py"
from django.shortcuts import render


def post_list(request):
    posts = [{"title": "Hello"}, {"title": "Second"}]
    return render(request, "blog/post_list.html", {"posts": posts})
```

```html filename="ब्लॉग/टेम्पलेट्स/ब्लॉग/पोस्ट_लिस्ट.html"
{% extends "base.html" %}
{% block content %}
<ul>
  {% for post in posts %}
  <li>{{ post.title }}</li>
  {% endfor %}
</ul>
{% endblock %}
```

दृश्य और टेम्पलेट एक `.nexy` फ़ाइल हैं। टैग Jinja2 हैं, Django के करीब:

```nexy filename="src/routes/blog/index.nexy"
---
posts = [{"title": "Hello"}, {"title": "Second"}]
---
<ul>
  {% for post in posts %}
  <li>{{ post.title }}</li>
  {% endfor %}
</ul>
```

## `base.html` और `{% block %}`

```html filename="टेम्प्लेट/बेस.एचटीएमएल"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

एक `layout.nexy` अपने फ़ोल्डर के प्रत्येक पृष्ठ को लपेटता है और नीचे, पृष्ठों में `{% extends %}` के बिना:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## `{% include %}` और समावेशन टैग

```html filename="टेम्प्लेट/कार्ड.एचटीएमएल"
<article><h2>{{ title }}</h2>{{ body }}</article>
```

```html
{% include "card.html" with title="Latest" body="This week" %}
```

एक घटक एक `.nexy` फ़ाइल है जिसमें टाइप किए गए प्रॉप्स और उसके बच्चों के लिए एक स्लॉट है:

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
  <p>This week</p>
</Card>
```

`@` है `src/`: `nx new` `nexyconfig.py` में `useAliases = {"@": "src"}` लिखता है।

## टेम्पलेट फ़िल्टर

| Django | Jinja2 में `.nexy` |
|---|---|
| `{{ name\|default:"guest" }}` | `{{ name or "guest" }}` या `{{ name \| default("guest") }}` |
| `{{ title\|upper }}` | `{{ title \| upper }}` |
| `{{ body\|safe }}` | `{{ body \| safe }}` |
| `{{ items\|length }}` | `{{ items \| length }}` |
| `{% url "post" post.id %}` | `/posts/{{ post.id }}`: यूआरएल फ़ाइल पथ है |

> [!WARNING]
> Django डिफ़ॉल्ट रूप से हर मान से बच जाता है। `.nexy` टेम्प्लेट किसी विज़िटर द्वारा `| e` से टाइप किए जाने से बच नहीं सकते।

## मॉडल और ORM

```python filename="ब्लॉग/models.py"
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    published = models.BooleanField(default=False)
```

```python filename="ब्लॉग/views.py"
def published(request):
    posts = Post.objects.filter(published=True)
    return JsonResponse({"titles": [p.title for p in posts]})
```

नेक्सी का अपना कोई ORM नहीं है। `nx new` मचान बना सकता है SQLModel, SQLAlchemy या कछुआ-ओआरएम; SQLModel के साथ मॉडल और क्वेरी इस प्रकार पढ़ें:

```python filename="src/models/post_model.py"
from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    published: bool = False
```

```python filename="src/routes/api/posts/published.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.post_model import Post


async def GET():
    with Session(engine) as session:
        posts = session.exec(select(Post).where(Post.published)).all()
    return {"titles": [post.title for post in posts]}
```

[डेटाबेस](../guides/databases.md) देखें।

## पलायन

| Django | नेक्सी |
|---|---|
| `python manage.py makemigrations` | `nx migrate -m "add posts"` |
| `python manage.py migrate` | `nx migrate --upgrade` |

`nx migrate` SQLModel और SQLAlchemy के लिए Alembic, और टोर्टोइज़-ओआरएम के लिए Aerich ड्राइव करता है।

## फॉर्म और सीएसआरएफ

```python filename="ब्लॉग/views.py"
from django.shortcuts import redirect


def add_note(request):
    if request.method == "POST":
        NOTES.append(request.POST["title"])
        return redirect("notes")
    return render(request, "notes.html", {"notes": NOTES})
```

```html filename="ब्लॉग/टेम्पलेट्स/नोट्स.html"
<form method="post">
  {% csrf_token %}
  <input name="title">
  <button type="submit">Add</button>
</form>
```

क्रिया वह फ़ंक्शन है जिस पर प्रपत्र पोस्ट करता है। इसके पैरामीटर फॉर्म फ़ील्ड हैं, और विज़िटर को `303` के साथ पृष्ठ पर वापस भेजा जाता है:

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

कोई `{% csrf_token %}` नहीं है: कार्रवाई पथ की सुरक्षा के लिए [क्रियाएँ](../guides/actions.md#security) देखें, और जिसे आप अभी भी स्वयं जांचते हैं।

## Django फॉर्म और डीआरएफ सीरिएलाइज़र

```python filename="ब्लॉग/serializers.py"
from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    published = serializers.BooleanField(default=False)
```

एक Pydantic मॉडल बॉडी को मान्य करता है, और एक अमान्य मॉडल `422` को उस फ़ील्ड के साथ उत्तर देता है जो विफल रही:

```python filename="src/routes/api/posts/index.py"
from pydantic import BaseModel, Field


class NewPost(BaseModel):
    title: str = Field(max_length=200)
    published: bool = False


async def POST(post: NewPost):
    return post
```

## `@login_required`

```python filename="ब्लॉग/views.py"
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request, "dashboard.html")
```

एक `dependencies.py` पूरे फ़ोल्डर की सुरक्षा करता है:

```python filename="src/routes/डैशबोर्ड/निर्भरता.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized()


dependencies = [require_login]
```

```nexy filename="src/routes/dashboard/index.nexy"
---
from nexy import useSession

user = useSession()["user"]
---
<h1>Welcome back, {{ user }}</h1>
```

`nexyconfig.py` में सत्र चालू हैं:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useAliases = {"@": "src"}
    useSession = {"secret_key": "change-me"}
```

## मिडलवेयर

```python filename="ब्लॉग/middleware.py"
class AppHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-App"] = "demo"
        return response
```

```python filename="सेटिंग्स.py"
MIDDLEWARE = [..., "blog.middleware.AppHeaderMiddleware"]
```

एक `middleware.py` अपने फ़ोल्डर के मार्गों को लपेटता है; जड़ में मौजूद व्यक्ति उन सभी को लपेटता है:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `Http404` और `404.html`

```python filename="ब्लॉग/views.py"
from django.shortcuts import get_object_or_404


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "post.html", {"post": post})
```

`notFound()` पृष्ठ को रोकता है, और `notfound.nexy` रूट पर `404.html` की भूमिका निभाता है:

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

## `cache_page`

```python filename="ब्लॉग/views.py"
from django.views.decorators.cache import cache_page


@cache_page(60)
def post_list(request): ...
```

फ्रंटमैटर में एक पंक्ति प्रति यूआरएल पेज को कैश करती है और इसे पृष्ठभूमि में फिर से प्रस्तुत करती है:

```nexy filename="src/routes/blog/archive.nexy"
---
revalidate = 60
---
<h1>Archive</h1>
```

## `settings.py`

| Django सेटिंग | `nexyconfig.py` |
|---|---|
| `SECRET_KEY` + `SessionMiddleware` | `useSession = {"secret_key": ...}` |
| `ALLOWED_HOSTS` | `useTrustedHost = {"allowed_hosts": [...]}` |
| `SECURE_SSL_REDIRECT` | `useHTTPSRedirect = True` |
| `CORS_ALLOWED_ORIGINS` (django-cors-headers) | `useCORS = {"allow_origins": [...]}` |
| `MIDDLEWARE` | `useMiddlewares = [...]`, या `middleware.py` फ़ाइलें |
| `DATABASES` | `DATABASE_URL` में `.env`, `src/configs/db.py` द्वारा पढ़ा गया |
| `STATIC_URL`, `STATICFILES_DIRS` | `public/`, `/` में सेवा दी गई |

## ऐप्स

एक Django प्रोजेक्ट ऐप्स में विभाजित है। नेक्सी में, `src/routes/` का एक फ़ोल्डर यूआरएल के लिए इकाई है, और `src/models/` और `src/services/` उनके द्वारा साझा किए गए कोड को रखते हैं। निर्भरता इंजेक्शन वाले नियंत्रकों और मॉड्यूल के लिए, [मॉड्यूलर राउटर ](../routing/modular/README.md) निकटतम मिलान है।

## व्यवस्थापक

नेक्सी की कोई एडमिन साइट नहीं है. FastAPI एडमिन पैकेजों में से किसी एक को माउंट करें, जैसे कि SQLAdmin, या `.nexy` फ़ाइलों और क्रियाओं से अपनी ज़रूरत के पेज बनाएं।

## परीक्षण

```python filename="ब्लॉग/tests.py"
from django.test import TestCase


class HelloTests(TestCase):
    def test_hello(self):
        self.assertEqual(self.client.get("/api/hello/").json(), {"message": "Hello"})
```

```python filename="परीक्षण/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## चल रहा है

| Django | नेक्सी |
|---|---|
| `django-admin startproject` | `nx new` |
| `python manage.py runserver` | `nx dev` |
| `gunicorn project.wsgi` | `nx build`, फिर `nx start` |
| `python manage.py test` | `nx test` |
| `python manage.py collectstatic` | `nx build` |

## अगले चरण

- [से Flask से नेक्सी](flask.md)
- [डेटाबेस](../guides/databases.md)
- [क्रियाएँ](../guides/actions.md)
- [निर्भरताएँ और रक्षक](../routing/fbr/dependencies/README.md)
