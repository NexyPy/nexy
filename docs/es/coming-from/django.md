# De Django a Nexy

En Nexy, una vista Django y su línea `urls.py` se convierten en un archivo en `src/routes/`, las plantillas permanecen como Jinja2 y el ORM, los formularios y el administrador son su elección en lugar de estar integrados.

Cada sección a continuación muestra un hábito Django, luego lo mismo en Nexy.

## Una vista y su URL

```python filename="blog/vistas.py"
from django.http import JsonResponse


def hello(request):
    return JsonResponse({"message": "Hello"})
```

```python filename="blog/url.py"
from django.urls import path

from . import views

urlpatterns = [path("api/hello/", views.hello)]
```

No hay `urls.py`: la ruta del archivo es la URL, el nombre de la función es el método y un `dict` devuelto es JSON.

```python filename="src/rutas/api/hola.py"
async def GET():
    return {"message": "Hello"}
```

## Convertidores de ruta

```python filename="blog/url.py"
urlpatterns = [path("api/posts/<int:id>/", views.post_detail)]
```

El convertidor se convierte en una anotación de tipo en un segmento `[id]`:

```python filename="src/rutas/api/posts/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` se convierte en `[...rest].py`.

## `request.GET` y `request.POST`

```python filename="blog/vistas.py"
def search(request):
    q = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    return JsonResponse({"q": q, "page": page})
```

Un parámetro de consulta es un parámetro de función, convertido y validado:

```python filename="src/rutas/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Vistas basadas en clases

```python filename="blog/vistas.py"
from django.views import View


class NoteView(View):
    def get(self, request, id):
        return JsonResponse({"id": id})

    def delete(self, request, id):
        return JsonResponse({"deleted": id})
```

Una función por método, en el archivo de la URL:

```python filename="src/rutas/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Plantillas y `render`

```python filename="blog/vistas.py"
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

La vista y la plantilla son un archivo `.nexy`. Las etiquetas son Jinja2, cercanas a las de Django:

```nexy filename="src/rutas/blog/index.nexy"
---
posts = [{"title": "Hello"}, {"title": "Second"}]
---
<ul>
  {% for post in posts %}
  <li>{{ post.title }}</li>
  {% endfor %}
</ul>
```

## `base.html` y `{% block %}`

```html filename="plantillas/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

Un `layout.nexy` envuelve cada página de su carpeta y debajo, sin `{% extends %}` en las páginas:

```nexy filename="src/rutas/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## `{% include %}` y etiquetas de inclusión

```html filename="plantillas/tarjeta.html"
<article><h2>{{ title }}</h2>{{ body }}</article>
```

```html
{% include "card.html" with title="Latest" body="This week" %}
```

Un componente es un archivo `.nexy` con accesorios escritos y una ranura para sus hijos:

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
---
<article>
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/rutas/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>This week</p>
</Card>
```

`@` es `src/`: `nx new` escribe `useAliases = {"@": "src"}` en `nexyconfig.py`.

## Filtros de plantilla

| Django | Jinja2 en `.nexy` |
|---|---|
| `{{ name\|default:"guest" }}` | `{{ name or "guest" }}` o `{{ name \| default("guest") }}` |
| `{{ title\|upper }}` | `{{ title \| upper }}` |
| `{{ body\|safe }}` | `{{ body \| safe }}` |
| `{{ items\|length }}` | `{{ items \| length }}` |
| `{% url "post" post.id %}` | `/posts/{{ post.id }}`: la URL es la ruta del archivo |

> [!WARNING]
> Django escapa de todos los valores de forma predeterminada. Las plantillas `.nexy` no: escapan de lo que un visitante escribió con `| e`.

## Modelos y ORM

```python filename="blog/modelos.py"
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    published = models.BooleanField(default=False)
```

```python filename="blog/vistas.py"
def published(request):
    posts = Post.objects.filter(published=True)
    return JsonResponse({"titles": [p.title for p in posts]})
```

Nexy no tiene ORM propio. `nx new` puede andamiar SQLModel, SQLAlchemy o Tortoise-ORM; con SQLModel el modelo y la consulta se leen así:

```python filename="src/modelos/post_model.py"
from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    published: bool = False
```

```python filename="src/rutas/api/posts/published.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.post_model import Post


async def GET():
    with Session(engine) as session:
        posts = session.exec(select(Post).where(Post.published)).all()
    return {"titles": [post.title for post in posts]}
```

Consulte [Bases de datos](../guides/databases.md).

## Migraciones

| Django | nexy |
|---|---|
| `python manage.py makemigrations` | `nx migrate -m "add posts"` |
| `python manage.py migrate` | `nx migrate --upgrade` |

`nx migrate` maneja Alembic para SQLModel y SQLAlchemy, y Aerich para Tortoise-ORM.

## Formularios y CSRF

