# От Django до Некси

В Nexy представление Django и его строка `urls.py` становятся одним файлом в `src/routes/`, шаблоны остаются похожими на Jinja2, а ORM, формы и администрация - это ваш выбор, а не встроенные.

В каждом разделе ниже показана привычка Django, затем то же самое в Nexy.

## Представление и его URL-адрес

```python filename="блог/views.py"
from django.http import JsonResponse


def hello(request):
    return JsonResponse({"message": "Hello"})
```

```python filename="блог/urls.py"
from django.urls import path

from . import views

urlpatterns = [path("api/hello/", views.hello)]
```

`urls.py` отсутствует: путь к файлу - это URL-адрес, имя функции - это метод, а возвращаемый `dict` - это JSON.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Преобразователи пути

```python filename="блог/urls.py"
urlpatterns = [path("api/posts/<int:id>/", views.post_detail)]
```

Конвертер становится аннотацией типа в сегменте `[id]`:

```python filename="src/routes/api/posts/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` становится `[...rest].py`.

## `request.GET` и `request.POST`

```python filename="блог/views.py"
def search(request):
    q = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    return JsonResponse({"q": q, "page": page})
```

Параметр запроса - это параметр функции, преобразованный и проверенный:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Представления на основе классов

```python filename="блог/views.py"
from django.views import View


class NoteView(View):
    def get(self, request, id):
        return JsonResponse({"id": id})

    def delete(self, request, id):
        return JsonResponse({"deleted": id})
```

Одна функция на метод в файле URL:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## Шаблоны и `render`

```python filename="блог/views.py"
from django.shortcuts import render


def post_list(request):
    posts = [{"title": "Hello"}, {"title": "Second"}]
    return render(request, "blog/post_list.html", {"posts": posts})
```

```html filename="блог/шаблоны/блог/post_list.html"
{% extends "base.html" %}
{% block content %}
<ul>
  {% for post in posts %}
  <li>{{ post.title }}</li>
  {% endfor %}
</ul>
{% endblock %}
```

Представление и шаблон представляют собой один файл `.nexy`. Теги Jinja2 близки к Django:

```nexy filename="src/маршруты/блог/index.nexy"
---
posts = [{"title": "Hello"}, {"title": "Second"}]
---
<ul>
  {% for post in posts %}
  <li>{{ post.title }}</li>
  {% endfor %}
</ul>
```

## `base.html` и `{% block %}`

```html filename="шаблоны/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

`layout.nexy` оборачивает каждую страницу своей папки и ниже, без `{% extends %}` на страницах:

```nexy filename="src/маршруты/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## `{% include %}` и теги включения

```html filename="шаблоны/card.html"
<article><h2>{{ title }}</h2>{{ body }}</article>
```

```html
{% include "card.html" with title="Latest" body="This week" %}
```

Компонент представляет собой файл `.nexy` с типизированными реквизитами и слотом для его дочерних элементов:

```nexy filename="источник/компоненты/Card.nexy"
---
title: prop[str]
---
<article>
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="источник/маршруты/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>This week</p>
</Card>
```

`@` - это `src/`: `nx new` записывает `useAliases = {"@": "src"}` в `nexyconfig.py`.

## Фильтры шаблонов

| Django | Jinja2 в `.nexy` |
|---|---|
| `{{ name\|default:"guest" }}` | `{{ name or "guest" }}` или `{{ name \| default("guest") }}` |
| `{{ title\|upper }}` | `{{ title \| upper }}` |
| `{{ body\|safe }}` | `{{ body \| safe }}` |
| `{{ items\|length }}` | `{{ items \| length }}` |
| `{% url "post" post.id %}` | `/posts/{{ post.id }}`: URL-адрес - это путь к файлу. |

> [!WARNING]
> Django по умолчанию экранирует все значения. Шаблоны `.nexy` не позволяют: экранировать то, что посетитель набрал с помощью `| e`.

## Модели и ORM

```python filename="блог/models.py"
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    published = models.BooleanField(default=False)
```

```python filename="блог/views.py"
def published(request):
    posts = Post.objects.filter(published=True)
    return JsonResponse({"titles": [p.title for p in posts]})
```

У Nexy нет собственного ORM. `nx new` может поддерживать SQLModel, SQLAlchemy или Tortoise-ORM; с SQLModel модель и запрос читаются следующим образом:

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

См. [Базы данных](../guides/databases.md).

## Миграции

| Django | Некси |
|---|---|
| `python manage.py makemigrations` | `nx migrate -m "add posts"` |
| `python manage.py migrate` | `nx migrate --upgrade` |

`nx migrate` управляет Alembic для SQLModel и SQLAlchemy и Aerich для Tortoise-ORM.

## Формы и CSRF

