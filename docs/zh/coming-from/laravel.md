# 从 Laravel 到 Nexy

在 Nexy 中，Laravel 路由及其控制器方法成为 `src/routes/` 下的一个文件：Blade 视图成为 `.nexy` 页面，`$request->validate` 成为 Pydantic 模型，Eloquent 成为您选择的 ORM，例如 SQLModel。

下面的每个部分都显示了 Laravel 的习惯，然后是 Nexy 中的相同内容。

## 一条路线

```php filename="路线/api.php"
use Illuminate\Support\Facades\Route;

Route::get('/hello', fn () => ['message' => 'Hello']);
```

没有路由文件：文件路径是 URL，函数名称是方法。

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## 路由参数和 `where`

```php filename="路线/api.php"
Route::get('/users/{id}', fn (int $id) => ['id' => $id])->whereNumber('id');
```

`{id}` 是 `[id]` 段，`int` 注释是约束：`/api/users/abc` 答案 `404`。

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

可选的 `{slug?}` 或 `{path}` 匹配斜杠 (`->where('path', '.*')`) 是一个 `[...path].py` 包罗万象的东西。

## 控制器

```php filename="应用程序/Http/Controllers/NoteController.php"
class NoteController extends Controller
{
    public function show(int $id) { return ['id' => $id]; }

    public function destroy(int $id) { return ['deleted' => $id]; }
}
```

```php filename="路线/api.php"
Route::get('/notes/{id}', [NoteController::class, 'show']);
Route::delete('/notes/{id}', [NoteController::class, 'destroy']);
```

控制器方法是文件的函数，以动词命名：

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

对于具有注入服务的类，如 Laravel 控制器中的类，请参阅[模块化路由器](../routing/modular/README.md)。

## 查询字符串

```php filename="应用程序/Http/Controllers/SearchController.php"
public function __invoke(Request $request)
{
    return ['q' => $request->query('q', ''), 'page' => (int) $request->query('page', 1)];
}
```

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## 验证和表单请求

```php filename="应用程序/Http/Controllers/ItemController.php"
public function store(Request $request)
{
    $data = $request->validate([
        'name' => 'required|string|max:100',
        'price' => 'required|numeric|gt:0',
    ]);

    return response()->json($data, 201);
}
```

这些规则是一个 Pydantic 模型。一个用字段和规则打破一个答案 `422` 的主体，就像 Laravel 所做的那样：

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## 具有前缀和中间件的路由组

```php filename="路线/api.php"
Route::prefix('admin')->middleware('admin')->group(function () {
    Route::get('/stats', fn () => ['users' => 3]);
});
```

```php filename="应用程序/Http/Middleware/EnsureAdmin.php"
public function handle(Request $request, Closure $next)
{
    abort_unless($request->header('X-Role') === 'admin', 403, 'Admins only');

    return $next($request);
}
```

文件夹是前缀，它的 `dependencies.py` 是组的中间件：

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

```python filename="src/routes/admin/dependency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## 全局中间件

```php filename="应用程序/Http/Middleware/AddAppHeader.php"
public function handle(Request $request, Closure $next)
{
    $response = $next($request);
    $response->headers->set('X-App', 'demo');

    return $response;
}
```

路由根目录处的 `middleware.py` 包装每个请求：

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## 刀片视图

```php filename="路线/web.php"
Route::get('/users', fn () => view('users', ['users' => [['name' => 'Ada'], ['name' => 'Alan']]]));
```

```blade filename="资源/视图/users.blade.php"
@extends('layouts.app')

@section('content')
<ul>
  @foreach ($users as $user)
  <li>{{ $user['name'] }}</li>
  @endforeach
</ul>
@endsection
```

路线和视图是一个 `.nexy` 文件：

```nexy filename="src/routes/users.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

| 刀片 | Jinja2 在 `.nexy` |
|---|---|
| `{{ $name }}`（逃脱） | `{{ name \| e }}`: `.nexy` 默认不转义 |
| `{!! $html !!}` | `{{ html \| safe }}` |
| `@if ($user) ... @endif` | `{% if user %} ... {% endif %}` |
| `@foreach ($items as $item)` | `{% for item in items %}` |
| `@php ... @endphp` | Python 在前面的内容 |

## 布局和 `@yield`

```blade filename="资源/视图/布局/app.blade.php"
<!DOCTYPE html>
<html>
  <body>@yield('content')</body>
</html>
```

`layout.nexy` 包裹其文件夹的每一页，页面中没有 `@extends`：

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## 叶片组件

