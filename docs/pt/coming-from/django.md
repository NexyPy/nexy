# De Django para Nexy

No Nexy, uma visualização Django e sua linha `urls.py` tornam-se um arquivo em `src/routes/`, os modelos permanecem semelhantes ao Jinja2, e o ORM, formulários e administrador são sua escolha, em vez de integrados.

Cada seção abaixo mostra um hábito Django, então a mesma coisa no Nexy.

## Uma visualização e seu URL

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

Não há `urls.py`: o caminho do arquivo é a URL, o nome da função é o método e um `dict` retornado é JSON.

```python filename="src/rotas/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Conversores de caminho

```python filename="blog/urls.py"
urlpatterns = [path("api/posts/<int:id>/", views.post_detail)]
```

O conversor se torna uma anotação de tipo em um segmento `[id]`:

```python filename="src/rotas/api/posts/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` torna-se `[...rest].py`.

## `request.GET` e `request.POST`

```python filename="blog/views.py"
def search(request):
    q = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    return JsonResponse({"q": q, "page": page})
```

Um parâmetro de consulta é um parâmetro de função, convertido e validado:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Visualizações baseadas em classe

```python filename="blog/views.py"
from django.views import View


class NoteView(View):
    def get(self, request, id):
        return JsonResponse({"id": id})

    def delete(self, request, id):
        return JsonResponse({"deleted": id})
```

Uma função por método, no arquivo da URL:

```python filename="src/rotas/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Modelos e `render`

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

A visualização e o modelo são um arquivo `.nexy`. As tags são Jinja2, próximas de Django:

```nexy filename="src/rotas/blog/index.nexy"
---
posts = [{"title": "Hello"}, {"title": "Second"}]
---
<ul>
  {% for post in posts %}
  <li>{{ post.title }}</li>
  {% endfor %}
</ul>
```

## `base.html` e `{% block %}`

```html filename="modelos/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

Um `layout.nexy` envolve todas as páginas de sua pasta e abaixo, sem `{% extends %}` nas páginas:

```nexy filename="src/rotas/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## `{% include %}` e tags de inclusão

```html filename="modelos/cartão.html"
<article><h2>{{ title }}</h2>{{ body }}</article>
```

```html
{% include "card.html" with title="Latest" body="This week" %}
```

Um componente é um arquivo `.nexy` com adereços digitados e um slot para seus filhos:

```nexy filename="src/componentes/Card.nexy"
---
title: prop[str]
---
<article>
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/rotas/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>This week</p>
</Card>
```

`@` é `src/`: `nx new` escreve `useAliases = {"@": "src"}` em `nexyconfig.py`.

## Filtros de modelo

| Django | Jinja2 em `.nexy` |
|---|---|
| `{{ name\|default:"guest" }}` | `{{ name or "guest" }}` ou `{{ name \| default("guest") }}` |
| `{{ title\|upper }}` | `{{ title \| upper }}` |
| `{{ body\|safe }}` | `{{ body \| safe }}` |
| `{{ items\|length }}` | `{{ items \| length }}` |
| `{% url "post" post.id %}` | `/posts/{{ post.id }}`: o URL é o caminho do arquivo |

> [!WARNING]
> Django escapa de todos os valores por padrão. Os modelos `.nexy` não: escapam do que um visitante digitou com `| e`.

## Modelos e o ORM

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

Nexy não possui ORM próprio. `nx new` pode criar andaime SQLModel, SQLAlchemy ou Tortoise-ORM; com SQLModel o modelo e a consulta são assim:

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

Consulte [Bancos de dados](../guides/databases.md).

## Migrações

| Django | Nexy |
|---|---|
| `python manage.py makemigrations` | `nx migrate -m "add posts"` |
| `python manage.py migrate` | `nx migrate --upgrade` |

`nx migrate` unidades Alembic para SQLModel e SQLAlchemy, e Aerich para Tortoise-ORM.

## Formulários e CSRF

```python filename="blog/views.py"
from django.shortcuts import redirect


def add_note(request):
    if request.method == "POST":
        NOTES.append(request.POST["title"])
        return redirect("notes")
    return render(request, "notes.html", {"notes": NOTES})
