# Dari Django hingga Nexy

Di Nexy, tampilan Django dan baris `urls.py`-nya menjadi satu file di bawah `src/routes/`, templat tetap seperti Jinja2, dan ORM, formulir, dan admin adalah pilihan Anda, bukan bawaan.

Setiap bagian di bawah menunjukkan kebiasaan Django, lalu hal yang sama di Nexy.

## Tampilan dan URL-nya

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

Tidak ada `urls.py`: jalur file adalah URL, nama fungsi adalah metodenya, dan `dict` yang dikembalikan adalah JSON.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Konverter jalur

```python filename="blog/urls.py"
urlpatterns = [path("api/posts/<int:id>/", views.post_detail)]
```

Konverter menjadi anotasi tipe pada segmen `[id]`:

```python filename="src/routes/api/posts/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` menjadi `[...rest].py`.

## `request.GET` dan `request.POST`

```python filename="blog/views.py"
def search(request):
    q = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    return JsonResponse({"q": q, "page": page})
```

Parameter kueri adalah parameter fungsi, dikonversi dan divalidasi:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Tampilan berbasis kelas

```python filename="blog/views.py"
from django.views import View


class NoteView(View):
    def get(self, request, id):
        return JsonResponse({"id": id})

    def delete(self, request, id):
        return JsonResponse({"deleted": id})
```

Satu fungsi per metode, dalam file URL:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Templat dan `render`

```python filename="blog/views.py"
from django.shortcuts import render


def post_list(request):
    posts = [{"title": "Hello"}, {"title": "Second"}]
    return render(request, "blog/post_list.html", {"posts": posts})
```

```html filename="blog/templat/blog/post_list.html"
{% extends "base.html" %}
{% block content %}
<ul>
  {% for post in posts %}
  <li>{{ post.title }}</li>
  {% endfor %}
</ul>
{% endblock %}
```

Tampilan dan templatnya adalah satu file `.nexy`. Tagnya adalah Jinja2, dekat dengan Django:

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

## `base.html` dan `{% block %}`

```html filename="templat/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

`layout.nexy` membungkus setiap halaman foldernya dan di bawahnya, tanpa `{% extends %}` di halaman:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## `{% include %}` dan tag penyertaan

```html filename="template/card.html"
<article><h2>{{ title }}</h2>{{ body }}</article>
```

```html
{% include "card.html" with title="Latest" body="This week" %}
```

Komponen adalah file `.nexy` dengan props yang diketik dan slot untuk turunannya:

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
---
<article>
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/rute/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>This week</p>
</Card>
```

`@` adalah `src/`: `nx new` menulis `useAliases = {"@": "src"}` di `nexyconfig.py`.

## Filter templat

| Django | Jinja2 di `.nexy` |
|---|---|
| `{{ name\|default:"guest" }}` | `{{ name or "guest" }}` atau `{{ name \| default("guest") }}` |
| `{{ title\|upper }}` | `{{ title \| upper }}` |
| `{{ body\|safe }}` | `{{ body \| safe }}` |
| `{{ items\|length }}` | `{{ items \| length }}` |
| `{% url "post" post.id %}` | `/posts/{{ post.id }}`: URL adalah jalur file |

> [!WARNING]
> Django lolos dari setiap nilai secara default. Templat `.nexy` tidak: lolos dari apa yang diketik pengunjung dengan `| e`.

## Model dan ORM

```python filename="blog/model.py"
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

Nexy tidak memiliki ORM sendiri. `nx new` dapat perancah SQLModel, SQLAlchemy atau Tortoise-ORM; dengan SQLModel model dan kuerinya berbunyi seperti ini:

```python filename="src/model/post_model.py"
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

Lihat [Database](../guides/databases.md).

## Migrasi

| Django | Nexy |
|---|---|
| `python manage.py makemigrations` | `nx migrate -m "add posts"` |
| `python manage.py migrate` | `nx migrate --upgrade` |

`nx migrate` menggerakkan Alembic untuk SQLModel dan SQLAlchemy, dan Aerich untuk Tortoise-ORM.

## Formulir dan CSRF

```python filename="blog/views.py"
from django.shortcuts import redirect


def add_note(request):
    if request.method == "POST":
        NOTES.append(request.POST["title"])
        return redirect("notes")
    return render(request, "notes.html", {"notes": NOTES})
```

