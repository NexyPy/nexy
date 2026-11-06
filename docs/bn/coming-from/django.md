# Django থেকে নেক্সি পর্যন্ত

Nexy-এ একটি Django ভিউ এবং এর `urls.py` লাইনটি `src/routes/` এর অধীনে একটি ফাইলে পরিণত হয়, টেমপ্লেটগুলি জিনজা2-এর মতো থাকে এবং বিল্ট-ইন করার পরিবর্তে ORM, ফর্ম এবং অ্যাডমিন আপনার পছন্দ।

নীচের প্রতিটি বিভাগ একটি Django অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস।

## একটি ভিউ এবং এর URL

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

এখানে কোন `urls.py` নেই: ফাইল পাথ হল URL, ফাংশনের নাম হল পদ্ধতি, এবং একটি ফেরত `dict` হল JSON।

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## পাথ রূপান্তরকারী

```python filename="blog/urls.py"
urlpatterns = [path("api/posts/<int:id>/", views.post_detail)]
```

রূপান্তরকারী একটি `[id]` বিভাগে একটি টাইপ টীকা হয়ে যায়:

```python filename="src/routes/api/posts/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` হয়ে যায় `[...rest].py`।

## `request.GET` এবং `request.POST`

```python filename="blog/views.py"
def search(request):
    q = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    return JsonResponse({"q": q, "page": page})
```

একটি ক্যোয়ারী প্যারামিটার হল একটি ফাংশন প্যারামিটার, রূপান্তরিত এবং বৈধ:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## ক্লাস ভিত্তিক দৃষ্টিভঙ্গি

```python filename="blog/views.py"
from django.views import View


class NoteView(View):
    def get(self, request, id):
        return JsonResponse({"id": id})

    def delete(self, request, id):
        return JsonResponse({"deleted": id})
```

URL এর ফাইলে প্রতি পদ্ধতিতে একটি ফাংশন:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## টেমপ্লেট এবং `render`

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

ভিউ এবং টেমপ্লেট একটি `.nexy` ফাইল। ট্যাগগুলি হল Jinja2, Django এর কাছাকাছি:

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

## `base.html` এবং `{% block %}`

```html filename="templates/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

একটি `layout.nexy` পৃষ্ঠাগুলিতে `{% extends %}` ছাড়াই তার ফোল্ডারের প্রতিটি পৃষ্ঠা এবং নীচে মোড়ানো হয়:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## `{% include %}` এবং অন্তর্ভুক্তি ট্যাগ

```html filename="templates/card.html"
<article><h2>{{ title }}</h2>{{ body }}</article>
```

```html
{% include "card.html" with title="Latest" body="This week" %}
```

একটি উপাদান হল একটি `.nexy` ফাইল যাতে টাইপ করা প্রপস এবং একটি স্লট থাকে তার বাচ্চাদের জন্য:

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

`@` হল `src/`: `nx new` লিখেছেন `useAliases = {"@": "src"}` `nexyconfig.py`।

## টেমপ্লেট ফিল্টার

| Django | Jinja2 `.nexy` মধ্যে |
|---|---|
| `{{ name\|default:"guest" }}` | `{{ name or "guest" }}` বা `{{ name \| default("guest") }}` |
| `{{ title\|upper }}` | `{{ title \| upper }}` |
| `{{ body\|safe }}` | `{{ body \| safe }}` |
| `{{ items\|length }}` | `{{ items \| length }}` |
| `{% url "post" post.id %}` | `/posts/{{ post.id }}`: URL হল ফাইল পাথ |

> [!WARNING]
> Django ডিফল্টরূপে প্রতিটি মান এড়িয়ে যায়। `.nexy` টেমপ্লেটগুলি করে না: একজন দর্শক `| e` দিয়ে যা টাইপ করেছেন তা এড়িয়ে যান।

## মডেল এবং ORM

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

Nexy এর নিজস্ব কোন ORM নেই। `nx new` ভারা হতে পারে SQLModel, SQLAlchemy বা কচ্ছপ-ORM; SQLModel মডেল এবং ক্যোয়ারী এই মত পড়া:

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

[ডেটাবেস](../guides/databases.md) দেখুন।

## মাইগ্রেশন

| Django | নেক্সি |
|---|---|
| `python manage.py makemigrations` | `nx migrate -m "add posts"` |
| `python manage.py migrate` | `nx migrate --upgrade` |

`nx migrate` চালায় Alembic জন্য SQLModel এবং SQLAlchemy, এবং Aerich কচ্ছপ-ORM-এর জন্য।

## ফর্ম এবং CSRF

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

একটি কর্ম হল ফর্ম পোস্ট করার ফাংশন। এর প্যারামিটারগুলি হল ফর্ম ক্ষেত্র, এবং ভিজিটরকে একটি `303` সহ পৃষ্ঠায় ফেরত পাঠানো হয়:

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

এখানে কোন `{% csrf_token %}` নেই: দেখুন [ক্রিয়াগুলি](../guides/actions.md#security) যা কর্ম পথকে রক্ষা করে, এবং আপনি এখনও নিজেকে কী পরীক্ষা করেন।

## Django ফর্ম এবং ডিআরএফ সিরিয়ালাইজার

```python filename="blog/serializers.py"
from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    published = serializers.BooleanField(default=False)
```

একটি Pydantic মডেল শরীরকে বৈধ করে, এবং একটি অবৈধ একটি উত্তর দেয় `422` যে ক্ষেত্রে ব্যর্থ হয়েছে:

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

একটি `dependencies.py` একটি সম্পূর্ণ ফোল্ডার রক্ষা করে:

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

সেশনগুলি `nexyconfig.py`-এ চালু করা হয়েছে:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useAliases = {"@": "src"}
    useSession = {"secret_key": "change-me"}
```

