# 从 Django 到 Nexy

在 Nexy 中，Django 视图及其 `urls.py` 行成为 `src/routes/` 下的一个文件，模板与 Jinja2 类似，ORM、表单和管理是您的选择，而不是内置的。

下面的每个部分都显示了一个 Django 习惯，然后 Nexy 中也显示了相同的内容。

## 视图及其 URL

```python filename="博客/views.py"
from django.http import JsonResponse


def hello(request):
    return JsonResponse({"message": "Hello"})
```

```python filename="博客/urls.py"
from django.urls import path

from . import views

urlpatterns = [path("api/hello/", views.hello)]
```

没有 `urls.py`：文件路径是URL，函数名是方法，返回的 `dict` 是JSON。

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## 路径转换器

```python filename="博客/urls.py"
urlpatterns = [path("api/posts/<int:id>/", views.post_detail)]
```

转换器成为 `[id]` 段上的类型注释：

```python filename="src/routes/api/posts/[id].py"
async def GET(id: int):
    return {"id": id}
```

`<path:rest>` 变为 `[...rest].py`。

## `request.GET` 和 `request.POST`

```python filename="博客/views.py"
def search(request):
    q = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    return JsonResponse({"q": q, "page": page})
```

查询参数是一个函数参数，经过转换和验证：

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## 基于类的视图

```python filename="博客/views.py"
from django.views import View


class NoteView(View):
    def get(self, request, id):
        return JsonResponse({"id": id})

    def delete(self, request, id):
        return JsonResponse({"deleted": id})
```

URL 文件中每个方法一个函数：

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

## 模板和 `render`

```python filename="博客/views.py"
from django.shortcuts import render


def post_list(request):
    posts = [{"title": "Hello"}, {"title": "Second"}]
    return render(request, "blog/post_list.html", {"posts": posts})
```

```html filename="博客/模板/博客/post_list.html"
{% extends "base.html" %}
{% block content %}
<ul>
  {% for post in posts %}
  <li>{{ post.title }}</li>
  {% endfor %}
</ul>
{% endblock %}
```

视图和模板是一个 `.nexy` 文件。标签是 Jinja2，接近 Django 的：

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

## `base.html` 和 `{% block %}`

```html filename="模板/base.html"
<!DOCTYPE html>
<html>
  <body>{% block content %}{% endblock %}</body>
</html>
```

`layout.nexy` 包含其文件夹及其下面的每一页，页面中没有 `{% extends %}`：

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## `{% include %}` 和包含标签

```html filename="模板/card.html"
<article><h2>{{ title }}</h2>{{ body }}</article>
```

```html
{% include "card.html" with title="Latest" body="This week" %}
```

组件是一个 `.nexy` 文件，带有类型化的 props 和一个用于其子组件的槽：

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

`@` 是 `src/`：`nx new` 将 `useAliases = {"@": "src"}` 写入 `nexyconfig.py`。

## 模板过滤器

| Django | Jinja2 在 `.nexy` |
|---|---|
| `{{ name\|default:"guest" }}` | `{{ name or "guest" }}` 或 `{{ name \| default("guest") }}` |
| `{{ title\|upper }}` | `{{ title \| upper }}` |
| `{{ body\|safe }}` | `{{ body \| safe }}` |
| `{{ items\|length }}` | `{{ items \| length }}` |
| `{% url "post" post.id %}` | `/posts/{{ post.id }}`：URL是文件路径 |

> [!WARNING]
> Django 默认转义每个值。 `.nexy` 模板不会：转义访问者使用 `| e` 键入的内容。

## 模型和 ORM

```python filename="博客/models.py"
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    published = models.BooleanField(default=False)
```

```python filename="博客/views.py"
def published(request):
    posts = Post.objects.filter(published=True)
    return JsonResponse({"titles": [p.title for p in posts]})
```

Nexy 没有自己的 ORM。 `nx new` 可以支架 SQLModel、SQLAlchemy 或Tortoise-ORM；使用 SQLModel 模型和查询如下所示：

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

请参阅[数据库](../guides/databases.md)。

## 迁移

| Django | 内克西 |
|---|---|
| `python manage.py makemigrations` | `nx migrate -m "add posts"` |
| `python manage.py migrate` | `nx migrate --upgrade` |

`nx migrate` 驱动 SQLModel 和 SQLAlchemy 的 Alembic，以及 Tortoise-ORM 的 Aerich。

## 表格和 CSRF