```blade filename="资源/视图/组件/card.blade.php"
@props(['title'])
<article>
  <h2>{{ $title }}</h2>
  {{ $slot }}
</article>
```

```blade
<x-card title="Latest"><p>This week</p></x-card>
```

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

## 表单、`@csrf` 和重定向

```blade filename="资源/视图/notes.blade.php"
<form method="POST" action="{{ route('notes.store') }}">
  @csrf
  <input name="title">
  <button type="submit">Add</button>
</form>
```

```php filename="应用程序/Http/Controllers/NoteController.php"
public function store(Request $request)
{
    Note::create($request->validate(['title' => 'required']));

    return back();
}
```

操作是表单发布到的控制器方法。它的参数是字段，访问者成功时会转到 `back()` 和 `303`：

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

## 雄辩与迁移

```php filename="应用程序/模型/Post.php"
class Post extends Model
{
    protected $fillable = ['title', 'published'];
}

$posts = Post::where('published', true)->get();
```

Nexy 没有自己的 ORM。 `nx new` 可以搭建 SQLModel、SQLAlchemy 或Tortoise-ORM；与 SQLModel：

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

| 工匠 | 内克西 |
|---|---|
| `php artisan make:migration` | `nx migrate -m "add posts"` |
| `php artisan migrate` | `nx migrate --upgrade` |

请参阅[数据库](../guides/databases.md)。

## `abort(404)` 和错误视图

```php filename="路线/web.php"
Route::get('/posts/{slug}', function (string $slug) {
    abort_unless(isset(POSTS[$slug]), 404);
    return view('post', ['post' => POSTS[$slug]]);
});
```

`notFound()` 是 `abort(404)`，`notfound.nexy` 是 `resources/views/errors/404.blade.php`：

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
```

## 会议

```php filename="应用程序/Http/Controllers/LoginController.php"
public function store(Request $request)
{
    session(['user' => $request->input('name')]);

    return ['user' => session('user')];
}
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useAliases = {"@": "src"}
    useSession = {"secret_key": "change-me"}
```

```python filename="src/routes/api/login.py"
from pydantic import BaseModel

from nexy.http import Request


class Login(BaseModel):
    name: str


async def POST(request: Request, body: Login):
    request.session["user"] = body.name
    return {"user": body.name}
```

页面使用 `useSession()` 读取会话。

## 队列和 `dispatch`

```php filename="应用程序/Http/Controllers/SignupController.php"
SendWelcomeEmail::dispatch($user);

return response()->json(['queued' => true], 202);
```

对于可以在答案后运行的工作，FastAPI 的后台任务就足够了：

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse

SENT: list[str] = []


def send_welcome_email(email: str) -> None:
    SENT.append(email)


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome_email, email)
    return JSONResponse({"queued": True}, status_code=202)
```

对于其他机器上的重试和工作人员，请使用 Python 队列，例如 Celery、RQ 或 arq。

## 缓存页面

```php
Route::get('/blog', BlogController::class)->middleware('cache.headers:public;max_age=60');
```

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

该页面按 URL 进行缓存，并在 60 秒后在后台再次呈现。

## `.env` 和 `config/`

| 拉维尔 | 内克西 |
|---|---|
| `.env` + `config/database.php` | `.env` 与 `DATABASE_URL`，由 `src/configs/db.py` 读取 |
| `config/cors.php` | `useCORS` 在 `nexyconfig.py` |
| `APP_KEY` 会议 | `useSession = {"secret_key": ...}` |
| `public/` | `public/`，服务于 `/` |

## 火线和惯性

Livewire 的服务器驱动组件映射到从页面调用的操作。 Inertia 的 React 或 Vue 页面映射到 `.tsx` 或 `.vue` 路线，或者映射到 `.nexy` 页面内的岛屿。请参阅[操作](../guides/actions.md) 和[岛屿](../rendering/islands.md)。

## 测试

```php filename="测试/功能/HelloTest.php"
public function test_hello(): void
{
    $this->getJson('/api/hello')->assertExactJson(['message' => 'Hello']);
}
```

```python filename="测试/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## 跑步

| 拉维尔 | 内克西 |
|---|---|
| `laravel new` | `nx new` |
| `php artisan serve` | `nx dev` |
| `php artisan route:list` | `/docs` |
| `php artisan test` | `nx test` |
| `npm run build` | `nx build` |

## 后续步骤

- [从 Django 到 Nexy](django.md)
- [行动](../guides/actions.md)
- [数据库](../guides/databases.md)
- [.nexy 文件](../views/nexy/README.md)
