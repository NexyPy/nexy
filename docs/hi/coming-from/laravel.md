# लारवेल से नेक्सी तक

नेक्सी में एक लारवेल मार्ग और इसकी नियंत्रक विधि `src/routes/` के अंतर्गत एक फ़ाइल बन जाती है: एक ब्लेड दृश्य एक `.nexy` पृष्ठ, `$request->validate` एक Pydantic मॉडल बन जाता है, और आपके द्वारा चुना गया एक ओआरएम, जैसे कि SQLModel बन जाता है।

नीचे दिया गया प्रत्येक अनुभाग लारवेल आदत दिखाता है, फिर नेक्सी में भी यही चीज़।

## एक मार्ग

```php filename="मार्ग/api.php"
use Illuminate\Support\Facades\Route;

Route::get('/hello', fn () => ['message' => 'Hello']);
```

कोई रूट फ़ाइल नहीं है: फ़ाइल पथ URL है, और फ़ंक्शन नाम विधि है।

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## रूट पैरामीटर और `where`

```php filename="मार्ग/api.php"
Route::get('/users/{id}', fn (int $id) => ['id' => $id])->whereNumber('id');
```

`{id}` एक `[id]` खंड है, और `int` एनोटेशन बाधा है: `/api/users/abc` उत्तर `404` देता है।

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

एक वैकल्पिक `{slug?}` या `{path}` मिलान स्लैश (`->where('path', '.*')`) एक `[...path].py` कैच-ऑल है।

## नियंत्रक

```php filename="ऐप/Http/कंट्रोलर्स/नोटकंट्रोलर.php"
class NoteController extends Controller
{
    public function show(int $id) { return ['id' => $id]; }

    public function destroy(int $id) { return ['deleted' => $id]; }
}
```

```php filename="मार्ग/api.php"
Route::get('/notes/{id}', [NoteController::class, 'show']);
Route::delete('/notes/{id}', [NoteController::class, 'destroy']);
```

नियंत्रक विधियाँ फ़ाइल के कार्य हैं, जिनका नाम क्रिया के नाम पर रखा गया है:

```python filename="src/routes/api/notes/[id].py"
async def GET(id: int):
    return {"id": id}


async def DELETE(id: int):
    return {"deleted": id}
```

इंजेक्टेड सेवाओं वाली कक्षाओं के लिए, जैसे लारवेल नियंत्रक में, [मॉड्यूलर राउटर](../routing/modular/README.md) देखें।

## क्वेरी स्ट्रिंग्स

```php filename="ऐप/Http/कंट्रोलर्स/SearchController.php"
public function __invoke(Request $request)
{
    return ['q' => $request->query('q', ''), 'page' => (int) $request->query('page', 1)];
}
```

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## सत्यापन और प्रपत्र अनुरोध

```php filename="ऐप/एचटीपी/कंट्रोलर्स/आइटमकंट्रोलर.php"
public function store(Request $request)
{
    $data = $request->validate([
        'name' => 'required|string|max:100',
        'price' => 'required|numeric|gt:0',
    ]);

    return response()->json($data, 201);
}
```

नियम एक Pydantic मॉडल हैं। एक निकाय जो एक को तोड़ता है वह उत्तर देता है `422` क्षेत्र और नियम के साथ, जैसा कि लारवेल करता है:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## उपसर्ग और मिडलवेयर के साथ समूहों को रूट करें

```php filename="मार्ग/api.php"
Route::prefix('admin')->middleware('admin')->group(function () {
    Route::get('/stats', fn () => ['users' => 3]);
});
```

```php filename="ऐप/Http/Middleware/EnsureAdmin.php"
public function handle(Request $request, Closure $next)
{
    abort_unless($request->header('X-Role') === 'admin', 403, 'Admins only');

    return $next($request);
}
```

फ़ोल्डर उपसर्ग है, और इसका `dependencies.py` समूह का मिडलवेयर है:

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

## वैश्विक मिडलवेयर

```php filename="ऐप/Http/Middleware/AddAppHeader.php"
public function handle(Request $request, Closure $next)
{
    $response = $next($request);
    $response->headers->set('X-App', 'demo');

    return $response;
}
```

रूट रूट पर एक `middleware.py` प्रत्येक अनुरोध को लपेटता है:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## ब्लेड दृश्य

```php filename="मार्ग/वेब.php"
Route::get('/users', fn () => view('users', ['users' => [['name' => 'Ada'], ['name' => 'Alan']]]));
```

```blade filename="संसाधन/विचार/उपयोगकर्ता.ब्लेड.php"
@extends('layouts.app')

@section('content')
<ul>
  @foreach ($users as $user)
  <li>{{ $user['name'] }}</li>
  @endforeach
</ul>
@endsection
```

मार्ग और दृश्य एक `.nexy` फ़ाइल हैं:

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

| ब्लेड | Jinja2 में `.nexy` |
|---|---|
| `{{ $name }}` (भाग गया) | `{{ name \| e }}`: `.nexy` डिफ़ॉल्ट रूप से बचता नहीं है |
| `{!! $html !!}` | `{{ html \| safe }}` |
| `@if ($user) ... @endif` | `{% if user %} ... {% endif %}` |
| `@foreach ($items as $item)` | `{% for item in items %}` |
| `@php ... @endphp` | Python मुख्य बात में |

## लेआउट और `@yield`

