# Dari Laravel hingga Nexy

Di Nexy, rute Laravel dan metode pengontrolnya menjadi satu file di bawah `src/routes/`: tampilan Blade menjadi halaman `.nexy`, `$request->validate` model Pydantic, dan Eloquent menjadi ORM yang Anda pilih, seperti SQLModel.

Setiap bagian di bawah ini menunjukkan kebiasaan Laravel, lalu hal yang sama di Nexy.

## Sebuah rute

```php filename="rute/api.php"
use Illuminate\Support\Facades\Route;

Route::get('/hello', fn () => ['message' => 'Hello']);
```

Tidak ada file rute: jalur file adalah URL, dan nama fungsinya adalah metodenya.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## Parameter rute dan `where`

```php filename="rute/api.php"
Route::get('/users/{id}', fn (int $id) => ['id' => $id])->whereNumber('id');
```

`{id}` adalah segmen `[id]`, dan anotasi `int` adalah batasannya: `/api/users/abc` menjawab `404`.

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

Garis miring opsional `{slug?}` atau `{path}` yang cocok (`->where('path', '.*')`) adalah `[...path].py` yang mencakup semua.

## Pengendali

```php filename="app/Http/Controllers/NoteController.php"
class NoteController extends Controller
{
    public function show(int $id) { return ['id' => $id]; }

    public function destroy(int $id) { return ['deleted' => $id]; }
}
```

```php filename="rute/api.php"
Route::get('/notes/{id}', [NoteController::class, 'show']);
Route::delete('/notes/{id}', [NoteController::class, 'destroy']);
```

Metode pengontrol adalah fungsi file, dinamai berdasarkan kata kerja:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

Untuk kelas dengan layanan yang diinjeksi, seperti pada pengontrol Laravel, lihat [router modular](../routing/modular/README.md).

## String kueri

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

## Validasi dan Permintaan Formulir

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

Aturannya adalah model Pydantic. Badan yang melanggar jawaban `422` dengan bidang dan aturan, seperti yang dilakukan Laravel:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## Grup rute dengan awalan dan middleware

```php filename="rute/api.php"
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

Foldernya adalah awalan, dan `dependencies.py`-nya adalah middleware grup:

```python filename="src/route/admin/stats.py"
async def GET():
    return {"users": 3}
```

```python filename="src/rute/admin/dependensi.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## Perangkat menengah global

```php filename="app/Http/Middleware/AddAppHeader.php"
public function handle(Request $request, Closure $next)
{
    $response = $next($request);
    $response->headers->set('X-App', 'demo');

    return $response;
}
```

A `middleware.py` di root rute membungkus setiap permintaan:

```python filename="src/rute/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Tampilan pisau

```php filename="rute/web.php"
Route::get('/users', fn () => view('users', ['users' => [['name' => 'Ada'], ['name' => 'Alan']]]));
```

```blade filename="sumber daya/tampilan/pengguna.blade.php"
@extends('layouts.app')

@section('content')
<ul>
  @foreach ($users as $user)
  <li>{{ $user['name'] }}</li>
  @endforeach
</ul>
@endsection
```

Rute dan tampilannya adalah satu file `.nexy`:

```nexy filename="src/rute/pengguna.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

| Pisau | Jinja2 di `.nexy` |
|---|---|
| `{{ $name }}` (lolos) | `{{ name \| e }}`: `.nexy` tidak lolos secara default |
| `{!! $html !!}` | `{{ html \| safe }}` |
| `@if ($user) ... @endif` | `{% if user %} ... {% endif %}` |
| `@foreach ($items as $item)` | `{% for item in items %}` |
| `@php ... @endphp` | Python di materi depan |

## Tata letak dan `@yield`

```blade filename="sumber daya/tampilan/tata letak/app.blade.php"
<!DOCTYPE html>
<html>
  <body>@yield('content')</body>
</html>
```

`layout.nexy` membungkus setiap halaman foldernya, tanpa `@extends` di halaman:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## Komponen pisau

```blade filename="sumber daya/tampilan/komponen/card.blade.php"
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

```nexy filename="src/rute/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>This week</p>
</Card>
```

`@` adalah `src/`: `nx new` menulis `useAliases = {"@": "src"}` di `nexyconfig.py`.

## Formulir, `@csrf` dan pengalihan

```blade filename="sumber daya/tampilan/catatan.blade.php"
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

