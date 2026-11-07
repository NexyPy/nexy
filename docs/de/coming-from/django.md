# Von Django zu Nexy

In Nexy werden eine Django-Ansicht und ihre `urls.py`-Zeile zu einer Datei unter `src/routes/`, Vorlagen bleiben Jinja2-ähnlich und ORM, Formulare und Admin sind Ihre Wahl statt integriert.

Jeder Abschnitt unten zeigt eine Django-Gewohnheit, dann dasselbe in Nexy.

## Eine Ansicht und ihre URL

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

Es gibt kein `urls.py`: Der Dateipfad ist die URL, der Funktionsname ist die Methode und ein zurückgegebenes `dict` ist JSON.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Pfadkonverter

```python filename="blog/urls.py"
urlpatterns = [path("api/posts/<int:id>/", views.post_detail)]
```

Der Konverter wird zu einer Typanmerkung für ein `[id]`-Segment:

```python filename="src/routes/api/posts/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` wird zu `[...rest].py`.

## `request.GET` und `request.POST`

```python filename="blog/views.py"
def search(request):
    q = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    return JsonResponse({"q": q, "page": page})
```

Ein Abfrageparameter ist ein Funktionsparameter, konvertiert und validiert:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Klassenbasierte Ansichten

```python filename="blog/views.py"
from django.views import View


class NoteView(View):
    def get(self, request, id):
        return JsonResponse({"id": id})

    def delete(self, request, id):
        return JsonResponse({"deleted": id})
```

Eine Funktion pro Methode in der Datei der URL:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Vorlagen und `render`

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

Die Ansicht und die Vorlage sind eine `.nexy` Datei. Die Tags sind Jinja2, in der Nähe von Django:

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

## `base.html` und `{% block %}`

```html filename="templates/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

Ein `layout.nexy` umschließt jede Seite seines Ordners und darunter, ohne `{% extends %}` in den Seiten:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## `{% include %}` und Einschluss-Tags

```html filename="templates/card.html"
<article><h2>{{ title }}</h2>{{ body }}</article>
```

```html
{% include "card.html" with title="Latest" body="This week" %}
```

Eine Komponente ist eine `.nexy`-Datei mit typisierten Requisiten und einem Slot für ihre untergeordneten Elemente:

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

`@` ist `src/`: `nx new` schreibt `useAliases = {"@": "src"}` in `nexyconfig.py`.

## Vorlagenfilter

| Django | Jinja2 in `.nexy` |
|---|---|
| `{{ name\|default:"guest" }}` | `{{ name or "guest" }}` oder `{{ name \| default("guest") }}` |
| `{{ title\|upper }}` | `{{ title \| upper }}` |
| `{{ body\|safe }}` | `{{ body \| safe }}` |
| `{{ items\|length }}` | `{{ items \| length }}` |
| `{% url "post" post.id %}` | `/posts/{{ post.id }}`: Die URL ist der Dateipfad |

> [!WARNING]
> Django maskiert standardmäßig jeden Wert. `.nexy`-Vorlagen entkommen nicht, was ein Besucher mit `| e` eingegeben hat.

## Modelle und das ORM

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

Nexy hat kein eigenes ORM. `nx new` kann SQLModel, SQLAlchemy oder Tortoise-ORM als Gerüst verwenden; mit SQLModel lesen sich das Modell und die Abfrage so:

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

Siehe [Datenbanken](../guides/databases.md).

## Migrationen

| Django | Nexy |
|---|---|
| `python manage.py makemigrations` | `nx migrate -m "add posts"` |
| `python manage.py migrate` | `nx migrate --upgrade` |

`nx migrate` treibt Alembic für SQLModel und SQLAlchemy und Aerich für Tortoise-ORM.

## Formulare und CSRF

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

Eine Aktion ist die Funktion, an die das Formular sendet. Seine Parameter sind die Formularfelder, und der Besucher wird mit einem `303` auf die Seite zurückgeleitet:

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

Es gibt kein `{% csrf_token %}`: siehe [Aktionen](../guides/actions.md#security), was den Aktionspfad schützt und was Sie noch selbst überprüfen.

## Django Formulare und DRF-Serialisierer

```python filename="blog/serializers.py"
from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    published = serializers.BooleanField(default=False)
```

Ein Pydantic-Modell validiert den Körper und ein ungültiges Modell antwortet `422` mit dem Feld, das fehlgeschlagen ist:

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

Ein `dependencies.py` bewacht einen ganzen Ordner:

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

Sitzungen werden in `nexyconfig.py` eingeschaltet:

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

```python filename="Settings.py"
MIDDLEWARE = [..., "blog.middleware.AppHeaderMiddleware"]
```

Ein `middleware.py` umschließt die Routen seines Ordners; Derjenige an der Wurzel umschließt sie alle:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `Http404` und `404.html`

```python filename="blog/views.py"
from django.shortcuts import get_object_or_404


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "post.html", {"post": post})
```

`notFound()` stoppt die Seite und `notfound.nexy` am Routenstamm übernimmt die Rolle von `404.html`:

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

Eine Zeile im Frontmatter speichert die Seite pro URL zwischen und rendert sie im Hintergrund erneut:

```nexy filename="src/routes/blog/archive.nexy"
---
revalidate = 60
---
<h1>Archive</h1>
```

## `settings.py`

| Django-Einstellung | `nexyconfig.py` |
|---|---|
| `SECRET_KEY` + `SessionMiddleware` | `useSession = {"secret_key": ...}` |
| `ALLOWED_HOSTS` | `useTrustedHost = {"allowed_hosts": [...]}` |
| `SECURE_SSL_REDIRECT` | `useHTTPSRedirect = True` |
| `CORS_ALLOWED_ORIGINS` (Django-Cors-Header) | `useCORS = {"allow_origins": [...]}` |
| `MIDDLEWARE` | `useMiddlewares = [...]`- oder `middleware.py`-Dateien |
| `DATABASES` | `DATABASE_URL` in `.env`, gelesen von `src/configs/db.py` |
| `STATIC_URL`, `STATICFILES_DIRS` | `public/`, zugestellt in `/` |

## Apps

Ein Django Projekt ist in Apps aufgeteilt. In Nexy ist ein Ordner von `src/routes/` die Einheit für URLs, und `src/models/` und `src/services/` enthalten den Code, den sie gemeinsam nutzen. Für Controller und Module mit Abhängigkeitsinjektion ist der [modulare Router](../routing/modular/README.md) die beste Übereinstimmung.

## Der Administrator

Nexy hat keine Admin-Site. Mounten Sie eines der FastAPI Admin-Pakete, z. B. SQLAdmin, oder erstellen Sie die benötigten Seiten aus `.nexy` Dateien und Aktionen.

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

## Laufen

| Django | Nexy |
|---|---|
| `django-admin startproject` | `nx new` |
| `python manage.py runserver` | `nx dev` |
| `gunicorn project.wsgi` | `nx build`, dann `nx start` |
| `python manage.py test` | `nx test` |
| `python manage.py collectstatic` | `nx build` |

## Nächste Schritte

- [Von Flask zu Nexy](flask.md)
- [Datenbanken](../guides/databases.md)
- [Aktionen](../guides/actions.md)
- [Abhängigkeiten und Wachen](../routing/fbr/dependencies/README.md)