```python filename="блог/views.py"
from django.shortcuts import redirect


def add_note(request):
    if request.method == "POST":
        NOTES.append(request.POST["title"])
        return redirect("notes")
    return render(request, "notes.html", {"notes": NOTES})
```

```html filename="блог/шаблоны/notes.html"
<form method="post">
  {% csrf_token %}
  <input name="title">
  <button type="submit">Add</button>
</form>
```

Действие - это функция, которую отправляет форма. Его параметрами являются поля формы, а посетитель отправляется обратно на страницу с помощью `303`:

```python filename="src/actions/notes.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/маршруты/notes.nexy"
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

`{% csrf_token %}` нет: см. [Действия](../guides/actions.md#security) о том, что защищает путь действия, а что вы еще проверяете сами.

## Django формы и сериализаторы DRF

```python filename="блог/serializers.py"
from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    published = serializers.BooleanField(default=False)
```

Модель Pydantic проверяет тело, а недействительная модель отвечает `422` с полем, которое не удалось:

```python filename="src/routes/api/posts/index.py"
from pydantic import BaseModel, Field


class NewPost(BaseModel):
    title: str = Field(max_length=200)
    published: bool = False


async def POST(post: NewPost):
    return post
```

## `@login_required`

```python filename="блог/views.py"
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request, "dashboard.html")
```

`dependencies.py` охраняет целую папку:

```python filename="src/routes/dashboard/dependents.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized()


dependencies = [require_login]
```

```nexy filename="src/маршруты/панель мониторинга/index.nexy"
---
from nexy import useSession

user = useSession()["user"]
---
<h1>Welcome back, {{ user }}</h1>
```

Сессии включены в `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useAliases = {"@": "src"}
    useSession = {"secret_key": "change-me"}
```

## Промежуточное ПО

```python filename="блог/middleware.py"
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

`middleware.py` оборачивает маршруты своей папки; тот, что в корне, оборачивает их все:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `Http404` и `404.html`

```python filename="блог/views.py"
from django.shortcuts import get_object_or_404


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "post.html", {"post": post})
```

`notFound()` останавливает страницу, а `notfound.nexy` в корне маршрута играет роль `404.html`:

```nexy filename="src/маршруты/сообщения/[слизень].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="источник/маршруты/notfound.nexy"
<h1>Not found</h1>
<p><a href="/">Back home</a></p>
```

## `cache_page`

```python filename="блог/views.py"
from django.views.decorators.cache import cache_page


@cache_page(60)
def post_list(request): ...
```

Одна строка во фронтальной части кэширует страницу для каждого URL-адреса и снова отображает ее в фоновом режиме:

```nexy filename="src/маршруты/блог/archive.nexy"
---
revalidate = 60
---
<h1>Archive</h1>
```

## `settings.py`

| Django настройка | `nexyconfig.py` |
|---|---|
| `SECRET_KEY` + `SessionMiddleware` | `useSession = {"secret_key": ...}` |
| `ALLOWED_HOSTS` | `useTrustedHost = {"allowed_hosts": [...]}` |
| `SECURE_SSL_REDIRECT` | `useHTTPSRedirect = True` |
| `CORS_ALLOWED_ORIGINS` (джанго-корс-заголовки) | `useCORS = {"allow_origins": [...]}` |
| `MIDDLEWARE` | Файлы `useMiddlewares = [...]` или `middleware.py` |
| `DATABASES` | `DATABASE_URL` в `.env`, прочитано `src/configs/db.py` |
| `STATIC_URL`, `STATICFILES_DIRS` | `public/`, служил в `/` |

## Приложения

Проект Django разделен на приложения. В Nexy папка `src/routes/` является единицей URL-адресов, а `src/models/` и `src/services/` содержат общий код. Для контроллеров и модулей с внедрением зависимостей наиболее подходящим является [модульный маршрутизатор](../routing/modular/README.md)].

## Админ

У Nexy нет административного сайта. Подключите один из FastAPI пакетов администратора, например SQLAdmin, или создайте нужные страницы из `.nexy` файлов и действий.

## Тесты

```python filename="блог/tests.py"
from django.test import TestCase


class HelloTests(TestCase):
    def test_hello(self):
        self.assertEqual(self.client.get("/api/hello/").json(), {"message": "Hello"})
```

```python filename="тесты/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Бег

| Django | Некси |
|---|---|
| `django-admin startproject` | `nx new` |
| `python manage.py runserver` | `nx dev` |
| `gunicorn project.wsgi` | `nx build`, затем `nx start` |
| `python manage.py test` | `nx test` |
| `python manage.py collectstatic` | `nx build` |

## Следующие шаги

- [От Flask до Некси](flask.md)
- [Базы данных](../guides/databases.md)
- [Действия](../guides/actions.md)
- [Зависимости и меры защиты](../routing/fbr/dependencies/README.md)
