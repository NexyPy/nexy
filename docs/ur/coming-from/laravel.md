# Laravel سے Nexy تک

Nexy میں لاراول روٹ اور اس کا کنٹرولر طریقہ `src/routes/` کے تحت ایک فائل بن جاتا ہے: ایک بلیڈ ویو ایک `.nexy` صفحہ، `$request->validate` ایک Pydantic ماڈل، اور Eloquent ایک ORM جسے آپ منتخب کرتے ہیں، جیسے SQLModel۔

ذیل میں ہر سیکشن Laravel کی عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔

## ایک راستہ

```php filename="routes/api.php"
use Illuminate\Support\Facades\Route;

Route::get('/hello', fn () => ['message' => 'Hello']);
```

کوئی روٹس فائل نہیں ہے: فائل کا راستہ URL ہے، اور فنکشن کا نام طریقہ ہے۔

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## روٹ پیرامیٹرز اور `where`

```php filename="routes/api.php"
Route::get('/users/{id}', fn (int $id) => ['id' => $id])->whereNumber('id');
```

`{id}` ایک `[id]` طبقہ ہے، اور `int` تشریح رکاوٹ ہے: `/api/users/abc` جوابات `404`۔

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

ایک اختیاری `{slug?}` یا `{path}` مماثل سلیش (`->where('path', '.*')`) ایک `[...path].py` کیچ آل ہے۔

## کنٹرولرز

```php filename="app/Http/Controllers/NoteController.php"
class NoteController extends Controller
{
    public function show(int $id) { return ['id' => $id]; }

    public function destroy(int $id) { return ['deleted' => $id]; }
}
```

```php filename="routes/api.php"
Route::get('/notes/{id}', [NoteController::class, 'show']);
Route::delete('/notes/{id}', [NoteController::class, 'destroy']);
```

کنٹرولر طریقے فائل کے افعال ہیں، جن کا نام فعل کے نام پر رکھا گیا ہے:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

انجیکشن سروسز والی کلاسوں کے لیے، جیسا کہ لاراول کنٹرولر میں، [ماڈیولر روٹر](../routing/modular/README.md) دیکھیں۔

## استفسار کے تار

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

## توثیق اور فارم کی درخواستیں۔

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

قواعد ایک Pydantic ماڈل ہیں۔ ایک جسم جو ایک کو توڑتا ہے `422` فیلڈ اور قاعدہ کے ساتھ جواب دیتا ہے، جیسا کہ لارویل کرتا ہے:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## ایک سابقہ اور مڈل ویئر کے ساتھ روٹ گروپس

```php filename="routes/api.php"
Route::prefix('admin')->middleware('admin')->group(function () {
    Route::get('/stats', fn () => ['users' => 3]);
});
```

```php filename="app/Http/Midleware/EnsureAdmin.php"
public function handle(Request $request, Closure $next)
{
    abort_unless($request->header('X-Role') === 'admin', 403, 'Admins only');

    return $next($request);
}
```

فولڈر سابقہ ہے، اور اس کا `dependencies.py` گروپ کا مڈل ویئر ہے:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## عالمی مڈل ویئر

```php filename="app/Http/Midleware/AddAppHeader.php"
public function handle(Request $request, Closure $next)
{
    $response = $next($request);
    $response->headers->set('X-App', 'demo');

    return $response;
}
```

روٹس روٹ پر ایک `middleware.py` ہر درخواست کو سمیٹتا ہے:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## بلیڈ کے نظارے۔

```php filename="routes/web.php"
Route::get('/users', fn () => view('users', ['users' => [['name' => 'Ada'], ['name' => 'Alan']]]));
```

```blade filename="وسائل/views/users.blade.php"
@extends('layouts.app')

@section('content')
<ul>
  @foreach ($users as $user)
  <li>{{ $user['name'] }}</li>
  @endforeach
</ul>
@endsection
```

روٹ اور ویو ایک `.nexy` فائل ہیں:

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

| بلیڈ | Jinja2 `.nexy` میں |
|---|---|
| `{{ $name }}` (فرار) | `{{ name \| e }}`: `.nexy` ڈیفالٹ سے نہیں بچتا |
| `{!! $html !!}` | `{{ html \| safe }}` |
| `@if ($user) ... @endif` | `{% if user %} ... {% endif %}` |
| `@foreach ($items as $item)` | `{% for item in items %}` |
| `@php ... @endphp` | Python سامنے والے معاملے میں |

## لے آؤٹ اور `@yield`

```blade filename="وسائل/views/layouts/app.blade.php"
<!DOCTYPE html>
<html>
  <body>@yield('content')</body>
</html>
```

