# From Django to Nexy

In Nexy a Django view and its `urls.py` line become one file under `src/routes/`, templates stay
Jinja2-like, and the ORM, forms and admin are your choice instead of built in.

Each section below shows a Django habit, then the same thing in Nexy.

## A view and its URL

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

There is no `urls.py`: the file path is the URL, the function name is the method, and a returned
`dict` is JSON.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Path converters

```python filename="blog/urls.py"
urlpatterns = [path("api/posts/<int:id>/", views.post_detail)]
```

The converter becomes a type annotation on a `[id]` segment:

```python filename="src/routes/api/posts/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` becomes `[...rest].py`.

## `request.GET` and `request.POST`

```python filename="blog/views.py"
def search(request):
    q = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    return JsonResponse({"q": q, "page": page})
```

A query parameter is a function parameter, converted and validated:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Class-based views

```python filename="blog/views.py"
from django.views import View


class NoteView(View):
    def get(self, request, id):
        return JsonResponse({"id": id})

    def delete(self, request, id):
        return JsonResponse({"deleted": id})
```

One function per method, in the file of the URL:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Templates and `render`

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

The view and the template are one `.nexy` file. The tags are Jinja2, close to Django's:

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

## `base.html` and `{% block %}`

```html filename="templates/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

A `layout.nexy` wraps every page of its folder and below, without `{% extends %}` in the pages:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## `{% include %}` and inclusion tags

```html filename="templates/card.html"
<article><h2>{{ title }}</h2>{{ body }}</article>
```

```html
{% include "card.html" with title="Latest" body="This week" %}
```

A component is a `.nexy` file with typed props and a slot for its children:

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

`@` is `src/`: `nx new` writes `useAliases = {"@": "src"}` in `nexyconfig.py`.

## Template filters

| Django | Jinja2 in `.nexy` |
|---|---|
| `{{ name\|default:"guest" }}` | `{{ name or "guest" }}` or `{{ name \| default("guest") }}` |
| `{{ title\|upper }}` | `{{ title \| upper }}` |
| `{{ body\|safe }}` | `{{ body \| safe }}` |
| `{{ items\|length }}` | `{{ items \| length }}` |
| `{% url "post" post.id %}` | `/posts/{{ post.id }}`: the URL is the file path |

> [!WARNING]
> Django escapes every value by default. `.nexy` templates do not: escape what a visitor typed
> with `| e`.

## Models and the ORM

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

Nexy has no ORM of its own. `nx new` can scaffold SQLModel, SQLAlchemy or Tortoise-ORM; with
SQLModel the model and the query read like this:

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

See [Databases](../guides/databases.md).

## Migrations

| Django | Nexy |
|---|---|
| `python manage.py makemigrations` | `nx migrate -m "add posts"` |
| `python manage.py migrate` | `nx migrate --upgrade` |

`nx migrate` drives Alembic for SQLModel and SQLAlchemy, and Aerich for Tortoise-ORM.

## Forms and CSRF

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

An action is the function the form posts to. Its parameters are the form fields, and the visitor is
sent back to the page with a `303`:

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

There is no `{% csrf_token %}`: see [Actions](../guides/actions.md#security) for what protects the
action path, and what you still check yourself.

## Django forms and DRF serializers

```python filename="blog/serializers.py"
from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    published = serializers.BooleanField(default=False)
```

A Pydantic model validates the body, and an invalid one answers `422` with the field that failed:

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

A `dependencies.py` guards a whole folder:

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

Sessions are switched on in `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useAliases = {"@": "src"}
    useSession = {"secret_key": "change-me"}
```

## Middleware

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

A `middleware.py` wraps the routes of its folder; the one at the root wraps them all:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `Http404` and `404.html`

```python filename="blog/views.py"
from django.shortcuts import get_object_or_404


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "post.html", {"post": post})
```

`notFound()` stops the page, and `notfound.nexy` at the routes root plays the role of `404.html`:

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

One line in the frontmatter caches the page per URL and renders it again in the background:

```nexy filename="src/routes/blog/archive.nexy"
---
revalidate = 60
---
<h1>Archive</h1>
```

## `settings.py`

| Django setting | `nexyconfig.py` |
|---|---|
| `SECRET_KEY` + `SessionMiddleware` | `useSession = {"secret_key": ...}` |
| `ALLOWED_HOSTS` | `useTrustedHost = {"allowed_hosts": [...]}` |
| `SECURE_SSL_REDIRECT` | `useHTTPSRedirect = True` |
| `CORS_ALLOWED_ORIGINS` (django-cors-headers) | `useCORS = {"allow_origins": [...]}` |
| `MIDDLEWARE` | `useMiddlewares = [...]`, or `middleware.py` files |
| `DATABASES` | `DATABASE_URL` in `.env`, read by `src/configs/db.py` |
| `STATIC_URL`, `STATICFILES_DIRS` | `public/`, served at `/` |

## Apps

A Django project is split into apps. In Nexy, a folder of `src/routes/` is the unit for URLs, and
`src/models/` and `src/services/` hold the code they share. For controllers and modules with
dependency injection, the [modular router](../routing/modular/README.md) is the closest match.

## The admin

Nexy has no admin site. Mount one of the FastAPI admin packages, such as SQLAdmin, or build the
pages you need from `.nexy` files and actions.

## Tests

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

## Running

| Django | Nexy |
|---|---|
| `django-admin startproject` | `nx new` |
| `python manage.py runserver` | `nx dev` |
| `gunicorn project.wsgi` | `nx build`, then `nx start` |
| `python manage.py test` | `nx test` |
| `python manage.py collectstatic` | `nx build` |

## Next steps

- [From Flask to Nexy](flask.md)
- [Databases](../guides/databases.md)
- [Actions](../guides/actions.md)
- [Dependencies and guards](../routing/fbr/dependencies/README.md)