```python filename="blog/vistas.py"
from django.shortcuts import redirect


def add_note(request):
    if request.method == "POST":
        NOTES.append(request.POST["title"])
        return redirect("notes")
    return render(request, "notes.html", {"notes": NOTES})
```

```html filename="blog/plantillas/notas.html"
<form method="post">
  {% csrf_token %}
  <input name="title">
  <button type="submit">Add</button>
</form>
```

Una acción es la función en la que se publica el formulario. Sus parámetros son los campos del formulario y el visitante regresa a la página con un `303`:

```python filename="src/acciones/notas.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/rutas/notas.nexy"
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

No hay `{% csrf_token %}`: consulte [Acciones](../guides/actions.md#security) para saber qué protege la ruta de acción y qué aún verifica usted mismo.

## Django formularios y serializadores DRF

```python filename="blog/serializadores.py"
from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    published = serializers.BooleanField(default=False)
```

Un modelo Pydantic valida el cuerpo, y uno no válido responde `422` con el campo que falló:

```python filename="src/rutas/api/posts/index.py"
from pydantic import BaseModel, Field


class NewPost(BaseModel):
    title: str = Field(max_length=200)
    published: bool = False


async def POST(post: NewPost):
    return post
```

## `@login_required`

```python filename="blog/vistas.py"
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request, "dashboard.html")
```

Un `dependencies.py` guarda una carpeta completa:

```python filename="src/rutas/dashboard/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized()


dependencies = [require_login]
```

```nexy filename="src/rutas/dashboard/index.nexy"
---
from nexy import useSession

user = useSession()["user"]
---
<h1>Welcome back, {{ user }}</h1>
```

Las sesiones se activan en `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useAliases = {"@": "src"}
    useSession = {"secret_key": "change-me"}
```

## software intermedio

```python filename="blog/middleware.py"
class AppHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-App"] = "demo"
        return response
```

```python filename="configuración.py"
MIDDLEWARE = [..., "blog.middleware.AppHeaderMiddleware"]
```

Un `middleware.py` envuelve las rutas de su carpeta; el de la raíz los envuelve a todos:

```python filename="src/rutas/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `Http404` y `404.html`

```python filename="blog/vistas.py"
from django.shortcuts import get_object_or_404


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "post.html", {"post": post})
```

`notFound()` detiene la página, y `notfound.nexy` en la raíz de rutas desempeña el papel de `404.html`:

```nexy filename="src/rutas/publicaciones/[slug].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="src/rutas/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## `cache_page`

```python filename="blog/vistas.py"
from django.views.decorators.cache import cache_page


@cache_page(60)
def post_list(request): ...
```

Una línea en la portada almacena en caché la página por URL y la muestra nuevamente en segundo plano:

```nexy filename="src/rutas/blog/archive.nexy"
---
revalidate = 60
---
<h1>Archive</h1>
```

## `settings.py`

| Django ajuste | `nexyconfig.py` |
|---|---|
| `SECRET_KEY` + `SessionMiddleware` | `useSession = {"secret_key": ...}` |
| `ALLOWED_HOSTS` | `useTrustedHost = {"allowed_hosts": [...]}` |
| `SECURE_SSL_REDIRECT` | `useHTTPSRedirect = True` |
| `CORS_ALLOWED_ORIGINS` (django-cors-encabezados) | `useCORS = {"allow_origins": [...]}` |
| `MIDDLEWARE` | Archivos `useMiddlewares = [...]` o `middleware.py` |
| `DATABASES` | `DATABASE_URL` en `.env`, leído por `src/configs/db.py` |
| `STATIC_URL`, `STATICFILES_DIRS` | `public/`, servido en `/` |

## Aplicaciones

Un proyecto Django se divide en aplicaciones. En Nexy, una carpeta de `src/routes/` es la unidad para las URL, y `src/models/` y `src/services/` contienen el código que comparten. Para controladores y módulos con inyección de dependencia, el [enrutador modular](../routing/modular/README.md) es la coincidencia más cercana.

## el administrador

Nexy no tiene un sitio de administración. Monte uno de los FastAPI paquetes de administración, como SQLAdmin, o cree las páginas que necesita a partir de `.nexy` archivos y acciones.

## Pruebas

```python filename="blog/pruebas.py"
from django.test import TestCase


class HelloTests(TestCase):
    def test_hello(self):
        self.assertEqual(self.client.get("/api/hello/").json(), {"message": "Hello"})
```

```python filename="pruebas/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## corriendo

| Django | nexy |
|---|---|
| `django-admin startproject` | `nx new` |
| `python manage.py runserver` | `nx dev` |
| `gunicorn project.wsgi` | `nx build`, luego `nx start` |
| `python manage.py test` | `nx test` |
| `python manage.py collectstatic` | `nx build` |

## Próximos pasos

- [De Flask a Nexy](flask.md)
- [Bases de datos](../guides/databases.md)
- [Acciones](../guides/actions.md)
- [Dependencias y guardias](../routing/fbr/dependencies/README.md)
