# Django سے Nexy تک

Nexy میں ایک Django منظر اور اس کی `urls.py` لائن `src/routes/` کے تحت ایک فائل بن جاتی ہے، ٹیمپلیٹس Jinja2 کی طرح رہتے ہیں، اور ORM، فارمز اور ایڈمن بلٹ ان کے بجائے آپ کی پسند ہیں۔

ذیل میں ہر سیکشن ایک Django عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔

## ایک منظر اور اس کا URL

```python filename="blog/views.py"
from django.http import JsonResponse


def hello(request):
    return JsonResponse({"message": "Hello"})
```

```python filename="blog/urls.py"
from django.urls import path

from . import views

urlpatterns = [path("api/hello/", views.hello)]
```

کوئی `urls.py` نہیں ہے: فائل کا راستہ URL ہے، فنکشن کا نام طریقہ ہے، اور واپس کیا گیا `dict` JSON ہے۔

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## پاتھ کنورٹرز

```python filename="blog/urls.py"
urlpatterns = [path("api/posts/<int:id>/", views.post_detail)]
```

کنورٹر ایک `[id]` سیگمنٹ پر ایک قسم کی تشریح بن جاتا ہے:

```python filename="src/routes/api/posts/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` بن جاتا ہے `[...rest].py`۔

## `request.GET` اور `request.POST`

```python filename="blog/views.py"
def search(request):
    q = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    return JsonResponse({"q": q, "page": page})
```

استفسار پیرامیٹر ایک فنکشن پیرامیٹر ہے، تبدیل شدہ اور توثیق شدہ:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## کلاس پر مبنی خیالات

```python filename="blog/views.py"
from django.views import View


class NoteView(View):
    def get(self, request, id):
        return JsonResponse({"id": id})

    def delete(self, request, id):
        return JsonResponse({"deleted": id})
```

URL کی فائل میں فی طریقہ ایک فنکشن:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## سانچے اور `render`

```python filename="blog/views.py"
from django.shortcuts import render


def post_list(request):
    posts = [{"title": "Hello"}, {"title": "Second"}]
    return render(request, "blog/post_list.html", {"posts": posts})
```

```html filename="blog/templates/blog/post_list.html"
{% extends "base.html" %}
{% block content %}
<ul>
  {% for post in posts %}
  <li>{{ post.title }}</li>
  {% endfor %}
</ul>
{% endblock %}
```

منظر اور سانچہ ایک `.nexy` فائل ہیں۔ ٹیگز Jinja2 ہیں، Django کے قریب:

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

## `base.html` اور `{% block %}`

```html filename="templates/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

A `layout.nexy` اپنے فولڈر کے ہر صفحے کو اور نیچے سمیٹتا ہے، صفحات میں `{% extends %}` کے بغیر:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## `{% include %}` اور شمولیت کے ٹیگ

```html filename="templates/card.html"
<article><h2>{{ title }}</h2>{{ body }}</article>
```

```html
{% include "card.html" with title="Latest" body="This week" %}
```

ایک جزو ایک `.nexy` فائل ہے جس میں ٹائپ شدہ پرپس اور اس کے بچوں کے لیے ایک سلاٹ ہے:

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

`@` ہے `src/`: `nx new` `nexyconfig.py` میں `useAliases = {"@": "src"}` لکھتے ہیں۔

## ٹیمپلیٹ فلٹرز

| Django | Jinja2 میں `.nexy` |
|---|---|
| `{{ name\|default:"guest" }}` | `{{ name or "guest" }}` یا `{{ name \| default("guest") }}` |
| `{{ title\|upper }}` | `{{ title \| upper }}` |
| `{{ body\|safe }}` | `{{ body \| safe }}` |
| `{{ items\|length }}` | `{{ items \| length }}` |
| `{% url "post" post.id %}` | `/posts/{{ post.id }}`: URL فائل کا راستہ ہے۔ |

> [!WARNING]
> Django ڈیفالٹ کے لحاظ سے ہر قدر سے بچ جاتا ہے۔ `.nexy` ٹیمپلیٹس ایسا نہیں کرتے: ایک وزیٹر `| e` کے ساتھ جو ٹائپ کرتا ہے اس سے بچ جاتا ہے۔

## ماڈلز اور ORM

```python filename="blog/models.py"
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    published = models.BooleanField(default=False)
```

```python filename="blog/views.py"
def published(request):
    posts = Post.objects.filter(published=True)
    return JsonResponse({"titles": [p.title for p in posts]})
```

Nexy کا اپنا کوئی ORM نہیں ہے۔ `nx new` سکیفولڈ کر سکتے ہیں SQLModel، SQLAlchemy یا کچھوا-ORM؛ SQLModel کے ساتھ ماڈل اور استفسار اس طرح پڑھا گیا:

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

دیکھیں [ڈیٹا بیس](../guides/databases.md)۔

## ہجرتیں

| Django | نیکسی |
|---|---|
| `python manage.py makemigrations` | `nx migrate -m "add posts"` |
| `python manage.py migrate` | `nx migrate --upgrade` |

`nx migrate` Alembic SQLModel اور SQLAlchemy کے لیے، اور Aerich ٹورٹوائز-ORM کے لیے چلاتا ہے۔

## فارم اور CSRF

```python filename="blog/views.py"
from django.shortcuts import redirect


def add_note(request):
    if request.method == "POST":
        NOTES.append(request.POST["title"])
        return redirect("notes")
    return render(request, "notes.html", {"notes": NOTES})
