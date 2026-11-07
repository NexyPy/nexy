# Do Laravel ao Nexy

No Nexy, uma rota Laravel e seu método controlador tornam-se um arquivo em `src/routes/`: uma visualização Blade se torna uma página `.nexy`, `$request->validate` um modelo Pydantic, e Eloquent um ORM que você escolhe, como SQLModel.

Cada seção abaixo mostra um hábito do Laravel, e a mesma coisa no Nexy.

## Uma rota

```php filename="rotas/api.php"
use Illuminate\Support\Facades\Route;

Route::get('/hello', fn () => ['message' => 'Hello']);
```

Não há arquivo de rotas: o caminho do arquivo é a URL e o nome da função é o método.

```python filename="src/rotas/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Parâmetros de rota e `where`

```php filename="rotas/api.php"
Route::get('/users/{id}', fn (int $id) => ['id' => $id])->whereNumber('id');
```

`{id}` é um segmento `[id]` e a anotação `int` é a restrição: `/api/users/abc` responde `404`.

```python filename="src/rotas/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

Uma barra opcional `{slug?}` ou `{path}` correspondente (`->where('path', '.*')`) é um `[...path].py` genérico.

## Controladores

```php filename="app/Http/Controllers/NoteController.php"
class NoteController extends Controller
{
    public function show(int $id) { return ['id' => $id]; }

    public function destroy(int $id) { return ['deleted' => $id]; }
}
```

```php filename="rotas/api.php"
Route::get('/notes/{id}', [NoteController::class, 'show']);
Route::delete('/notes/{id}', [NoteController::class, 'destroy']);
```

Os métodos do controlador são as funções do arquivo, nomeados após o verbo:

```python filename="src/rotas/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

Para classes com serviços injetados, como em um controlador Laravel, consulte o [roteador modular](../routing/modular/README.md).

## Cadeias de caracteres de consulta

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

## Validação e solicitações de formulário

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

As regras são um modelo Pydantic. Um corpo que quebra responde `422` com o campo e a regra, como o Laravel faz:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## Grupos de rotas com prefixo e middleware

```php filename="rotas/api.php"
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

A pasta é o prefixo e seu `dependencies.py` é o middleware do grupo:

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

## Middleware global

```php filename="app/Http/Middleware/AddAppHeader.php"
public function handle(Request $request, Closure $next)
{
    $response = $next($request);
    $response->headers->set('X-App', 'demo');

    return $response;
}
```

Um `middleware.py` na raiz das rotas agrupa todas as solicitações:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Visualizações da lâmina

```php filename="rotas/web.php"
Route::get('/users', fn () => view('users', ['users' => [['name' => 'Ada'], ['name' => 'Alan']]]));
```

```blade filename="recursos/views/users.blade.php"
@extends('layouts.app')

@section('content')
<ul>
  @foreach ($users as $user)
  <li>{{ $user['name'] }}</li>
  @endforeach
</ul>
@endsection
```

A rota e a visualização são um arquivo `.nexy`:

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

| Lâmina | Jinja2 em `.nexy` |
|---|---|
| `{{ $name }}` (escapou) | `{{ name \| e }}`: `.nexy` não escapa por padrão |
| `{!! $html !!}` | `{{ html \| safe }}` |
| `@if ($user) ... @endif` | `{% if user %} ... {% endif %}` |
| `@foreach ($items as $item)` | `{% for item in items %}` |
| `@php ... @endphp` | Python no frontmatter |

## Layouts e `@yield`

```blade filename="recursos/visualizações/layouts/app.blade.php"
<!DOCTYPE html>
<html>
  <body>@yield('content')</body>
</html>
```

Um `layout.nexy` envolve todas as páginas de sua pasta, sem `@extends` nas páginas:

```nexy filename="src/rotas/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Componentes da lâmina

```blade filename="recursos/visualizações/componentes/card.blade.php"
@props(['title'])
<article>
  <h2>{{ $title }}</h2>
  {{ $slot }}
