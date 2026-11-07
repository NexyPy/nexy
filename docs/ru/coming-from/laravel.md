# От Laravel до Nexy

В Nexy маршрут Laravel и его метод контроллера становятся одним файлом в `src/routes/`: представление Blade становится страницей `.nexy`, `$request->validate` - моделью Pydantic, а Eloquent - выбранным вами ORM, например SQLModel.

В каждом разделе ниже показаны особенности Laravel, а затем то же самое в Nexy.

## Маршрут

```php filename="маршруты/api.php"
use Illuminate\Support\Facades\Route;

Route::get('/hello', fn () => ['message' => 'Hello']);
```

Файла маршрутов нет: путь к файлу - это URL-адрес, а имя функции - это метод.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Параметры маршрута и `where`

```php filename="маршруты/api.php"
Route::get('/users/{id}', fn (int $id) => ['id' => $id])->whereNumber('id');
```

`{id}` - это сегмент `[id]`, а аннотация `int` - это ограничение: `/api/users/abc` отвечает `404`.

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

Необязательные `{slug?}` или `{path}` соответствующие косые черты (`->where('path', '.*')`) - это универсальный вариант `[...path].py`.

## Контроллеры

```php filename="приложение/Http/Контроллеры/NoteController.php"
class NoteController extends Controller
{
    public function show(int $id) { return ['id' => $id]; }

    public function destroy(int $id) { return ['deleted' => $id]; }
}
```

```php filename="маршруты/api.php"
Route::get('/notes/{id}', [NoteController::class, 'show']);
Route::delete('/notes/{id}', [NoteController::class, 'destroy']);
```

Методы контроллера - это функции файла, названного в честь глагола:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

Для классов с внедренными сервисами, например, в контроллере Laravel, см. [модульный маршрутизатор](../routing/modular/README.md).

## Строки запроса

```php filename="приложение/Http/Контроллеры/SearchController.php"
public function __invoke(Request $request)
{
    return ['q' => $request->query('q', ''), 'page' => (int) $request->query('page', 1)];
}
```

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## Проверка и запросы форм

```php filename="приложение/Http/Контроллеры/ItemController.php"
public function store(Request $request)
{
    $data = $request->validate([
        'name' => 'required|string|max:100',
        'price' => 'required|numeric|gt:0',
    ]);

    return response()->json($data, 201);
}
```

Правила представляют собой модель Pydantic. Тело, которое нарушает одно, отвечает `422` полем и правилом, как это делает Laravel:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## Группы маршрутов с префиксом и промежуточным программным обеспечением

```php filename="маршруты/api.php"
Route::prefix('admin')->middleware('admin')->group(function () {
    Route::get('/stats', fn () => ['users' => 3]);
});
```

```php filename="приложение/Http/Middleware/EnsureAdmin.php"
public function handle(Request $request, Closure $next)
{
    abort_unless($request->header('X-Role') === 'admin', 403, 'Admins only');

    return $next($request);
}
```

Папка является префиксом, а ее `dependencies.py` - промежуточным программным обеспечением группы:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## Глобальное промежуточное программное обеспечение

```php filename="приложение/Http/Middleware/AddAppHeader.php"
public function handle(Request $request, Closure $next)
{
    $response = $next($request);
    $response->headers->set('X-App', 'demo');

    return $response;
}
```

`middleware.py` в корне маршрута оборачивает каждый запрос:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Виды лезвий

```php filename=""
Route::get('/users', fn () => view('users', ['users' => [['name' => 'Ada'], ['name' => 'Alan']]]));
```

```blade filename="ресурсы/просмотры/users.blade.php"
@extends('layouts.app')

@section('content')
<ul>
  @foreach ($users as $user)
  <li>{{ $user['name'] }}</li>
  @endforeach
</ul>
@endsection
```

Маршрут и представление представляют собой один файл `.nexy`:

```nexy filename="src/маршруты/users.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

| Лезвие | Jinja2 в `.nexy` |
|---|---|
| `{{ $name }}` (сбежал) | `{{ name \| e }}`: `.nexy` по умолчанию не экранируется |
| `{!! $html !!}` | `{{ html \| safe }}` |
| `@if ($user) ... @endif` | `{% if user %} ... {% endif %}` |
| `@foreach ($items as $item)` | `{% for item in items %}` |
| `@php ... @endphp` | Python во вступительной части |

## Макеты и `@yield`

```blade filename="ресурсы/представления/макеты/app.blade.php"
<!DOCTYPE html>
<html>
  <body>@yield('content')</body>
</html>
```

`layout.nexy` оборачивает каждую страницу своей папки, без `@extends` на страницах:

```nexy filename="src/маршруты/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Компоненты лезвия

