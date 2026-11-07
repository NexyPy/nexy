# من لارافيل إلى نكسي

في Nexy، يصبح مسار Laravel وطريقة التحكم الخاصة به ملفًا واحدًا ضمن `src/routes/`: يصبح عرض Blade صفحة `.nexy`، و `$request->validate` نموذجًا Pydantic، وEloquent هو ORM تختاره، مثل SQLModel.

يعرض كل قسم أدناه إحدى عادات Laravel، ثم نفس الشيء في Nexy.

## طريق

```php filename="الطرق/api.php"
use Illuminate\Support\Facades\Route;

Route::get('/hello', fn () => ['message' => 'Hello']);
```

لا يوجد ملف مسارات: مسار الملف هو عنوان URL، واسم الوظيفة هو الطريقة.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## معلمات الطريق و `where`

```php filename="الطرق/api.php"
Route::get('/users/{id}', fn (int $id) => ['id' => $id])->whereNumber('id');
```

`{id}` هو مقطع `[id]`، والتعليق `int` هو القيد: `/api/users/abc` يجيب `404`.

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

الشرط المائل الاختياري `{slug?}` أو `{path}` المتطابق (`->where('path', '.*')`) هو `[...path].py` شامل.

## وحدات التحكم

```php filename="app/Http/Controllers/NoteController.php"
class NoteController extends Controller
{
    public function show(int $id) { return ['id' => $id]; }

    public function destroy(int $id) { return ['deleted' => $id]; }
}
```

```php filename="الطرق/api.php"
Route::get('/notes/{id}', [NoteController::class, 'show']);
Route::delete('/notes/{id}', [NoteController::class, 'destroy']);
```

أساليب التحكم هي وظائف الملف، والتي تحمل اسم الفعل:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

بالنسبة للفئات التي تحتوي على خدمات محقونة، كما هو الحال في وحدة تحكم Laravel، راجع [modular router](../routing/modular/README.md).

## سلاسل الاستعلام

```php filename="app/Http/Controllers/SearchController.php"
public function __invoke(Request $request)
{
    return ['q' => $request->query('q', ''), 'page' => (int) $request->query('page', 1)];
}
```

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## التحقق من الصحة وطلبات النموذج

```php filename="app/Http/Controllers/ItemController.php"
public function store(Request $request)
{
    $data = $request->validate([
        'name' => 'required|string|max:100',
        'price' => 'required|numeric|gt:0',
    ]);

    return response()->json($data, 201);
}
```

القواعد نموذج Pydantic . الجسم الذي ينكسر يجيب `422` بالمجال والقاعدة كما يفعل Laravel:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## توجيه المجموعات باستخدام البادئة والبرامج الوسيطة

```php filename="الطرق/api.php"
Route::prefix('admin')->middleware('admin')->group(function () {
    Route::get('/stats', fn () => ['users' => 3]);
});
```

```php filename="app/Http/Middleware/EnsureAdmin.php"
public function handle(Request $request, Closure $next)
{
    abort_unless($request->header('X-Role') === 'admin', 403, 'Admins only');

    return $next($request);
}
```

المجلد هو البادئة، و `dependencies.py` هو الوسيط للمجموعة:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

```python filename="src/routes/admin/dependeency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## الوسيطة العالمية

```php filename="app/Http/Middleware/AddAppHeader.php"
public function handle(Request $request, Closure $next)
{
    $response = $next($request);
    $response->headers->set('X-App', 'demo');

    return $response;
}
```

A `middleware.py` في جذر المسارات يلتف كل طلب:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## وجهات نظر بليد

```php filename="الطرق/web.php"
Route::get('/users', fn () => view('users', ['users' => [['name' => 'Ada'], ['name' => 'Alan']]]));
```

```blade filename="الموارد/المشاهدات/users.blade.php"
@extends('layouts.app')

@section('content')
<ul>
  @foreach ($users as $user)
  <li>{{ $user['name'] }}</li>
  @endforeach
</ul>
@endsection
```

المسار والعرض هما ملف واحد `.nexy`:

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

| بليد | Jinja2 في `.nexy` |
|---|---|
| `{{ $name }}` (هرب) | `{{ name \| e }}`: `.nexy` لا يفلت افتراضيًا |
| `{!! $html !!}` | `{{ html \| safe }}` |
| `@if ($user) ... @endif` | `{% if user %} ... {% endif %}` |
| `@foreach ($items as $item)` | `{% for item in items %}` |
| `@php ... @endphp` | Python في المقدمة |

## التخطيطات و `@yield`

```blade filename="الموارد/طرق العرض/التخطيطات/app.blade.php"
<!DOCTYPE html>
<html>
  <body>@yield('content')</body>