ایک `layout.nexy` اپنے فولڈر کے ہر صفحے کو سمیٹتا ہے، صفحات میں کوئی `@extends` نہیں:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## بلیڈ کے اجزاء

```blade filename="وسائل/views/components/card.blade.php"
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

`@` ہے `src/`: `nx new` `nexyconfig.py` میں `useAliases = {"@": "src"}` لکھتے ہیں۔

## فارم، `@csrf` اور ری ڈائریکٹ

```blade filename="وسائل/views/notes.blade.php"
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

ایک ایکشن کنٹرولر طریقہ ہے جس پر فارم پوسٹ کیا جاتا ہے۔ اس کے پیرامیٹرز فیلڈز ہیں، اور وزیٹر کامیابی پر `303` کے ساتھ `back()` جاتا ہے:

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

## فصاحت و بلاغت

```php filename="app/Models/Post.php"
class Post extends Model
{
    protected $fillable = ['title', 'published'];
}

$posts = Post::where('published', true)->get();
```

Nexy کا اپنا کوئی ORM نہیں ہے۔ `nx new` سکیفولڈ کر سکتے ہیں SQLModel، SQLAlchemy یا کچھوا-ORM؛ کے ساتھ SQLModel:

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

| کاریگر | نیکسی |
|---|---|
| `php artisan make:migration` | `nx migrate -m "add posts"` |
| `php artisan migrate` | `nx migrate --upgrade` |

دیکھیں [ڈیٹا بیس](../guides/databases.md)۔

## `abort(404)` اور غلطی کے خیالات

```php filename="routes/web.php"
Route::get('/posts/{slug}', function (string $slug) {
    abort_unless(isset(POSTS[$slug]), 404);
    return view('post', ['post' => POSTS[$slug]]);
});
```

`notFound()` ہے `abort(404)`، اور `notfound.nexy` ہے `resources/views/errors/404.blade.php`:

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

## سیشنز

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

ایک صفحہ `useSession()` کے ساتھ سیشن پڑھتا ہے۔

## قطاریں اور `dispatch`

```php filename="app/Http/Controllers/SignupController.php"
SendWelcomeEmail::dispatch($user);

return response()->json(['queued' => true], 202);
```

اس کام کے لیے جو جواب کے بعد چل سکتا ہے، FastAPI کے پس منظر کے کام کافی ہیں:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse

SENT: list[str] = []


def send_welcome_email(email: str) -> None:
    SENT.append(email)


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome_email, email)
    return JSONResponse({"queued": True}, status_code=202)
```

دوسری مشینوں پر دوبارہ کوشش کرنے اور کارکنوں کے لیے، Python قطار کا استعمال کریں جیسے سیلری، RQ یا arq۔

## صفحہ کیش کرنا

```php
Route::get('/blog', BlogController::class)->middleware('cache.headers:public;max_age=60');
```

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

صفحہ فی یو آر ایل کیش کیا جاتا ہے اور 60 سیکنڈ کے بعد پس منظر میں دوبارہ پیش کیا جاتا ہے۔

## `.env` اور `config/`

| لارویل | نیکسی |
|---|---|
| `.env` + `config/database.php` | `.env` `DATABASE_URL` کے ساتھ، `src/configs/db.py` نے پڑھا |
| `config/cors.php` | `useCORS` میں `nexyconfig.py` |
| `APP_KEY` سیشن کے لیے | `useSession = {"secret_key": ...}` |
| `public/` | `public/`، `/` میں خدمت کی |

## لائیو وائر اور جڑتا

Livewire کے سرور سے چلنے والے اجزاء صفحہ سے بلائے گئے اعمال کا نقشہ بناتے ہیں۔ Inertia کے React یا Vue صفحات `.tsx` یا `.vue` راستوں، یا `.nexy` صفحہ کے اندر جزیروں کا نقشہ بناتے ہیں۔ دیکھیں [ایکشنز](../guides/actions.md) اور [جزیرے](../rendering/islands.md)۔

## ٹیسٹ

```php filename="tests/Feature/HelloTest.php"
public function test_hello(): void
{
    $this->getJson('/api/hello')->assertExactJson(['message' => 'Hello']);
}
```

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## چل رہا ہے۔

| لارویل | نیکسی |
|---|---|
| `laravel new` | `nx new` |
| `php artisan serve` | `nx dev` |
| `php artisan route:list` | `/docs` |
| `php artisan test` | `nx test` |
| `npm run build` | `nx build` |

## اگلے اقدامات

- [سے Django سے Nexy](django.md)
- [اعمال](../guides/actions.md)
- [ڈیٹا بیس](../guides/databases.md)
- [.nexy فائلیں](../views/nexy/README.md)