```blade filename="ресурсы/представления/компоненты/card.blade.php"
@props(['title'])
<article>
  <h2>{{ $title }}</h2>
  {{ $slot }}
</article>
```

```blade
<x-card title="Latest"><p>This week</p></x-card>
```

```nexy filename="источник/компоненты/Card.nexy"
---
title: prop[str]
---
<article>
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="источник/маршруты/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>This week</p>
</Card>
```

`@` - это `src/`: `nx new` записывает `useAliases = {"@": "src"}` в `nexyconfig.py`.

## Формы, `@csrf` и перенаправления

```blade filename="ресурсы/просмотры/notes.blade.php"
<form method="POST" action="{{ route('notes.store') }}">
  @csrf
  <input name="title">
  <button type="submit">Add</button>
</form>
```

```php filename="приложение/Http/Контроллеры/NoteController.php"
public function store(Request $request)
{
    Note::create($request->validate(['title' => 'required']));

    return back();
}
```

Действие - это метод контроллера, которому отправляется форма. Его параметрами являются поля, и в случае успеха посетитель переходит к `back()` с сообщением `303`:

```python filename="src/actions/notes.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/маршруты/notes.nexy"
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

## Красноречивый и миграции

```php filename="приложение/Модели/Post.php"
class Post extends Model
{
    protected $fillable = ['title', 'published'];
}

$posts = Post::where('published', true)->get();
```

У Nexy нет собственного ORM. `nx new` может поддерживать SQLModel, SQLAlchemy или Tortoise-ORM; с SQLModel:

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

| Ремесленник | Некси |
|---|---|
| `php artisan make:migration` | `nx migrate -m "add posts"` |
| `php artisan migrate` | `nx migrate --upgrade` |

См. [Базы данных](../guides/databases.md).

## `abort(404)` и просмотры ошибок

```php filename=""
Route::get('/posts/{slug}', function (string $slug) {
    abort_unless(isset(POSTS[$slug]), 404);
    return view('post', ['post' => POSTS[$slug]]);
});
```

`notFound()` - это `abort(404)`, а `notfound.nexy` - это `resources/views/errors/404.blade.php`:

```nexy filename="src/маршруты/сообщения/[слизень].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="источник/маршруты/notfound.nexy"
<h1>Not found</h1>
```

## Сессии

```php filename="приложение/Http/Контроллеры/LoginController.php"
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

Страница считывает сеанс с помощью `useSession()`.

## Очереди и `dispatch`

```php filename="приложение/Http/Контроллеры/SignupController.php"
SendWelcomeEmail::dispatch($user);

return response()->json(['queued' => true], 202);
```

Для работы, которая может запуститься после ответа, достаточно фоновых задач FastAPI:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse

SENT: list[str] = []


def send_welcome_email(email: str) -> None:
    SENT.append(email)


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome_email, email)
    return JSONResponse({"queued": True}, status_code=202)
```

Для повторных попыток и рабочих процессов на других машинах используйте очередь Python, например Celery, RQ или arq.

## Кэширование страницы

```php
Route::get('/blog', BlogController::class)->middleware('cache.headers:public;max_age=60');
```

```nexy filename="src/маршруты/блог/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

Страница кэшируется для каждого URL-адреса и снова отображается в фоновом режиме через 60 секунд.

## `.env` и `config/`

| Ларавел | Некси |
|---|---|
| `.env` + `config/database.php` | `.env` с `DATABASE_URL`, прочитано `src/configs/db.py` |
| `config/cors.php` | `useCORS` в `nexyconfig.py` |
| `APP_KEY` для сеансов | `useSession = {"secret_key": ...}` |
| `public/` | `public/`, служил в `/` |

## Livewire и инерция

Серверные компоненты Livewire сопоставляются с действиями, вызываемыми со страницы. Страницы Inertia React или Vue соответствуют маршрутам `.tsx` или `.vue` или островам внутри страницы `.nexy`. См. [Действия](../guides/actions.md) и [Острова](../rendering/islands.md).

## Тесты

```php filename="тесты/Функция/HelloTest.php"
public function test_hello(): void
{
    $this->getJson('/api/hello')->assertExactJson(['message' => 'Hello']);
}
```

```python filename="тесты/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Бег

| Ларавел | Некси |
|---|---|
| `laravel new` | `nx new` |
| `php artisan serve` | `nx dev` |
| `php artisan route:list` | `/docs` |
| `php artisan test` | `nx test` |
| `npm run build` | `nx build` |

## Следующие шаги

- [От Django до Некси](django.md)
- [Действия](../guides/actions.md)
- [Базы данных](../guides/databases.md)
- [файлы .nexy](../views/nexy/README.md)