</html>
```

A `layout.nexy` يغلف كل صفحة من المجلد الخاص به، مع عدم وجود `@extends` في الصفحات:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## مكونات الشفرة

```blade filename="الموارد/طرق العرض/المكونات/card.blade.php"
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

`@` هو `src/`: `nx new` يكتب `useAliases = {"@": "src"}` في `nexyconfig.py`.

## النماذج، `@csrf` وإعادة التوجيه

```blade filename="الموارد/المشاهدات/notes.blade.php"
<form method="POST" action="{{ route('notes.store') }}">
  @csrf
  <input name="title">
  <button type="submit">Add</button>
</form>
```

```php filename="app/Http/Controllers/NoteController.php"
public function store(Request $request)
{
    Note::create($request->validate(['title' => 'required']));

    return back();
}
```

الإجراء هو طريقة التحكم التي ينشرها النموذج. معلماته هي الحقول، ويذهب الزائر `back()` بعلامة `303` عند النجاح:

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

## الفصيحة والهجرات

```php filename="التطبيق/النماذج/Post.php"
class Post extends Model
{
    protected $fillable = ['title', 'published'];
}

$posts = Post::where('published', true)->get();
```

Nexy ليس لديه ORM خاص به. `nx new` يمكن أن يكون سقالة SQLModel، SQLAlchemy أو سلحفاة-ORM؛ مع SQLModel:

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

| حرفي | نكسي |
|---|---|
| `php artisan make:migration` | `nx migrate -m "add posts"` |
| `php artisan migrate` | `nx migrate --upgrade` |

انظر [قواعد البيانات](../guides/databases.md).

## `abort(404)` ومشاهد الخطأ

```php filename="الطرق/web.php"
Route::get('/posts/{slug}', function (string $slug) {
    abort_unless(isset(POSTS[$slug]), 404);
    return view('post', ['post' => POSTS[$slug]]);
});
```

`notFound()` هو `abort(404)`، و `notfound.nexy` هو `resources/views/errors/404.blade.php`:

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

## الجلسات

```php filename="app/Http/Controllers/LoginController.php"
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

صفحة تقرأ الجلسة مع `useSession()`.

## طوابير و `dispatch`

```php filename="app/Http/Controllers/SignupController.php"
SendWelcomeEmail::dispatch($user);

return response()->json(['queued' => true], 202);
```

بالنسبة للعمل الذي يمكن تشغيله بعد الإجابة، فإن مهام الخلفية الخاصة بـ FastAPI كافية:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse

SENT: list[str] = []


def send_welcome_email(email: str) -> None:
    SENT.append(email)


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome_email, email)
    return JSONResponse({"queued": True}, status_code=202)
```

بالنسبة لإعادة المحاولة والعاملين على أجهزة أخرى، استخدم قائمة انتظار Python مثل Celery أو RQ أو arq.

## التخزين المؤقت للصفحة

```php
Route::get('/blog', BlogController::class)->middleware('cache.headers:public;max_age=60');
```

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

يتم تخزين الصفحة مؤقتًا لكل عنوان URL ويتم عرضها مرة أخرى في الخلفية بعد 60 ثانية.

## `.env` و `config/`

| لارافيل | نكسي |
|---|---|
| `.env` + `config/database.php` | `.env` مع `DATABASE_URL`، قرأه `src/configs/db.py` |
| `config/cors.php` | `useCORS` في `nexyconfig.py` |
| `APP_KEY` للجلسات | `useSession = {"secret_key": ...}` |
| `public/` | `public/`، خدم في `/` |

## Livewire والقصور الذاتي

تقوم المكونات التي يحركها الخادم في Livewire بتعيين الإجراءات التي يتم استدعاؤها من الصفحة. تحدد صفحات Inertia React أو Vue مسارات `.tsx` أو `.vue`، أو إلى جزر داخل صفحة `.nexy`. انظر [الإجراءات](../guides/actions.md) و [الجزر](../rendering/islands.md).

## الاختبارات

```php filename="الاختبارات/الميزات/HelloTest.php"
public function test_hello(): void
{
    $this->getJson('/api/hello')->assertExactJson(['message' => 'Hello']);
}
```

```python filename="الاختبارات/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## الجري

| لارافيل | نكسي |
|---|---|
| `laravel new` | `nx new` |
| `php artisan serve` | `nx dev` |
| `php artisan route:list` | `/docs` |
| `php artisan test` | `nx test` |
| `npm run build` | `nx build` |

## الخطوات التالية

- [من Django إلى نكسي](django.md)
- [الإجراءات](../guides/actions.md)
- [قواعد البيانات](../guides/databases.md)
- [ملفات .nexy](../views/nexy/README.md)