Suatu tindakan adalah metode pengontrol tempat formulir diposkan. Parameternya adalah bidang, dan pengunjung menuju `back()` dengan `303` jika berhasil:

```python filename="src/aksi/catatan.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/rute/catatan.nexy"
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

## Fasih dan migrasi

```php filename="app/Models/Post.php"
class Post extends Model
{
    protected $fillable = ['title', 'published'];
}

$posts = Post::where('published', true)->get();
```

Nexy tidak memiliki ORM sendiri. `nx new` dapat perancah SQLModel, SQLAlchemy atau Tortoise-ORM; dengan SQLModel:

```python filename="src/model/post_model.py"
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

| Pengrajin | Nexy |
|---|---|
| `php artisan make:migration` | `nx migrate -m "add posts"` |
| `php artisan migrate` | `nx migrate --upgrade` |

Lihat [Database](../guides/databases.md).

## `abort(404)` dan tampilan kesalahan

```php filename="rute/web.php"
Route::get('/posts/{slug}', function (string $slug) {
    abort_unless(isset(POSTS[$slug]), 404);
    return view('post', ['post' => POSTS[$slug]]);
});
```

`notFound()` adalah `abort(404)`, dan `notfound.nexy` adalah `resources/views/errors/404.blade.php`:

```nexy filename="src/rute/postingan/[siput].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello, world"}

slug: prop[str]
if slug not in POSTS:
    notFound()
---
<h1>{{ POSTS[slug] }}</h1>
```

```nexy filename="src/rute/tidak ditemukan.nexy"
<h1>Not found</h1>
```

## Sesi

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

Sebuah halaman membaca sesi dengan `useSession()`.

## Antrian dan `dispatch`

```php filename="app/Http/Controllers/SignupController.php"
SendWelcomeEmail::dispatch($user);

return response()->json(['queued' => true], 202);
```

Untuk pekerjaan yang dapat dijalankan setelah jawabannya, tugas latar belakang FastAPI sudah cukup:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse

SENT: list[str] = []


def send_welcome_email(email: str) -> None:
    SENT.append(email)


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome_email, email)
    return JSONResponse({"queued": True}, status_code=202)
```

Untuk percobaan ulang dan pekerja di mesin lain, gunakan antrian Python seperti Celery, RQ atau arq.

## Menyimpan halaman dalam cache

```php
Route::get('/blog', BlogController::class)->middleware('cache.headers:public;max_age=60');
```

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

Halaman di-cache per URL dan dirender lagi di latar belakang setelah 60 detik.

## `.env` dan `config/`

| Laravel | Nexy |
|---|---|
| `.env` + `config/database.php` | `.env` dengan `DATABASE_URL`, dibaca oleh `src/configs/db.py` |
| `config/cors.php` | `useCORS` di `nexyconfig.py` |
| `APP_KEY` untuk sesi | `useSession = {"secret_key": ...}` |
| `public/` | `public/`, bertugas di `/` |

## Livewire dan Inersia

Komponen berbasis server Livewire dipetakan ke tindakan yang dipanggil dari halaman. Halaman React atau Vue Inersia dipetakan ke rute `.tsx` atau `.vue`, atau ke pulau-pulau di dalam halaman `.nexy`. Lihat [Aksi](../guides/actions.md) dan [Pulau](../rendering/islands.md).

## Tes

```php filename="tes/Fitur/HelloTest.php"
public function test_hello(): void
{
    $this->getJson('/api/hello')->assertExactJson(['message' => 'Hello']);
}
```

```python filename="tes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Berlari

| Laravel | Nexy |
|---|---|
| `laravel new` | `nx new` |
| `php artisan serve` | `nx dev` |
| `php artisan route:list` | `/docs` |
| `php artisan test` | `nx test` |
| `npm run build` | `nx build` |

## Langkah selanjutnya

- [Dari Django hingga Nexy](django.md)
- [Tindakan](../guides/actions.md)
- [Basis Data](../guides/databases.md)
- [file .nexy](../views/nexy/README.md)
