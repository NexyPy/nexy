# লারাভেল থেকে নেক্সি পর্যন্ত

নেক্সিতে একটি লারাভেল রুট এবং এর কন্ট্রোলার পদ্ধতি `src/routes/` এর অধীনে একটি ফাইল হয়ে যায়: একটি ব্লেড ভিউ একটি `.nexy` পৃষ্ঠা, `$request->validate` একটি Pydantic মডেল, এবং আপনার বেছে নেওয়া একটি ওআরএম যেমন SQLModel।

নীচের প্রতিটি বিভাগ একটি Laravel অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস।

## একটি রুট

```php filename="রুট/api.php"
use Illuminate\Support\Facades\Route;

Route::get('/hello', fn () => ['message' => 'Hello']);
```

কোন রুট ফাইল নেই: ফাইল পাথ হল URL, এবং ফাংশনের নাম হল পদ্ধতি।

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## রুট প্যারামিটার এবং `where`

```php filename="রুট/api.php"
Route::get('/users/{id}', fn (int $id) => ['id' => $id])->whereNumber('id');
```

`{id}` হল একটি `[id]` সেগমেন্ট, এবং `int` টীকা হল সীমাবদ্ধতা: `/api/users/abc` উত্তর দেয় `404`।

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

একটি ঐচ্ছিক `{slug?}` বা একটি `{path}` ম্যাচিং স্ল্যাশ (`->where('path', '.*')`) হল একটি `[...path].py` ক্যাচ-অল।

## কন্ট্রোলার

```php filename="app/Http/Controllers/NoteController.php"
class NoteController extends Controller
{
    public function show(int $id) { return ['id' => $id]; }

    public function destroy(int $id) { return ['deleted' => $id]; }
}
```

```php filename="রুট/api.php"
Route::get('/notes/{id}', [NoteController::class, 'show']);
Route::delete('/notes/{id}', [NoteController::class, 'destroy']);
```

কন্ট্রোলার পদ্ধতি হল ফাইলের ফাংশন, ক্রিয়াটির নামকরণ করা হয়েছে:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

লারাভেল কন্ট্রোলারের মতো ইনজেকশন পরিষেবা সহ ক্লাসের জন্য, [মডুলার রাউটার](../routing/modular/README.md) দেখুন।

## প্রশ্ন স্ট্রিং

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

## বৈধতা এবং ফর্ম অনুরোধ

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

নিয়ম একটি Pydantic মডেল। একটি শরীর যা একজনকে ক্ষেত্র এবং নিয়মের সাথে উত্তর দেয় `422`, যেমন লারাভেল করে:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## একটি উপসর্গ এবং মিডলওয়্যার সহ রুট গ্রুপ

```php filename="রুট/api.php"
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

ফোল্ডারটি হল উপসর্গ, এবং এর `dependencies.py` হল গ্রুপের মিডলওয়্যার:

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

## গ্লোবাল মিডলওয়্যার

```php filename="app/Http/Middleware/AddAppHeader.php"
public function handle(Request $request, Closure $next)
{
    $response = $next($request);
    $response->headers->set('X-App', 'demo');

    return $response;
}
```

রুট রুটে একটি `middleware.py` প্রতিটি অনুরোধ মোড়ানো হয়:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## ব্লেড ভিউ

```php filename="রুট/web.php"
Route::get('/users', fn () => view('users', ['users' => [['name' => 'Ada'], ['name' => 'Alan']]]));
```

```blade filename="resource/views/users.blade.php"
@extends('layouts.app')

@section('content')
<ul>
  @foreach ($users as $user)
  <li>{{ $user['name'] }}</li>
  @endforeach
</ul>
@endsection
```

রুট এবং ভিউ একটি `.nexy` ফাইল:

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

| ব্লেড | Jinja2 `.nexy` মধ্যে |
|---|---|
| `{{ $name }}` (পলায়ন) | `{{ name \| e }}`: `.nexy` ডিফল্টরূপে অব্যাহতি পায় না |
| `{!! $html !!}` | `{{ html \| safe }}` |
| `@if ($user) ... @endif` | `{% if user %} ... {% endif %}` |
| `@foreach ($items as $item)` | `{% for item in items %}` |
| `@php ... @endphp` | Python ফ্রন্ট ম্যাটারে |

## বিন্যাস এবং `@yield`

```blade filename="resource/views/layouts/app.blade.php"
<!DOCTYPE html>
<html>
  <body>@yield('content')</body>
</html>
```

একটি `layout.nexy` তার ফোল্ডারের প্রতিটি পৃষ্ঠাকে মুড়ে দেয়, পৃষ্ঠাগুলিতে `@extends` নেই:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## ব্লেড উপাদান

```blade filename="resource/views/components/card.blade.php"
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

