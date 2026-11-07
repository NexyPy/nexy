# De Django à Nexy

Dans Nexy, une vue Django et sa ligne `urls.py` deviennent un seul fichier sous `src/routes/`, les modèles restent similaires à Jinja2, et l'ORM, les formulaires et l'administrateur sont votre choix au lieu d'être intégrés.

Chaque section ci-dessous montre une habitude Django, puis la même chose dans Nexy.

## Une vue et son URL

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

Il n'y a pas de `urls.py` : le chemin du fichier est l'URL, le nom de la fonction est la méthode et un `dict` renvoyé est JSON.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Convertisseurs de chemin

```python filename="blog/urls.py"
urlpatterns = [path("api/posts/<int:id>/", views.post_detail)]
```

Le convertisseur devient une annotation de type sur un segment `[id]` :

```python filename="src/routes/api/posts/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` devient `[...rest].py`.

## `request.GET` et `request.POST`

```python filename="blog/views.py"
def search(request):
    q = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    return JsonResponse({"q": q, "page": page})
```

Un paramètre de requête est un paramètre de fonction, converti et validé :

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Vues basées sur les classes

```python filename="blog/views.py"
from django.views import View


class NoteView(View):
    def get(self, request, id):
        return JsonResponse({"id": id})

    def delete(self, request, id):
        return JsonResponse({"deleted": id})
```

Une fonction par méthode, dans le fichier de l'URL :

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Modèles et `render`

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

La vue et le modèle forment un seul fichier `.nexy`. Les balises sont des Jinja2, proches de celles de Django :

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

## `base.html` et `{% block %}`

```html filename="modèles/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

Un `layout.nexy` enveloppe chaque page de son dossier et au-dessous, sans `{% extends %}` dans les pages :

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## `{% include %}` et balises d'inclusion

```html filename="modèles/carte.html"
<article><h2>{{ title }}</h2>{{ body }}</article>
```

```html
{% include "card.html" with title="Latest" body="This week" %}
```

Un composant est un fichier `.nexy` avec des accessoires typés et un emplacement pour ses enfants :

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

`@` est `src/` : `nx new` écrit `useAliases = {"@": "src"}` dans `nexyconfig.py`.

## Filtres de modèles

| Django | Jinja2 dans `.nexy` |
|---|---|
| `{{ name\|default:"guest" }}` | `{{ name or "guest" }}` ou `{{ name \| default("guest") }}` |
| `{{ title\|upper }}` | `{{ title \| upper }}` |
| `{{ body\|safe }}` | `{{ body \| safe }}` |
| `{{ items\|length }}` | `{{ items \| length }}` |
| `{% url "post" post.id %}` | `/posts/{{ post.id }}` : l'URL est le chemin du fichier |

> [!WARNING]
> Django échappe à chaque valeur par défaut. Les modèles `.nexy` ne permettent pas : d'échapper à ce qu'un visiteur a tapé avec `| e`.

## Les modèles et l'ORM

```python filename="blog/modèles.py"
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

Nexy n'a pas d'ORM propre. `nx new` peut échafauder SQLModel, SQLAlchemy ou Tortoise-ORM ; avec SQLModel le modèle et la requête se lisent comme ceci :

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

Voir [Bases de données](../guides/databases.md).

## Migrations

| Django | Nexy |
|---|---|
| `python manage.py makemigrations` | `nx migrate -m "add posts"` |
| `python manage.py migrate` | `nx migrate --upgrade` |

`nx migrate` entraîne Alembic pour SQLModel et SQLAlchemy, et Aerich pour Tortoise-ORM.

## Formulaires et CSRF

```python filename="blog/views.py"
from django.shortcuts import redirect


def add_note(request):
    if request.method == "POST":
        NOTES.append(request.POST["title"])
        return redirect("notes")
    return render(request, "notes.html", {"notes": NOTES})
```

```html filename="blog/modèles/notes.html"
<form method="post">
  {% csrf_token %}
  <input name="title">
  <button type="submit">Add</button>
</form>
```

Une action est la fonction sur laquelle le formulaire est publié. Ses paramètres sont les champs du formulaire, et le visiteur est renvoyé vers la page avec un `303` :

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

Il n'y a pas de `{% csrf_token %}` : voir [Actions](../guides/actions.md#security) pour savoir ce qui protège le chemin d'action et ce que vous vérifiez toujours vous-même.

## Django formulaires et sérialiseurs DRF

```python filename="blog/sérialiseurs.py"
from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    published = serializers.BooleanField(default=False)
```

Un modèle Pydantic valide le corps, et un modèle invalide répond `422` avec le champ qui a échoué :

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

Un `dependencies.py` garde un dossier entier :

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

Les sessions sont activées dans `nexyconfig.py` :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useAliases = {"@": "src"}
    useSession = {"secret_key": "change-me"}
```

## Intergiciel

```python filename="blog/middleware.py"
class AppHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-App"] = "demo"
        return response
```

```python filename="paramètres.py"
MIDDLEWARE = [..., "blog.middleware.AppHeaderMiddleware"]
```

Un `middleware.py` enveloppe les routes de son dossier ; celui à la racine les enveloppe tous :

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `Http404` et `404.html`

```python filename="blog/views.py"
from django.shortcuts import get_object_or_404


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "post.html", {"post": post})
```

`notFound()` arrête la page, et `notfound.nexy` à la racine des routes joue le rôle de `404.html` :

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

Une ligne dans le frontmatter met en cache la page par URL et la restitue à nouveau en arrière-plan :

```nexy filename="src/routes/blog/archive.nexy"
---
revalidate = 60
---
<h1>Archive</h1>
```

## `settings.py`

| réglage Django | `nexyconfig.py` |
|---|---|
| `SECRET_KEY` + `SessionMiddleware` | `useSession = {"secret_key": ...}` |
| `ALLOWED_HOSTS` | `useTrustedHost = {"allowed_hosts": [...]}` |
| `SECURE_SSL_REDIRECT` | `useHTTPSRedirect = True` |
| `CORS_ALLOWED_ORIGINS` (django-cors-en-têtes) | `useCORS = {"allow_origins": [...]}` |
| `MIDDLEWARE` | Fichiers `useMiddlewares = [...]` ou `middleware.py` |
| `DATABASES` | `DATABASE_URL` dans `.env`, lu par `src/configs/db.py` |
| `STATIC_URL`, `STATICFILES_DIRS` | `public/`, servi à `/` |

## Applications

Un projet Django est divisé en applications. Dans Nexy, un dossier de `src/routes/` est l'unité des URL, et `src/models/` et `src/services/` contiennent le code qu'ils partagent. Pour les contrôleurs et les modules avec injection de dépendances, le [routeur modulaire](../routing/modular/README.md) est la correspondance la plus proche.

## L'administrateur

Nexy n'a pas de site d'administration. Montez l'un des FastAPI packages d'administration, tels que SQLAdmin, ou créez les pages dont vous avez besoin à partir de `.nexy` fichiers et actions.

## Essais

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

## Courir

| Django | Nexy |
|---|---|
| `django-admin startproject` | `nx new` |
| `python manage.py runserver` | `nx dev` |
| `gunicorn project.wsgi` | `nx build`, puis `nx start` |
| `python manage.py test` | `nx test` |
| `python manage.py collectstatic` | `nx build` |

## Prochaines étapes

- [De Flask à Nexy](flask.md)
- [Bases de données](../guides/databases.md)
- [Actions](../guides/actions.md)
- [Dépendances et gardiens](../routing/fbr/dependencies/README.md)