```blade filename="संसाधन/विचार/लेआउट/app.blade.php"
<!DOCTYPE html>
<html>
  <body>@yield('content')</body>
</html>
```

एक `layout.nexy` अपने फ़ोल्डर के प्रत्येक पृष्ठ को लपेटता है, पृष्ठों में कोई `@extends` नहीं है:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

## ब्लेड घटक

```blade filename="संसाधन/विचार/घटक/कार्ड.ब्लेड.php"
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

`@` है `src/`: `nx new` `nexyconfig.py` में `useAliases = {"@": "src"}` लिखता है।

## प्रपत्र, `@csrf` और पुनर्निर्देशन

```blade filename="संसाधन/विचार/नोट्स.ब्लेड.php"
<form method="POST" action="{{ route('notes.store') }}">
  @csrf
  <input name="title">
  <button type="submit">Add</button>
</form>
```

```php filename="ऐप/Http/कंट्रोलर्स/नोटकंट्रोलर.php"
public function store(Request $request)
{
    Note::create($request->validate(['title' => 'required']));

    return back();
}
```

एक क्रिया वह नियंत्रक विधि है जिस पर प्रपत्र पोस्ट करता है। इसके पैरामीटर फ़ील्ड हैं, और विज़िटर सफलता पर `303` के साथ `back()` जाता है:

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

## वाक्पटुता और पलायन

```php filename="ऐप/मॉडल/पोस्ट.php"
class Post extends Model
{
    protected $fillable = ['title', 'published'];
}

$posts = Post::where('published', true)->get();
```

नेक्सी का अपना कोई ORM नहीं है। `nx new` मचान बना सकता है SQLModel, SQLAlchemy या कछुआ-ओआरएम; SQLModel के साथ:

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

| कारीगर | नेक्सी |
|---|---|
| `php artisan make:migration` | `nx migrate -m "add posts"` |
| `php artisan migrate` | `nx migrate --upgrade` |

[डेटाबेस](../guides/databases.md) देखें।

## `abort(404)` और त्रुटि दृश्य

```php filename="मार्ग/वेब.php"
Route::get('/posts/{slug}', function (string $slug) {
    abort_unless(isset(POSTS[$slug]), 404);
    return view('post', ['post' => POSTS[$slug]]);
});
```

`notFound()` है `abort(404)`, और `notfound.nexy` है `resources/views/errors/404.blade.php`:

```nexy filename="src/routes/posts/[स्लग].nexy"
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

## सत्र

```php filename="ऐप/Http/कंट्रोलर्स/LoginController.php"
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

एक पृष्ठ सत्र को `useSession()` के साथ पढ़ता है।

## कतारें और `dispatch`

```php filename="ऐप/Http/कंट्रोलर्स/साइनअपकंट्रोलर.php"
SendWelcomeEmail::dispatch($user);

return response()->json(['queued' => true], 202);
```

उत्तर के बाद चल सकने वाले कार्य के लिए, FastAPI के पृष्ठभूमि कार्य पर्याप्त हैं:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse

SENT: list[str] = []


def send_welcome_email(email: str) -> None:
    SENT.append(email)


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome_email, email)
    return JSONResponse({"queued": True}, status_code=202)
```

अन्य मशीनों पर पुनः प्रयास और श्रमिकों के लिए, सेलेरी, आरक्यू या आर्क जैसे Python कतार का उपयोग करें।

## किसी पृष्ठ को कैशिंग करना

```php
Route::get('/blog', BlogController::class)->middleware('cache.headers:public;max_age=60');
```

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

पृष्ठ को प्रति URL कैश किया जाता है और 60 सेकंड के बाद पृष्ठभूमि में फिर से प्रस्तुत किया जाता है।

## `.env` और `config/`

| लारवेल | नेक्सी |
|---|---|
| `.env` + `config/database.php` | `.env` के साथ `DATABASE_URL`, `src/configs/db.py` द्वारा पढ़ा गया |
| `config/cors.php` | `useCORS` में `nexyconfig.py` |
| `APP_KEY` सत्रों के लिए | `useSession = {"secret_key": ...}` |
| `public/` | `public/`, `/` में सेवा दी गई |

## लाइववायर और जड़ता

लाइववायर के सर्वर-संचालित घटक किसी पृष्ठ से बुलाए गए कार्यों को मैप करते हैं। इनर्टिया के React या Vue पृष्ठ `.tsx` या `.vue` मार्गों, या `.nexy` पृष्ठ के अंदर के द्वीपों पर मैप करते हैं। [क्रियाएँ](../guides/actions.md) और [द्वीप](../rendering/islands.md) देखें।

## परीक्षण

```php filename="परीक्षण/फ़ीचर/HelloTest.php"
public function test_hello(): void
{
    $this->getJson('/api/hello')->assertExactJson(['message' => 'Hello']);
}
```

```python filename="परीक्षण/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## चल रहा है

| लारवेल | नेक्सी |
|---|---|
| `laravel new` | `nx new` |
| `php artisan serve` | `nx dev` |
| `php artisan route:list` | `/docs` |
| `php artisan test` | `nx test` |
| `npm run build` | `nx build` |

## अगले चरण

- [से Django से नेक्सी](django.md)
- [क्रियाएँ](../guides/actions.md)
- [डेटाबेस](../guides/databases.md)
- [.nexy फ़ाइलें](../views/nexy/README.md)