</article>
```

```blade
<x-card title="Latest"><p>This week</p></x-card>
```

```nexy filename="src/componentes/Card.nexy"
---
title: prop[str]
---
<article>
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/rotas/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>This week</p>
</Card>
```

`@` é `src/`: `nx new` escreve `useAliases = {"@": "src"}` em `nexyconfig.py`.

## Formulários, `@csrf` e redirecionamentos

```blade filename="recursos/views/notes.blade.php"
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

Uma ação é o método do controlador para o qual o formulário é postado. Seus parâmetros são os campos, e o visitante vai `back()` com um `303` em caso de sucesso:

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

## Eloquente e migrações

```php filename="app/Modelos/Post.php"
class Post extends Model
{
    protected $fillable = ['title', 'published'];
}

$posts = Post::where('published', true)->get();
```

Nexy não possui ORM próprio. `nx new` pode criar andaime SQLModel, SQLAlchemy ou Tortoise-ORM; com SQLModel:

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

| Artesão | Nexy |
|---|---|
| `php artisan make:migration` | `nx migrate -m "add posts"` |
| `php artisan migrate` | `nx migrate --upgrade` |

Consulte [Bancos de dados](../guides/databases.md).

## `abort(404)` e visualizações de erro

```php filename="rotas/web.php"
Route::get('/posts/{slug}', function (string $slug) {
    abort_unless(isset(POSTS[$slug]), 404);
    return view('post', ['post' => POSTS[$slug]]);
});
```

`notFound()` é `abort(404)` e `notfound.nexy` é `resources/views/errors/404.blade.php`:

```nexy filename="src/rotas/posts/[slug].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="src/rotas/notfound.nexy"
<h1>Not found</h1>
```

## Sessões

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

Uma página lê a sessão com `useSession()`.

## Filas e `dispatch`

```php filename="app/Http/Controllers/SignupController.php"
SendWelcomeEmail::dispatch($user);

return response()->json(['queued' => true], 202);
```

Para trabalhos que podem ser executados após a resposta, as tarefas em segundo plano de FastAPI são suficientes:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse

SENT: list[str] = []


def send_welcome_email(email: str) -> None:
    SENT.append(email)


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome_email, email)
    return JSONResponse({"queued": True}, status_code=202)
```

Para novas tentativas e trabalhadores em outras máquinas, use uma fila Python como Celery, RQ ou arq.

## Armazenando uma página em cache

```php
Route::get('/blog', BlogController::class)->middleware('cache.headers:public;max_age=60');
```

```nexy filename="src/rotas/blog/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

A página é armazenada em cache por URL e renderizada novamente em segundo plano após 60 segundos.

## `.env` e `config/`

| Laravel | Nexy |
|---|---|
| `.env` + `config/database.php` | `.env` com `DATABASE_URL`, lido por `src/configs/db.py` |
| `config/cors.php` | `useCORS` em `nexyconfig.py` |
| `APP_KEY` para sessões | `useSession = {"secret_key": ...}` |
| `public/` | `public/`, servido em `/` |

## Livewire e Inércia

Os componentes orientados ao servidor do Livewire são mapeados para ações chamadas de uma página. As páginas React ou Vue da inércia são mapeadas para rotas `.tsx` ou `.vue`, ou para ilhas dentro de uma página `.nexy`. Veja [Ações](../guides/actions.md) e [Ilhas](../rendering/islands.md).

## Testes

```php filename="testes/Recurso/HelloTest.php"
public function test_hello(): void
{
    $this->getJson('/api/hello')->assertExactJson(['message' => 'Hello']);
}
```

```python filename="testes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Correndo

| Laravel | Nexy |
|---|---|
| `laravel new` | `nx new` |
| `php artisan serve` | `nx dev` |
| `php artisan route:list` | `/docs` |
| `php artisan test` | `nx test` |
| `npm run build` | `nx build` |

## Próximas etapas

- [De Django para Nexy](django.md)
- [Ações](../guides/actions.md)
- [Bancos de dados](../guides/databases.md)
- [Arquivos .nexy](../views/nexy/README.md)
