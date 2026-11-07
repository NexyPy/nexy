# From Laravel to Nexy

In Nexy a Laravel route and its controller method become one file under `src/routes/`: a Blade
view becomes a `.nexy` page, `$request->validate` a Pydantic model, and Eloquent an ORM you pick,
such as SQLModel.

Each section below shows a Laravel habit, then the same thing in Nexy.

## A route

```php filename="routes/api.php"
use Illuminate\Support\Facades\Route;

Route::get('/hello', fn () => ['message' => 'Hello']);
```

There is no routes file: the file path is the URL, and the function name is the method.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Route parameters and `where`

```php filename="routes/api.php"
Route::get('/users/{id}', fn (int $id) => ['id' => $id])->whereNumber('id');
```

`{id}` is a `[id]` segment, and the `int` annotation is the constraint: `/api/users/abc` answers
`404`.

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

An optional `{slug?}` or a `{path}` matching slashes (`->where('path', '.*')`) is a
`[...path].py` catch-all.

## Controllers

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

The controller methods are the functions of the file, named after the verb:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

For classes with injected services, as in a Laravel controller, see the
[modular router](../routing/modular/README.md).

## Query strings

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

## Validation and Form Requests

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

The rules are a Pydantic model. A body that breaks one answers `422` with the field and the rule,
as Laravel does:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## Route groups with a prefix and middleware

```php filename="routes/api.php"
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

The folder is the prefix, and its `dependencies.py` is the middleware of the group:

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

## Global middleware

```php filename="app/Http/Middleware/AddAppHeader.php"
public function handle(Request $request, Closure $next)
{
    $response = $next($request);
    $response->headers->set('X-App', 'demo');

    return $response;
}
```

A `middleware.py` at the routes root wraps every request:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Blade views

```php filename="routes/web.php"
Route::get('/users', fn () => view('users', ['users' => [['name' => 'Ada'], ['name' => 'Alan']]]));
```

```blade filename="resources/views/users.blade.php"
@extends('layouts.app')

@section('content')
<ul>
  @foreach ($users as $user)
  <li>{{ $user['name'] }}</li>
  @endforeach
</ul>
@endsection
```

The route and the view are one `.nexy` file:

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

| Blade | Jinja2 in `.nexy` |
|---|---|
| `{{ $name }}` (escaped) | `{{ name \| e }}`: `.nexy` does not escape by default |
| `{!! $html !!}` | `{{ html \| safe }}` |
| `@if ($user) ... @endif` | `{% if user %} ... {% endif %}` |
| `@foreach ($items as $item)` | `{% for item in items %}` |
| `@php ... @endphp` | Python in the frontmatter |

## Layouts and `@yield`

```blade filename="resources/views/layouts/app.blade.php"
<!DOCTYPE html>
<html>
  <body>@yield('content')</body>
</html>
```

A `layout.nexy` wraps every page of its folder, with no `@extends` in the pages:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Blade components

```blade filename="resources/views/components/card.blade.php"
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

`@` is `src/`: `nx new` writes `useAliases = {"@": "src"}` in `nexyconfig.py`.

## Forms, `@csrf` and redirects

```blade filename="resources/views/notes.blade.php"
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

An action is the controller method the form posts to. Its parameters are the fields, and the
visitor goes `back()` with a `303` on success:

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

## Eloquent and migrations

```php filename="app/Models/Post.php"
class Post extends Model
{
    protected $fillable = ['title', 'published'];
}

$posts = Post::where('published', true)->get();
```

Nexy has no ORM of its own. `nx new` can scaffold SQLModel, SQLAlchemy or Tortoise-ORM; with
SQLModel:

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

| Artisan | Nexy |
|---|---|
| `php artisan make:migration` | `nx migrate -m "add posts"` |
| `php artisan migrate` | `nx migrate --upgrade` |

See [Databases](../guides/databases.md).

## `abort(404)` and error views

```php filename="routes/web.php"
Route::get('/posts/{slug}', function (string $slug) {
    abort_unless(isset(POSTS[$slug]), 404);
    return view('post', ['post' => POSTS[$slug]]);
});
```

`notFound()` is `abort(404)`, and `notfound.nexy` is `resources/views/errors/404.blade.php`:

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

## Sessions

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

A page reads the session with `useSession()`.

## Queues and `dispatch`

```php filename="app/Http/Controllers/SignupController.php"
SendWelcomeEmail::dispatch($user);

return response()->json(['queued' => true], 202);
```

For work that can run after the answer, FastAPI's background tasks are enough:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse

SENT: list[str] = []


def send_welcome_email(email: str) -> None:
    SENT.append(email)


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome_email, email)
    return JSONResponse({"queued": True}, status_code=202)
```

For retries and workers on other machines, use a Python queue such as Celery, RQ or arq.

## Caching a page

```php
Route::get('/blog', BlogController::class)->middleware('cache.headers:public;max_age=60');
```

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

The page is cached per URL and rendered again in the background after 60 seconds.

## `.env` and `config/`

| Laravel | Nexy |
|---|---|
| `.env` + `config/database.php` | `.env` with `DATABASE_URL`, read by `src/configs/db.py` |
| `config/cors.php` | `useCORS` in `nexyconfig.py` |
| `APP_KEY` for sessions | `useSession = {"secret_key": ...}` |
| `public/` | `public/`, served at `/` |

## Livewire and Inertia

Livewire's server-driven components map to actions called from a page. Inertia's React or Vue
pages map to `.tsx` or `.vue` routes, or to islands inside a `.nexy` page. See
[Actions](../guides/actions.md) and [Islands](../rendering/islands.md).

## Tests

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

## Running

| Laravel | Nexy |
|---|---|
| `laravel new` | `nx new` |
| `php artisan serve` | `nx dev` |
| `php artisan route:list` | `/docs` |
| `php artisan test` | `nx test` |
| `npm run build` | `nx build` |

## Next steps

- [From Django to Nexy](django.md)
- [Actions](../guides/actions.md)
- [Databases](../guides/databases.md)
- [.nexy files](../views/nexy/README.md)