```html filename="blog/template/catatan.html"
<form method="post">
  {% csrf_token %}
  <input name="title">
  <button type="submit">Add</button>
</form>
```

Tindakan adalah fungsi tempat formulir diposting. Parameternya adalah kolom formulir, dan pengunjung dikirim kembali ke halaman dengan `303`:

```python filename="src/tindakan/catatan.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/rute/catatan.nexy"
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

Tidak ada `{% csrf_token %}`: lihat [Tindakan](../guides/actions.md#security) untuk mengetahui apa yang melindungi jalur tindakan, dan apa yang masih Anda periksa sendiri.

## Django formulir dan serializer DRF

```python filename="blog/serializer.py"
from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    published = serializers.BooleanField(default=False)
```

Model Pydantic memvalidasi isi, dan model yang tidak valid menjawab `422` dengan bidang yang gagal:

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

A `dependencies.py` menjaga seluruh folder:

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

Sesi diaktifkan di `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useAliases = {"@": "src"}
    useSession = {"secret_key": "change-me"}
```

## Perangkat Tengah

```python filename="blog/middleware.py"
class AppHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-App"] = "demo"
        return response
```

```python filename="pengaturan.py"
MIDDLEWARE = [..., "blog.middleware.AppHeaderMiddleware"]
```

A `middleware.py` membungkus rute foldernya; yang di root membungkus semuanya:

```python filename="src/rute/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `Http404` dan `404.html`

```python filename="blog/views.py"
from django.shortcuts import get_object_or_404


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "post.html", {"post": post})
```

`notFound()` menghentikan halaman, dan `notfound.nexy` di root rute berperan sebagai `404.html`:

```nexy filename="src/rute/postingan/[siput].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="src/rute/tidak ditemukan.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## `cache_page`

```python filename="blog/views.py"
from django.views.decorators.cache import cache_page


@cache_page(60)
def post_list(request): ...
```

Satu baris di frontmatter menyimpan halaman per URL dan merendernya lagi di latar belakang:

```nexy filename="src/routes/blog/archive.nexy"
---
revalidate = 60
---
<h1>Archive</h1>
```

## `settings.py`

| Django pengaturan | `nexyconfig.py` |
|---|---|
| `SECRET_KEY` + `SessionMiddleware` | `useSession = {"secret_key": ...}` |
| `ALLOWED_HOSTS` | `useTrustedHost = {"allowed_hosts": [...]}` |
| `SECURE_SSL_REDIRECT` | `useHTTPSRedirect = True` |
| `CORS_ALLOWED_ORIGINS` (django-cors-header) | `useCORS = {"allow_origins": [...]}` |
| `MIDDLEWARE` | `useMiddlewares = [...]`, atau `middleware.py` file |
| `DATABASES` | `DATABASE_URL` di `.env`, dibaca oleh `src/configs/db.py` |
| `STATIC_URL`, `STATICFILES_DIRS` | `public/`, bertugas di `/` |

## Aplikasi

Proyek Django dibagi menjadi beberapa aplikasi. Di Nexy, folder `src/routes/` adalah unit untuk URL, dan `src/models/` dan `src/services/` menyimpan kode yang dibagikan. Untuk pengontrol dan modul dengan injeksi ketergantungan, [router modular](../routing/modular/README.md) adalah yang paling cocok.

## Adminnya

Nexy tidak memiliki situs admin. Pasang salah satu paket admin FastAPI, seperti SQLAdmin, atau buat halaman yang Anda perlukan dari `.nexy` file dan tindakan.

## Tes

```python filename="blog/tests.py"
from django.test import TestCase


class HelloTests(TestCase):
    def test_hello(self):
        self.assertEqual(self.client.get("/api/hello/").json(), {"message": "Hello"})
```

```python filename="tes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Berlari

| Django | Nexy |
|---|---|
| `django-admin startproject` | `nx new` |
| `python manage.py runserver` | `nx dev` |
| `gunicorn project.wsgi` | `nx build`, lalu `nx start` |
| `python manage.py test` | `nx test` |
| `python manage.py collectstatic` | `nx build` |

## Langkah selanjutnya

- [Dari Flask hingga Nexy](flask.md)
- [Basis Data](../guides/databases.md)
- [Tindakan](../guides/actions.md)
- [Ketergantungan dan penjaga](../routing/fbr/dependencies/README.md)
