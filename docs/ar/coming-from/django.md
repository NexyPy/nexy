# من Django إلى النكسي

في Nexy، يصبح العرض Django والسطر `urls.py` الخاص به ملفًا واحدًا ضمن `src/routes/`، وتظل القوالب تشبه Jinja2، كما أن ORM والنماذج والمسؤول هي اختيارك بدلاً من أن تكون مدمجة.

كل قسم أدناه يوضح عادة Django، ثم نفس الشيء في Nexy.

## طريقة العرض وعنوان URL الخاص بها

```python filename="مدونة/views.py"
from django.http import JsonResponse


def hello(request):
    return JsonResponse({"message": "Hello"})
```

```python filename="مدونة/urls.py"
from django.urls import path

from . import views

urlpatterns = [path("api/hello/", views.hello)]
```

لا يوجد `urls.py`: مسار الملف هو عنوان URL، واسم الوظيفة هو الطريقة، و `dict` الذي تم إرجاعه هو JSON.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## محولات المسار

```python filename="مدونة/urls.py"
urlpatterns = [path("api/posts/<int:id>/", views.post_detail)]
```

يصبح المحول تعليقًا توضيحيًا للنوع على مقطع `[id]`:

```python filename="src/routes/api/posts/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` يصبح `[...rest].py`.

## `request.GET` و `request.POST`

```python filename="مدونة/views.py"
def search(request):
    q = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    return JsonResponse({"q": q, "page": page})
```

معلمة الاستعلام هي معلمة دالة، يتم تحويلها والتحقق من صحتها:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## وجهات النظر على أساس الطبقة

```python filename="مدونة/views.py"
from django.views import View


class NoteView(View):
    def get(self, request, id):
        return JsonResponse({"id": id})

    def delete(self, request, id):
        return JsonResponse({"deleted": id})
```

وظيفة واحدة لكل طريقة، في ملف عنوان URL:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## القوالب و `render`

```python filename="مدونة/views.py"
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

العرض والقالب هما ملف `.nexy` واحد. العلامات هي Jinja2، قريبة من Django:

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

## `base.html` و `{% block %}`

```html filename="قوالب/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

A `layout.nexy` يلتف كل صفحة من المجلد الخاص به وما دونه، بدون `{% extends %}` في الصفحات:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## `{% include %}` وعلامات التضمين

```html filename="قوالب/card.html"
<article><h2>{{ title }}</h2>{{ body }}</article>
```

```html
{% include "card.html" with title="Latest" body="This week" %}
```

المكون هو ملف `.nexy` مع دعائم مكتوبة وفتحة لأبناءه:

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

`@` هو `src/`: `nx new` يكتب `useAliases = {"@": "src"}` في `nexyconfig.py`.

## مرشحات القالب

| Django | Jinja2 في `.nexy` |
|---|---|
| `{{ name\|default:"guest" }}` | `{{ name or "guest" }}` أو `{{ name \| default("guest") }}` |
| `{{ title\|upper }}` | `{{ title \| upper }}` |
| `{{ body\|safe }}` | `{{ body \| safe }}` |
| `{{ items\|length }}` | `{{ items \| length }}` |
| `{% url "post" post.id %}` | `/posts/{{ post.id }}`: عنوان URL هو مسار الملف |

> [!WARNING]
> Django يفلت من كل قيمة بشكل افتراضي. `.nexy` القوالب لا: تهرب مما كتبه الزائر بـ `| e`.

## النماذج وORM

```python filename="مدونة/models.py"
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    published = models.BooleanField(default=False)
```

```python filename="مدونة/views.py"
def published(request):
    posts = Post.objects.filter(published=True)
    return JsonResponse({"titles": [p.title for p in posts]})
```

Nexy ليس لديه ORM خاص به. `nx new` يمكنه السقالة SQLModel، SQLAlchemy أو السلحفاة-ORM؛ مع SQLModel يقرأ النموذج والاستعلام كما يلي:

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

انظر [قواعد البيانات](../guides/databases.md).

## الهجرات

| Django | نكسي |
|---|---|
| `python manage.py makemigrations` | `nx migrate -m "add posts"` |
| `python manage.py migrate` | `nx migrate --upgrade` |

`nx migrate` محركات الأقراص Alembic لـ SQLModel و SQLAlchemy، و Aerich لـ Tortoise-ORM.

## النماذج وCSRF

```python filename="مدونة/views.py"
from django.shortcuts import redirect


def add_note(request):
    if request.method == "POST":
        NOTES.append(request.POST["title"])
        return redirect("notes")
    return render(request, "notes.html", {"notes": NOTES})
```