```

```html filename="blog/templates/notes.html"
<form method="post">
  {% csrf_token %}
  <input name="title">
  <button type="submit">Add</button>
</form>
```

ایک ایکشن وہ فنکشن ہے جسے فارم پوسٹ کرتا ہے۔ اس کے پیرامیٹرز فارم فیلڈز ہیں، اور وزیٹر کو صفحہ پر واپس بھیج دیا جاتا ہے `303`:

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

یہاں کوئی `{% csrf_token %}` نہیں ہے: دیکھیں [ایکشنز](../guides/actions.md#security) اس کے لیے کہ عمل کے راستے کی حفاظت کیا ہے، اور آپ اب بھی اپنے آپ کو کیا جانچتے ہیں۔

## Django فارم اور ڈی آر ایف سیریلائزر

```python filename="blog/serializers.py"
from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    published = serializers.BooleanField(default=False)
```

ایک Pydantic ماڈل جسم کی توثیق کرتا ہے، اور ایک غلط جواب دیتا ہے `422` اس فیلڈ کے ساتھ جو ناکام ہوا:

```python filename="src/routes/api/posts/index.py"
from pydantic import BaseModel, Field


class NewPost(BaseModel):
    title: str = Field(max_length=200)
    published: bool = False


async def POST(post: NewPost):
    return post
```

## `@login_required`

```python filename="blog/views.py"
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request, "dashboard.html")
```

ایک `dependencies.py` پورے فولڈر کی حفاظت کرتا ہے:

```python filename="src/routes/dashboard/dependencies.py"
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

سیشنز کو `nexyconfig.py` میں آن کیا جاتا ہے:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useAliases = {"@": "src"}
    useSession = {"secret_key": "change-me"}
```

## مڈل ویئر

```python filename="blog/middleware.py"
class AppHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-App"] = "demo"
        return response
```

```python filename="settings.py"
MIDDLEWARE = [..., "blog.middleware.AppHeaderMiddleware"]
```

A `middleware.py` اپنے فولڈر کے راستوں کو لپیٹتا ہے۔ جڑ میں والا ان سب کو سمیٹتا ہے:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `Http404` اور `404.html`

```python filename="blog/views.py"
from django.shortcuts import get_object_or_404


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "post.html", {"post": post})
```

`notFound()` صفحہ کو روکتا ہے، اور روٹس پر `notfound.nexy` روٹ `404.html` کا کردار ادا کرتا ہے:

```nexy filename="src/routes/posts/[slug].nexy"
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

```python filename="blog/views.py"
from django.views.decorators.cache import cache_page


@cache_page(60)
def post_list(request): ...
```

فرنٹ میٹر میں ایک لائن صفحہ کو فی یو آر ایل کیش کرتی ہے اور اسے پس منظر میں دوبارہ پیش کرتی ہے:

```nexy filename="src/routes/blog/archive.nexy"
---
revalidate = 60
---
<h1>Archive</h1>
```

## `settings.py`

| Django ترتیب | `nexyconfig.py` |
|---|---|
| `SECRET_KEY` + `SessionMiddleware` | `useSession = {"secret_key": ...}` |
| `ALLOWED_HOSTS` | `useTrustedHost = {"allowed_hosts": [...]}` |
| `SECURE_SSL_REDIRECT` | `useHTTPSRedirect = True` |
| `CORS_ALLOWED_ORIGINS` (django-cors-headers) | `useCORS = {"allow_origins": [...]}` |
| `MIDDLEWARE` | `useMiddlewares = [...]`، یا `middleware.py` فائلیں۔ |
| `DATABASES` | `DATABASE_URL` `.env` میں، `src/configs/db.py` نے پڑھا |
| `STATIC_URL`، `STATICFILES_DIRS` | `public/`، پر خدمت کی `/` |

## ایپس

ایک Django پروجیکٹ ایپس میں تقسیم ہے۔ Nexy میں، `src/routes/` کا ایک فولڈر یو آر ایل کی اکائی ہے، اور `src/models/` اور `src/services/` وہ کوڈ رکھتے ہیں جسے وہ بانٹتے ہیں۔ انحصار انجیکشن والے کنٹرولرز اور ماڈیولز کے لیے، [ماڈیولر روٹر](../routing/modular/README.md) قریب ترین میچ ہے۔

## ایڈمن

Nexy کی کوئی ایڈمن سائٹ نہیں ہے۔ FastAPI ایڈمن پیکجز میں سے ایک کو ماؤنٹ کریں، جیسے کہ SQLAdmin، یا `.nexy` فائلز اور ایکشنز سے آپ کو مطلوبہ صفحات بنائیں۔

## ٹیسٹ

```python filename="blog/tests.py"
from django.test import TestCase


class HelloTests(TestCase):
    def test_hello(self):
        self.assertEqual(self.client.get("/api/hello/").json(), {"message": "Hello"})
```

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## چل رہا ہے۔

| Django | نیکسی |
|---|---|
| `django-admin startproject` | `nx new` |
| `python manage.py runserver` | `nx dev` |
| `gunicorn project.wsgi` | `nx build`، پھر `nx start` |
| `python manage.py test` | `nx test` |
| `python manage.py collectstatic` | `nx build` |

## اگلے اقدامات

- [سے Flask سے Nexy](flask.md)
- [ڈیٹا بیس](../guides/databases.md)
- [اعمال](../guides/actions.md)
- [انحصار اور محافظ](../routing/fbr/dependencies/README.md)
