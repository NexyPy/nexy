# Von Laravel bis Nexy

In Nexy werden eine Laravel-Route und ihre Controller-Methode zu einer Datei unter `src/routes/`: Eine Blade-Ansicht wird zu einer `.nexy`-Seite, `$request->validate` zu einem Pydantic-Modell und Eloquent zu einem von Ihnen ausgewählten ORM, z. B. SQLModel.

Jeder Abschnitt unten zeigt eine Laravel-Gewohnheit, dann dasselbe in Nexy.

## Eine Route

```php filename="Routen/api.php"
use Illuminate\Support\Facades\Route;

Route::get('/hello', fn () => ['message' => 'Hello']);
```

Es gibt keine Routendatei: Der Dateipfad ist die URL und der Funktionsname ist die Methode.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Routenparameter und `where`

```php filename="Routen/api.php"
Route::get('/users/{id}', fn (int $id) => ['id' => $id])->whereNumber('id');
```

`{id}` ist ein `[id]`-Segment und die Annotation `int` ist die Einschränkung: `/api/users/abc` antwortet auf `404`.

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

Ein optionaler `{slug?}` oder ein `{path}` passender Schrägstrich (`->where('path', '.*')`) ist ein Allheilmittel `[...path].py`.

## Controller

```php filename="app/Http/Controllers/NoteController.php"
class NoteController extends Controller
{
    public function show(int $id) { return ['id' => $id]; }

    public function destroy(int $id) { return ['deleted' => $id]; }
}
```

```php filename="Routen/api.php"
Route::get('/notes/{id}', [NoteController::class, 'show']);
Route::delete('/notes/{id}', [NoteController::class, 'destroy']);
```

Die Controller-Methoden sind die Funktionen der Datei, benannt nach dem Verb:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

Informationen zu Klassen mit injizierten Diensten, wie in einem Laravel-Controller, finden Sie im [modularen Router](../routing/modular/README.md).

## Abfragezeichenfolgen

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

## Validierung und Formularanfragen

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

Die Regeln sind ein Pydantic-Modell. Ein Körper, der einen bricht, antwortet `422` mit dem Feld und der Regel, wie Laravel es tut:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## Routengruppen mit Präfix und Middleware

```php filename="Routen/api.php"
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

Der Ordner ist das Präfix und sein `dependencies.py` ist die Middleware der Gruppe:

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

## Globale Middleware

```php filename="app/Http/Middleware/AddAppHeader.php"
public function handle(Request $request, Closure $next)
{
    $response = $next($request);
    $response->headers->set('X-App', 'demo');

    return $response;
}
```

Ein `middleware.py` im Routenstamm umschließt jede Anfrage:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Klingenansichten

```php filename="Routen/web.php"
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

Die Route und die Ansicht sind eine `.nexy` Datei:

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

| Klinge | Jinja2 in `.nexy` |
|---|---|
| `{{ $name }}` (entkommen) | `{{ name \| e }}`: `.nexy` wird standardmäßig nicht maskiert |
| `{!! $html !!}` | `{{ html \| safe }}` |
| `@if ($user) ... @endif` | `{% if user %} ... {% endif %}` |
| `@foreach ($items as $item)` | `{% for item in items %}` |
| `@php ... @endphp` | Python im Titelblatt |

## Layouts und `@yield`

```blade filename="resources/views/layouts/app.blade.php"
<!DOCTYPE html>
<html>
  <body>@yield('content')</body>
</html>
```

Ein `layout.nexy` umschließt jede Seite seines Ordners, ohne `@extends` in den Seiten:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Klingenkomponenten

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

`@` ist `src/`: `nx new` schreibt `useAliases = {"@": "src"}` in `nexyconfig.py`.

## Formulare, `@csrf` und Weiterleitungen

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

Eine Aktion ist die Controller-Methode, an die das Formular sendet. Seine Parameter sind die Felder, und der Besucher geht `back()` mit einem `303` bei Erfolg:

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

## Eloquent und Migrationen

```php filename="app/Models/Post.php"
class Post extends Model
{
    protected $fillable = ['title', 'published'];
}

$posts = Post::where('published', true)->get();
```

Nexy hat kein eigenes ORM. `nx new` kann SQLModel, SQLAlchemy oder Tortoise-ORM als Gerüst verwenden; mit SQLModel:

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

| Handwerker | Nexy |
|---|---|
| `php artisan make:migration` | `nx migrate -m "add posts"` |
| `php artisan migrate` | `nx migrate --upgrade` |

Siehe [Datenbanken](../guides/databases.md).

## `abort(404)` und Fehleransichten

```php filename="Routen/web.php"
Route::get('/posts/{slug}', function (string $slug) {
    abort_unless(isset(POSTS[$slug]), 404);
    return view('post', ['post' => POSTS[$slug]]);
});
```

`notFound()` ist `abort(404)` und `notfound.nexy` ist `resources/views/errors/404.blade.php`:

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

## Sitzungen

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

Eine Seite liest die Sitzung mit `useSession()`.

## Warteschlangen und `dispatch`

```php filename="app/Http/Controllers/SignupController.php"
SendWelcomeEmail::dispatch($user);

return response()->json(['queued' => true], 202);
```

Für Arbeiten, die nach der Antwort ausgeführt werden können, reichen die Hintergrundaufgaben von FastAPI aus:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse

SENT: list[str] = []


def send_welcome_email(email: str) -> None:
    SENT.append(email)


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome_email, email)
    return JSONResponse({"queued": True}, status_code=202)
```

Für Wiederholungsversuche und Worker auf anderen Maschinen verwenden Sie eine Python-Warteschlange wie Celery, RQ oder arq.

## Eine Seite zwischenspeichern

```php
Route::get('/blog', BlogController::class)->middleware('cache.headers:public;max_age=60');
```

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

Die Seite wird pro URL zwischengespeichert und nach 60 Sekunden im Hintergrund erneut gerendert.

## `.env` und `config/`

| Laravel | Nexy |
|---|---|
| `.env` + `config/database.php` | `.env` mit `DATABASE_URL`, gelesen von `src/configs/db.py` |
| `config/cors.php` | `useCORS` in `nexyconfig.py` |
| `APP_KEY` für Sitzungen | `useSession = {"secret_key": ...}` |
| `public/` | `public/`, zugestellt in `/` |

## Livewire und Trägheit

Die servergesteuerten Komponenten von Livewire werden auf Aktionen abgebildet, die von einer Seite aufgerufen werden. Die React- oder Vue-Seiten von Inertia sind auf `.tsx`- oder `.vue`-Routen oder auf Inseln innerhalb einer `.nexy`-Seite abgebildet. Siehe [Aktionen](../guides/actions.md) und [Inseln](../rendering/islands.md).

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

## Laufen

| Laravel | Nexy |
|---|---|
| `laravel new` | `nx new` |
| `php artisan serve` | `nx dev` |
| `php artisan route:list` | `/docs` |
| `php artisan test` | `nx test` |
| `npm run build` | `nx build` |

## Nächste Schritte

- [Von Django zu Nexy](django.md)
- [Aktionen](../guides/actions.md)
- [Datenbanken](../guides/databases.md)
- [.nexy-Dateien](../views/nexy/README.md)