```html filename="مدونة/قوالب/ملاحظات.html"
<form method="post">
  {% csrf_token %}
  <input name="title">
  <button type="submit">Add</button>
</form>
```

الإجراء هو الوظيفة التي ينشرها النموذج. معلماتها هي حقول النموذج، ويتم إرسال الزائر مرة أخرى إلى الصفحة مع `303`:

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

ليس هناك `{% csrf_token %}`: راجع [الإجراءات](../guides/actions.md#security) لما يحمي مسار العمل، وما زلت تفحصه بنفسك.

## Django النماذج ومتسلسلات DRF

```python filename="مدونة/serializers.py"
from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    published = serializers.BooleanField(default=False)
```

نموذج Pydantic يتحقق من صحة النص، ويجيب نموذج غير صالح `422` بالحقل الذي فشل:

```python filename="src/routes/api/posts/index.py"
from pydantic import BaseModel, Field


class NewPost(BaseModel):
    title: str = Field(max_length=200)
    published: bool = False


async def POST(post: NewPost):
    return post
```

## `@login_required`

```python filename="مدونة/views.py"
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request, "dashboard.html")
```

A `dependencies.py` يحرس مجلدًا كاملاً:

```python filename="src/routes/dashboard/dependeency.py"
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

يتم تشغيل الجلسات في `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useAliases = {"@": "src"}
    useSession = {"secret_key": "change-me"}
```

## الوسيطة

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

A `middleware.py` يلتف حول مسارات المجلد الخاص به؛ الذي في الجذر يغلفهم جميعًا:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `Http404` و `404.html`

```python filename="مدونة/views.py"
from django.shortcuts import get_object_or_404


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "post.html", {"post": post})
```

`notFound()` يوقف الصفحة، و `notfound.nexy` عند المسارات يلعب الجذر دور `404.html`:

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

```python filename="مدونة/views.py"
from django.views.decorators.cache import cache_page


@cache_page(60)
def post_list(request): ...
```

يقوم سطر واحد في المادة الأمامية بتخزين الصفحة مؤقتًا لكل عنوان URL ويعرضها مرة أخرى في الخلفية:

```nexy filename="src/routes/blog/archive.nexy"
---
revalidate = 60
---
<h1>Archive</h1>
```

## `settings.py`

| Django الإعداد | `nexyconfig.py` |
|---|---|
| `SECRET_KEY` + `SessionMiddleware` | `useSession = {"secret_key": ...}` |
| `ALLOWED_HOSTS` | `useTrustedHost = {"allowed_hosts": [...]}` |
| `SECURE_SSL_REDIRECT` | `useHTTPSRedirect = True` |
| `CORS_ALLOWED_ORIGINS` (جانغو-كور-رؤوس) | `useCORS = {"allow_origins": [...]}` |
| `MIDDLEWARE` | `useMiddlewares = [...]`، أو `middleware.py` الملفات |
| `DATABASES` | `DATABASE_URL` في `.env`، قرأه `src/configs/db.py` |
| `STATIC_URL`، `STATICFILES_DIRS` | `public/`، خدم في `/` |

## تطبيقات

يتم تقسيم المشروع Django إلى تطبيقات. في Nexy، مجلد `src/routes/` هو وحدة عناوين URL، و `src/models/` و `src/services/` يحتفظان بالرمز الذي يتشاركانه. بالنسبة لوحدات التحكم والوحدات النمطية التي تحتوي على حقن التبعية، فإن [جهاز التوجيه المعياري ](../routing/modular/README.md) هو الأقرب تطابقًا.

## المشرف

لا يوجد لدى Nexy موقع إداري. قم بتحميل إحدى حزم الإدارة FastAPI، مثل SQLAdmin، أو أنشئ الصفحات التي تحتاجها من الملفات والإجراءات `.nexy`.

## الاختبارات

```python filename="مدونة/tests.py"
from django.test import TestCase


class HelloTests(TestCase):
    def test_hello(self):
        self.assertEqual(self.client.get("/api/hello/").json(), {"message": "Hello"})
```

```python filename="الاختبارات/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## الجري

| Django | نكسي |
|---|---|
| `django-admin startproject` | `nx new` |
| `python manage.py runserver` | `nx dev` |
| `gunicorn project.wsgi` | `nx build`، ثم `nx start` |
| `python manage.py test` | `nx test` |
| `python manage.py collectstatic` | `nx build` |

## الخطوات التالية

- [من Flask إلى نكسي](flask.md)
- [قواعد البيانات](../guides/databases.md)
- [الإجراءات](../guides/actions.md)
- [التبعيات والحراس](../routing/fbr/dependencies/README.md)