```python filename="博客/views.py"
from django.shortcuts import redirect


def add_note(request):
    if request.method == "POST":
        NOTES.append(request.POST["title"])
        return redirect("notes")
    return render(request, "notes.html", {"notes": NOTES})
```

```html filename="博客/模板/notes.html"
<form method="post">
  {% csrf_token %}
  <input name="title">
  <button type="submit">Add</button>
</form>
```

操作是表单发布到的函数。它的参数是表单字段，访问者被发送回带有 `303` 的页面：

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

没有 `{% csrf_token %}`：请参阅 [操作](../guides/actions.md#security) 了解什么保护了操作路径，以及您仍然自己检查的内容。

## Django 表单和 DRF 序列化器

```python filename="博客/serializers.py"
from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    published = serializers.BooleanField(default=False)
```

一个 Pydantic 模型验证主体，而一个无效的模型用失败的字段回答 `422`：

```python filename="src/routes/api/posts/index.py"
from pydantic import BaseModel, Field


class NewPost(BaseModel):
    title: str = Field(max_length=200)
    published: bool = False


async def POST(post: NewPost):
    return post
```

## `@login_required`

```python filename="博客/views.py"
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request, "dashboard.html")
```

`dependencies.py` 保护整个文件夹：

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

会话在 `nexyconfig.py` 中打开：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useAliases = {"@": "src"}
    useSession = {"secret_key": "change-me"}
```

## 中间件

```python filename="博客/middleware.py"
class AppHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-App"] = "demo"
        return response
```

```python filename="设置.py"
MIDDLEWARE = [..., "blog.middleware.AppHeaderMiddleware"]
```

`middleware.py` 包装其文件夹的路由；根部的那一个将它们全部包裹起来：

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `Http404` 和 `404.html`

```python filename="博客/views.py"
from django.shortcuts import get_object_or_404


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "post.html", {"post": post})
```

`notFound()` 停止页面，路由根目录的 `notfound.nexy` 扮演 `404.html` 的角色：

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

```python filename="博客/views.py"
from django.views.decorators.cache import cache_page


@cache_page(60)
def post_list(request): ...
```

frontmatter 中的一行缓存每个 URL 的页面并在后台再次呈现它：

```nexy filename="src/routes/blog/archive.nexy"
---
revalidate = 60
---
<h1>Archive</h1>
```

## `settings.py`

| Django 设置 | `nexyconfig.py` |
|---|---|
| `SECRET_KEY` + `SessionMiddleware` | `useSession = {"secret_key": ...}` |
| `ALLOWED_HOSTS` | `useTrustedHost = {"allowed_hosts": [...]}` |
| `SECURE_SSL_REDIRECT` | `useHTTPSRedirect = True` |
| `CORS_ALLOWED_ORIGINS`（django-cors-headers） | `useCORS = {"allow_origins": [...]}` |
| `MIDDLEWARE` | `useMiddlewares = [...]` 或 `middleware.py` 文件 |
| `DATABASES` | `.env` 中的 `DATABASE_URL`，由 `src/configs/db.py` 读取 |
| `STATIC_URL`，`STATICFILES_DIRS` | `public/`，服务于 `/` |

## 应用程序

Django 项目被分成多个应用程序。在 Nexy 中，`src/routes/` 的文件夹是 URL 的单位，`src/models/` 和 `src/services/` 保存它们共享的代码。对于具有依赖注入的控制器和模块，[模块化路由器](../routing/modular/README.md) 是最接近的匹配。

## 管理员

Nexy 没有管理站点。安装 FastAPI 管理包之一，例如 SQLAdmin，或从 `.nexy` 文件和操作构建您需要的页面。

## 测试

```python filename="博客/tests.py"
from django.test import TestCase


class HelloTests(TestCase):
    def test_hello(self):
        self.assertEqual(self.client.get("/api/hello/").json(), {"message": "Hello"})
```

```python filename="测试/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## 跑步

| Django | 内克西 |
|---|---|
| `django-admin startproject` | `nx new` |
| `python manage.py runserver` | `nx dev` |
| `gunicorn project.wsgi` | `nx build`，然后 `nx start` |
| `python manage.py test` | `nx test` |
| `python manage.py collectstatic` | `nx build` |

## 后续步骤

- [从 Flask 到 Nexy](flask.md)
- [数据库](../guides/databases.md)
- [行动](../guides/actions.md)
- [依赖项和守卫](../routing/fbr/dependencies/README.md)