`@` হল `src/`: `nx new` লিখেছেন `useAliases = {"@": "src"}` `nexyconfig.py`।

## ফর্ম, `@csrf` এবং পুনঃনির্দেশ

```blade filename="resource/views/notes.blade.php"
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

একটি কর্ম হল নিয়ামক পদ্ধতি যা ফর্ম পোস্ট করে। এর পরামিতিগুলি হল ক্ষেত্র, এবং দর্শক সাফল্যের উপর `303` সহ `back()` যায়:

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

## বাগ্মী এবং দেশান্তর

```php filename="app/Models/Post.php"
class Post extends Model
{
    protected $fillable = ['title', 'published'];
}

$posts = Post::where('published', true)->get();
```

Nexy এর নিজস্ব কোন ORM নেই। `nx new` ভারা হতে পারে SQLModel, SQLAlchemy বা কচ্ছপ-ORM; সঙ্গে SQLModel:

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

| কারিগর | নেক্সি |
|---|---|
| `php artisan make:migration` | `nx migrate -m "add posts"` |
| `php artisan migrate` | `nx migrate --upgrade` |

[ডেটাবেস](../guides/databases.md) দেখুন।

## `abort(404)` এবং ত্রুটি দেখা

```php filename="রুট/web.php"
Route::get('/posts/{slug}', function (string $slug) {
    abort_unless(isset(POSTS[$slug]), 404);
    return view('post', ['post' => POSTS[$slug]]);
});
```

`notFound()` হল `abort(404)`, এবং `notfound.nexy` হল `resources/views/errors/404.blade.php`:

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

## সেশন

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

একটি পৃষ্ঠা `useSession()` সহ অধিবেশনটি পড়ে।

## সারি এবং `dispatch`

```php filename="app/Http/Controllers/SignupController.php"
SendWelcomeEmail::dispatch($user);

return response()->json(['queued' => true], 202);
```

উত্তরের পরে চলতে পারে এমন কাজের জন্য, FastAPI এর ব্যাকগ্রাউন্ডের কাজগুলি যথেষ্ট:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse

SENT: list[str] = []


def send_welcome_email(email: str) -> None:
    SENT.append(email)


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome_email, email)
    return JSONResponse({"queued": True}, status_code=202)
```

অন্য মেশিনে পুনরায় চেষ্টা এবং কর্মীদের জন্য, সেলারি, আরকিউ বা আরকিউর মতো একটি Python সারি ব্যবহার করুন।

## একটি পৃষ্ঠা ক্যাশে করা হচ্ছে

```php
Route::get('/blog', BlogController::class)->middleware('cache.headers:public;max_age=60');
```

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

পৃষ্ঠাটি প্রতি URL ক্যাশে করা হয় এবং 60 সেকেন্ড পরে পটভূমিতে আবার রেন্ডার করা হয়।

## `.env` এবং `config/`

| লারাভেল | নেক্সি |
|---|---|
| `.env` + `config/database.php` | `.env` `DATABASE_URL` সহ, `src/configs/db.py` দ্বারা পঠিত |
| `config/cors.php` | `useCORS` `nexyconfig.py` এ |
| `APP_KEY` সেশনের জন্য | `useSession = {"secret_key": ...}` |
| `public/` | `public/`, `/` এ পরিবেশিত |

## লাইভওয়্যার এবং জড়তা

লাইভওয়্যারের সার্ভার-চালিত উপাদানগুলি একটি পৃষ্ঠা থেকে কল করা ক্রিয়াগুলির মানচিত্র করে। Inertia এর React বা Vue পৃষ্ঠাগুলি `.tsx` বা `.vue` রুটে, অথবা `.nexy` পৃষ্ঠার ভিতরের দ্বীপগুলির মানচিত্র। [কর্ম](../guides/actions.md) এবং [দ্বীপগুলি](../rendering/islands.md) দেখুন।

## টেস্ট

```php filename="tests/feature/HelloTest.php"
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

## চলছে

| লারাভেল | নেক্সি |
|---|---|
| `laravel new` | `nx new` |
| `php artisan serve` | `nx dev` |
| `php artisan route:list` | `/docs` |
| `php artisan test` | `nx test` |
| `npm run build` | `nx build` |

## পরবর্তী পদক্ষেপ

- [থেকে Django নেক্সি থেকে](django.md)
- [কর্ম](../guides/actions.md)
- [ডাটাবেস](../guides/databases.md)
- [.nexy ফাইল](../views/nexy/README.md)
