# De Laravel a Nexy

En Nexy, una ruta Laravel y su método de controlador se convierten en un archivo en `src/routes/`: una vista Blade se convierte en una página `.nexy`, `$request->validate` un modelo Pydantic y Eloquent en un ORM que elija, como SQLModel.

Cada sección a continuación muestra un hábito de Laravel, luego lo mismo en Nexy.

## una ruta

```php filename="rutas/api.php"
use Illuminate\Support\Facades\Route;

Route::get('/hello', fn () => ['message' => 'Hello']);
```

No hay un archivo de rutas: la ruta del archivo es la URL y el nombre de la función es el método.

```python filename="src/rutas/api/hola.py"
async def GET():
    return {"message": "Hello"}
```

## Parámetros de ruta y `where`

```php filename="rutas/api.php"
Route::get('/users/{id}', fn (int $id) => ['id' => $id])->whereNumber('id');
```

`{id}` es un segmento `[id]` y la anotación `int` es la restricción: `/api/users/abc` responde a `404`.

```python filename="src/rutas/api/usuarios/[id].py"
async def GET(id: int):
    return {"id": id}
```

Una barra diagonal coincidente opcional `{slug?}` o `{path}` (`->where('path', '.*')`) es un `[...path].py` comodín.

## Controladores

```php filename="aplicación/Http/Controllers/NoteController.php"
class NoteController extends Controller
{
    public function show(int $id) { return ['id' => $id]; }

    public function destroy(int $id) { return ['deleted' => $id]; }
}
```

```php filename="rutas/api.php"
Route::get('/notes/{id}', [NoteController::class, 'show']);
Route::delete('/notes/{id}', [NoteController::class, 'destroy']);
```

Los métodos del controlador son las funciones del archivo, que llevan el nombre del verbo:

```python filename="src/rutas/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

Para clases con servicios inyectados, como en un controlador Laravel, consulte el [enrutador modular](../routing/modular/README.md).

## cadenas de consulta

```php filename="aplicación/Http/Controllers/SearchController.php"
public function __invoke(Request $request)
{
    return ['q' => $request->query('q', ''), 'page' => (int) $request->query('page', 1)];
}
```

```python filename="src/rutas/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Solicitudes de validación y formulario

```php filename="aplicación/Http/Controllers/ItemController.php"
public function store(Request $request)
{
    $data = $request->validate([
        'name' => 'required|string|max:100',
        'price' => 'required|numeric|gt:0',
    ]);

    return response()->json($data, 201);
}
```

Las reglas son un modelo Pydantic. Un cuerpo que se rompe responde `422` con el campo y la regla, como lo hace Laravel:

```python filename="src/rutas/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## Grupos de rutas con prefijo y middleware

```php filename="rutas/api.php"
Route::prefix('admin')->middleware('admin')->group(function () {
    Route::get('/stats', fn () => ['users' => 3]);
});
```

```php filename="aplicación/Http/Middleware/EnsureAdmin.php"
public function handle(Request $request, Closure $next)
{
    abort_unless($request->header('X-Role') === 'admin', 403, 'Admins only');

    return $next($request);
}
```

La carpeta es el prefijo y su `dependencies.py` es el middleware del grupo:

```python filename="src/rutas/admin/stats.py"
async def GET():
    return {"users": 3}
```

```python filename="src/rutas/admin/dependencias.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## software intermedio global

```php filename="aplicación/Http/Middleware/AddAppHeader.php"
public function handle(Request $request, Closure $next)
{
    $response = $next($request);
    $response->headers->set('X-App', 'demo');

    return $response;
}
```

Un `middleware.py` en la raíz de rutas envuelve cada solicitud:

```python filename="src/rutas/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Vistas de la hoja

```php filename="rutas/web.php"
Route::get('/users', fn () => view('users', ['users' => [['name' => 'Ada'], ['name' => 'Alan']]]));
```

```blade filename="recursos/vistas/usuarios.blade.php"
@extends('layouts.app')

@section('content')
<ul>
  @foreach ($users as $user)
  <li>{{ $user['name'] }}</li>
  @endforeach
</ul>
@endsection
```

La ruta y la vista son un `.nexy` archivo:

```nexy filename="src/rutas/usuarios.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

| Hoja | Jinja2 en `.nexy` |
|---|---|
| `{{ $name }}` (escapó) | `{{ name \| e }}`: `.nexy` no escapa por defecto |
| `{!! $html !!}` | `{{ html \| safe }}` |
| `@if ($user) ... @endif` | `{% if user %} ... {% endif %}` |
| `@foreach ($items as $item)` | `{% for item in items %}` |
| `@php ... @endphp` | Python en la portada |

## Diseños y `@yield`

```blade filename="recursos/vistas/diseños/app.blade.php"
<!DOCTYPE html>
<html>
  <body>@yield('content')</body>
</html>
```

Un `layout.nexy` envuelve cada página de su carpeta, sin `@extends` en las páginas:

```nexy filename="src/rutas/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Componentes de la hoja

```blade filename=""
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

```nexy filename="src/rutas/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>This week</p>
</Card>
```

`@` es `src/`: `nx new` escribe `useAliases = {"@": "src"}` en `nexyconfig.py`.

## Formularios, `@csrf` y redirecciones

```blade filename="recursos/vistas/notes.blade.php"
<form method="POST" action="{{ route('notes.store') }}">
  @csrf
  <input name="title">
  <button type="submit">Add</button>
</form>
```

```php filename="aplicación/Http/Controllers/NoteController.php"
public function store(Request $request)
{
    Note::create($request->validate(['title' => 'required']));

    return back();
}
```

Una acción es el método de controlador en el que se publica el formulario. Sus parámetros son los campos, y el visitante va `back()` con un `303` en caso de éxito:

```python filename="src/acciones/notas.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/rutas/notas.nexy"
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

## Elocuentes y migraciones.

```php filename="aplicación/Modelos/Post.php"
class Post extends Model
{
    protected $fillable = ['title', 'published'];
}

$posts = Post::where('published', true)->get();
```

Nexy no tiene ORM propio. `nx new` puede andamiar SQLModel, SQLAlchemy o Tortoise-ORM; con SQLModel:

```python filename="src/modelos/post_model.py"
from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    published: bool = False
```

```python filename="src/rutas/api/posts/published.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.post_model import Post


async def GET():
    with Session(engine) as session:
        posts = session.exec(select(Post).where(Post.published)).all()
    return {"titles": [post.title for post in posts]}
```

| Artesano | nexy |
|---|---|
| `php artisan make:migration` | `nx migrate -m "add posts"` |
| `php artisan migrate` | `nx migrate --upgrade` |

Consulte [Bases de datos](../guides/databases.md).

## `abort(404)` y vistas de error

```php filename="rutas/web.php"
Route::get('/posts/{slug}', function (string $slug) {
    abort_unless(isset(POSTS[$slug]), 404);
    return view('post', ['post' => POSTS[$slug]]);
});
```

`notFound()` es `abort(404)` y `notfound.nexy` es `resources/views/errors/404.blade.php`:

```nexy filename="src/rutas/publicaciones/[slug].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="src/rutas/notfound.nexy"
<h1>Not found</h1>
```

## Sesiones

```php filename="aplicación/Http/Controllers/LoginController.php"
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

```python filename="src/rutas/api/login.py"
from pydantic import BaseModel

from nexy.http import Request


class Login(BaseModel):
    name: str


async def POST(request: Request, body: Login):
    request.session["user"] = body.name
    return {"user": body.name}
```

Una página lee la sesión con `useSession()`.

## Colas y `dispatch`

```php filename="aplicación/Http/Controllers/SignupController.php"
SendWelcomeEmail::dispatch($user);

return response()->json(['queued' => true], 202);
```

Para el trabajo que puede ejecutarse después de la respuesta, las tareas en segundo plano de FastAPI son suficientes:

```python filename="src/rutas/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse

SENT: list[str] = []


def send_welcome_email(email: str) -> None:
    SENT.append(email)


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome_email, email)
    return JSONResponse({"queued": True}, status_code=202)
```

Para reintentos y trabajadores en otras máquinas, utilice una cola Python como Celery, RQ o arq.

## Almacenamiento en caché de una página

```php
Route::get('/blog', BlogController::class)->middleware('cache.headers:public;max_age=60');
```

```nexy filename="src/rutas/blog/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

La página se almacena en caché por URL y se vuelve a representar en segundo plano después de 60 segundos.

## `.env` y `config/`

| Laravel | nexy |
|---|---|
| `.env` + `config/database.php` | `.env` con `DATABASE_URL`, leído por `src/configs/db.py` |
| `config/cors.php` | `useCORS` en `nexyconfig.py` |
| `APP_KEY` para sesiones | `useSession = {"secret_key": ...}` |
| `public/` | `public/`, servido en `/` |

## Livewire e inercia

Los componentes controlados por el servidor de Livewire se asignan a acciones llamadas desde una página. Las páginas React o Vue de Inertia se asignan a rutas `.tsx` o `.vue`, o a islas dentro de una página `.nexy`. Ver [Acciones](../guides/actions.md) e [Islas](../rendering/islands.md).

## Pruebas

```php filename="pruebas/Característica/HelloTest.php"
public function test_hello(): void
{
    $this->getJson('/api/hello')->assertExactJson(['message' => 'Hello']);
}
```

```python filename="pruebas/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## corriendo

| Laravel | nexy |
|---|---|
| `laravel new` | `nx new` |
| `php artisan serve` | `nx dev` |
| `php artisan route:list` | `/docs` |
| `php artisan test` | `nx test` |
| `npm run build` | `nx build` |

## Próximos pasos

- [De Django a Nexy](django.md)
- [Acciones](../guides/actions.md)
- [Bases de datos](../guides/databases.md)
- [Archivos .nexy](../views/nexy/README.md)