```

```html filename="blog/modelos/notas.html"
<form method="post">
  {% csrf_token %}
  <input name="title">
  <button type="submit">Add</button>
</form>
```

Uma ação é a função para a qual o formulário é postado. Seus parâmetros são os campos do formulário, e o visitante é enviado de volta à página com um `303`:

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

Não há `{% csrf_token %}`: veja [Ações](../guides/actions.md#security) para saber o que protege o caminho da ação e o que você ainda verifica por si mesmo.

## Django formulários e serializadores DRF

```python filename="blog/serializers.py"
from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    published = serializers.BooleanField(default=False)
```

Um modelo Pydantic valida o corpo, e um inválido responde `422` com o campo que falhou:

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

Um `dependencies.py` protege uma pasta inteira:

```python filename="src/routes/dashboard/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized()


dependencies = [require_login]
```

```nexy filename="src/rotas/dashboard/index.nexy"
---
from nexy import useSession

user = useSession()["user"]
---
<h1>Welcome back, {{ user }}</h1>
```

As sessões são ativadas em `nexyconfig.py`:

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

```python filename="configurações.py"
MIDDLEWARE = [..., "blog.middleware.AppHeaderMiddleware"]
```

Um `middleware.py` agrupa as rotas de sua pasta; aquele na raiz envolve todos eles:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `Http404` e `404.html`

```python filename="blog/views.py"
from django.shortcuts import get_object_or_404


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "post.html", {"post": post})
```

`notFound()` para a página e `notfound.nexy` na raiz da rota desempenha o papel de `404.html`:

```nexy filename="src/rotas/posts/[slug].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="src/rotas/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## `cache_page`

```python filename="blog/views.py"
from django.views.decorators.cache import cache_page


@cache_page(60)
def post_list(request): ...
```

Uma linha no frontmatter armazena em cache a página por URL e a renderiza novamente em segundo plano:

```nexy filename="src/routes/blog/archive.nexy"
---
revalidate = 60
---
<h1>Archive</h1>
```

## `settings.py`

| Configuração Django | `nexyconfig.py` |
|---|---|
| `SECRET_KEY` + `SessionMiddleware` | `useSession = {"secret_key": ...}` |
| `ALLOWED_HOSTS` | `useTrustedHost = {"allowed_hosts": [...]}` |
| `SECURE_SSL_REDIRECT` | `useHTTPSRedirect = True` |
| `CORS_ALLOWED_ORIGINS` (cabeçalhos django-cors) | `useCORS = {"allow_origins": [...]}` |
| `MIDDLEWARE` | `useMiddlewares = [...]` ou `middleware.py` arquivos |
| `DATABASES` | `DATABASE_URL` em `.env`, lido por `src/configs/db.py` |
| `STATIC_URL`, `STATICFILES_DIRS` | `public/`, servido em `/` |

## Aplicativos

Um projeto Django é dividido em aplicativos. No Nexy, uma pasta de `src/routes/` é a unidade para URLs, e `src/models/` e `src/services/` contêm o código que eles compartilham. Para controladores e módulos com injeção de dependência, o [roteador modular](../routing/modular/README.md) é a correspondência mais próxima.

## O administrador

Nexy não tem site de administração. Monte um dos FastAPI pacotes de administração, como SQLAdmin, ou crie as páginas necessárias a partir de `.nexy` arquivos e ações.

## Testes

```python filename="blog/testes.py"
from django.test import TestCase


class HelloTests(TestCase):
    def test_hello(self):
        self.assertEqual(self.client.get("/api/hello/").json(), {"message": "Hello"})
```

```python filename="testes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Correndo

| Django | Nexy |
|---|---|
| `django-admin startproject` | `nx new` |
| `python manage.py runserver` | `nx dev` |
| `gunicorn project.wsgi` | `nx build`, então `nx start` |
| `python manage.py test` | `nx test` |
| `python manage.py collectstatic` | `nx build` |

## Próximas etapas

- [De Flask para Nexy](flask.md)
- [Bancos de dados](../guides/databases.md)
- [Ações](../guides/actions.md)
- [Dependências e guardas](../routing/fbr/dependencies/README.md)