## মিডলওয়্যার

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

একটি `middleware.py` এর ফোল্ডারের রুটগুলি মোড়ানো হয়; মূলে থাকা একজন তাদের সব গুটিয়ে রাখে:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `Http404` এবং `404.html`

```python filename="blog/views.py"
from django.shortcuts import get_object_or_404


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "post.html", {"post": post})
```

`notFound()` পৃষ্ঠাটিকে থামায়, এবং `notfound.nexy` রুটে রুট `404.html` এর ভূমিকা পালন করে:

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

ফ্রন্টম্যাটারে একটি লাইন প্রতি ইউআরএল পৃষ্ঠাটিকে ক্যাশ করে এবং এটিকে আবার পটভূমিতে রেন্ডার করে:

```nexy filename="src/routes/blog/archive.nexy"
---
revalidate = 60
---
<h1>Archive</h1>
```

## `settings.py`

| Django সেটিং | `nexyconfig.py` |
|---|---|
| `SECRET_KEY` + `SessionMiddleware` | `useSession = {"secret_key": ...}` |
| `ALLOWED_HOSTS` | `useTrustedHost = {"allowed_hosts": [...]}` |
| `SECURE_SSL_REDIRECT` | `useHTTPSRedirect = True` |
| `CORS_ALLOWED_ORIGINS` (জ্যাঙ্গো-কর্স-হেডার) | `useCORS = {"allow_origins": [...]}` |
| `MIDDLEWARE` | `useMiddlewares = [...]`, বা `middleware.py` ফাইল |
| `DATABASES` | `DATABASE_URL` `.env` মধ্যে, `src/configs/db.py` দ্বারা পঠিত |
| `STATIC_URL`, `STATICFILES_DIRS` | `public/`, `/` এ পরিবেশিত |

## অ্যাপস

একটি Django প্রকল্প অ্যাপগুলিতে বিভক্ত। Nexy-এ, `src/routes/`-এর একটি ফোল্ডার হল URL-এর একক, এবং `src/models/` এবং `src/services/` তাদের শেয়ার করা কোড ধারণ করে। নির্ভরতা ইনজেকশন সহ কন্ট্রোলার এবং মডিউলগুলির জন্য, [মডুলার রাউটার](../routing/modular/README.md) সবচেয়ে কাছের মিল।

## অ্যাডমিন

Nexy কোন অ্যাডমিন সাইট আছে. একটি FastAPI অ্যাডমিন প্যাকেজ মাউন্ট করুন, যেমন SQLAdmin, অথবা `.nexy` ফাইল এবং অ্যাকশন থেকে আপনার প্রয়োজনীয় পৃষ্ঠাগুলি তৈরি করুন।

## টেস্ট

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

## চলছে

| Django | নেক্সি |
|---|---|
| `django-admin startproject` | `nx new` |
| `python manage.py runserver` | `nx dev` |
| `gunicorn project.wsgi` | `nx build`, তারপর `nx start` |
| `python manage.py test` | `nx test` |
| `python manage.py collectstatic` | `nx build` |

## পরবর্তী পদক্ষেপ

- [থেকে Flask নেক্সি থেকে](flask.md)
- [ডাটাবেস](../guides/databases.md)
- [কর্ম](../guides/actions.md)
- [নির্ভরতা এবং প্রহরী](../routing/fbr/dependencies/README.md)
