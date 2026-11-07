# De Laravel à Nexy

Dans Nexy, une route Laravel et sa méthode de contrôleur deviennent un seul fichier sous `src/routes/` : une vue Blade devient une page `.nexy`, `$request->validate` un modèle Pydantic et Eloquent un ORM que vous choisissez, tel que SQLModel.

Chaque section ci-dessous montre une habitude Laravel, puis la même chose dans Nexy.

## Un itinéraire

```php filename="routes/api.php"
use Illuminate\Support\Facades\Route;

Route::get('/hello', fn () => ['message' => 'Hello']);
```

Il n'y a pas de fichier de routes : le chemin du fichier est l'URL et le nom de la fonction est la méthode.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Paramètres d'itinéraire et `where`

```php filename="routes/api.php"
Route::get('/users/{id}', fn (int $id) => ['id' => $id])->whereNumber('id');
```

`{id}` est un segment `[id]`, et l'annotation `int` est la contrainte : `/api/users/abc` répond à `404`.

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

Une barre oblique facultative `{slug?}` ou `{path}` correspondante (`->where('path', '.*')`) est un `[...path].py` fourre-tout.

## Contrôleurs

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

Les méthodes du contrôleur sont les fonctions du fichier, nommées d'après le verbe :

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

Pour les classes avec services injectés, comme dans un contrôleur Laravel, voir le [routeur modulaire](../routing/modular/README.md).

## Chaînes de requête

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

## Demandes de validation et de formulaire

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

Les règles sont un modèle Pydantic. Un corps qui casse on répond `422` avec le champ et la règle, comme le fait Laravel :

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## Groupes de routage avec un préfixe et un middleware

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

Le dossier est le préfixe, et son `dependencies.py` est le middleware du groupe :

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

## Intergiciel mondial

```php filename="app/Http/Middleware/AddAppHeader.php"
public function handle(Request $request, Closure $next)
{
    $response = $next($request);
    $response->headers->set('X-App', 'demo');

    return $response;
}
```

Un `middleware.py` à la racine des routes encapsule chaque requête :

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Vues de lame

```php filename="routes/web.php"
Route::get('/users', fn () => view('users', ['users' => [['name' => 'Ada'], ['name' => 'Alan']]]));
```

```blade filename="ressources/views/users.blade.php"
@extends('layouts.app')

@section('content')
<ul>
  @foreach ($users as $user)
  <li>{{ $user['name'] }}</li>
  @endforeach
</ul>
@endsection
```

L'itinéraire et la vue forment un seul fichier `.nexy` :

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

| Lame | Jinja2 dans `.nexy` |
|---|---|
| `{{ $name }}` (évadé) | `{{ name \| e }}` : `.nexy` ne s'échappe pas par défaut |
| `{!! $html !!}` | `{{ html \| safe }}` |
| `@if ($user) ... @endif` | `{% if user %} ... {% endif %}` |
| `@foreach ($items as $item)` | `{% for item in items %}` |
| `@php ... @endphp` | Python en première ligne |

## Mises en page et `@yield`

```blade filename="ressources/views/layouts/app.blade.php"
<!DOCTYPE html>
<html>
  <body>@yield('content')</body>
</html>
```

Un `layout.nexy` enveloppe chaque page de son dossier, sans `@extends` dans les pages :

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Composants de lame

```blade filename="ressources/views/components/card.blade.php"
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

`@` est `src/` : `nx new` écrit `useAliases = {"@": "src"}` dans `nexyconfig.py`.

## Formulaires, `@csrf` et redirections

```blade filename="ressources/views/notes.blade.php"
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

Une action est la méthode du contrôleur sur laquelle le formulaire est publié. Ses paramètres sont les champs, et le visiteur va `back()` avec un `303` en cas de succès :

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

## Éloquent et migrations

```php filename="app/Modèles/Post.php"
class Post extends Model
{
    protected $fillable = ['title', 'published'];
}

$posts = Post::where('published', true)->get();
```

Nexy n'a pas d'ORM propre. `nx new` peut échafauder SQLModel, SQLAlchemy ou Tortoise-ORM ; avec SQLModel :

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

Voir [Bases de données](../guides/databases.md).

## `abort(404)` et vues d'erreurs

```php filename="routes/web.php"
Route::get('/posts/{slug}', function (string $slug) {
    abort_unless(isset(POSTS[$slug]), 404);
    return view('post', ['post' => POSTS[$slug]]);
});
```

`notFound()` est `abort(404)` et `notfound.nexy` est `resources/views/errors/404.blade.php` :

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

## Séances

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

Une page lit la session avec `useSession()`.

## Files d'attente et `dispatch`

```php filename="app/Http/Controllers/SignupController.php"
SendWelcomeEmail::dispatch($user);

return response()->json(['queued' => true], 202);
```

Pour le travail qui peut s'exécuter après la réponse, les tâches en arrière-plan de FastAPI suffisent :

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse

SENT: list[str] = []


def send_welcome_email(email: str) -> None:
    SENT.append(email)


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome_email, email)
    return JSONResponse({"queued": True}, status_code=202)
```

Pour les tentatives et les travailleurs sur d'autres machines, utilisez une file d'attente Python telle que Celery, RQ ou arq.

## Mettre en cache une page

```php
Route::get('/blog', BlogController::class)->middleware('cache.headers:public;max_age=60');
```

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

La page est mise en cache par URL et rendue à nouveau en arrière-plan après 60 secondes.

## `.env` et `config/`

| Laravel | Nexy |
|---|---|
| `.env` + `config/database.php` | `.env` avec `DATABASE_URL`, lu par `src/configs/db.py` |
| `config/cors.php` | `useCORS` dans `nexyconfig.py` |
| `APP_KEY` pour les séances | `useSession = {"secret_key": ...}` |
| `public/` | `public/`, servi à `/` |

## Livewire et inertie

Les composants pilotés par le serveur de Livewire correspondent aux actions appelées à partir d'une page. Les pages React ou Vue d'Inertia correspondent à des itinéraires `.tsx` ou `.vue`, ou à des îles à l'intérieur d'une page `.nexy`. Voir [Actions](../guides/actions.md) et [Îles](../rendering/islands.md).

## Essais

```php filename="tests/Fonction/BonjourTest.php"
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

## Courir

| Laravel | Nexy |
|---|---|
| `laravel new` | `nx new` |
| `php artisan serve` | `nx dev` |
| `php artisan route:list` | `/docs` |
| `php artisan test` | `nx test` |
| `npm run build` | `nx build` |

## Prochaines étapes

- [De Django à Nexy](django.md)
- [Actions](../guides/actions.md)
- [Bases de données](../guides/databases.md)
- [Fichiers .nexy](../views/nexy/README.md)
