# Dari Ruby on Rails hingga Nexy

Di Nexy, rute Rails dan tindakan pengontrolnya menjadi satu file di bawah `src/routes/`: Tampilan ERB menjadi `.nexy` halaman dengan Jinja2, parameter kuat menjadi model Pydantic, dan `before_action` menjadi `dependencies.py`.

Setiap bagian di bawah menunjukkan kebiasaan Rails, lalu hal yang sama di Nexy.

## Rute dan tindakannya

```ruby filename="config/routes.rb"
get "/api/hello", to: "hello#show"
```

```ruby filename="aplikasi/controllers/hello_controller.rb"
class HelloController < ApplicationController
  def show
    render json: { message: "Hello" }
  end
end
```

Tidak ada `routes.rb`: jalur file adalah URL, nama fungsinya adalah metode HTTP.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `resources`

```ruby filename="config/routes.rb"
resources :notes, only: [:index, :create, :show, :destroy]
```

Tujuh tindakan REST tersebar di dua file, satu per URL:

```python filename="src/routes/api/notes/index.py"
from pydantic import BaseModel

NOTES: dict[int, str] = {}


class NewNote(BaseModel):
    title: str


async def GET():
    return [{"id": id, "title": title} for id, title in NOTES.items()]


async def POST(note: NewNote):
    id = max(NOTES, default=0) + 1
    NOTES[id] = note.title
    return {"id": id, "title": note.title}
```

```python filename="src/routes/api/notes/[id].py"
from nexy.http import HTTPException

from .index import NOTES


async def GET(id: int):
    if id not in NOTES:
        raise HTTPException(status_code=404, detail="No such note")
    return {"id": id, "title": NOTES[id]}


async def DELETE(id: int):
    NOTES.pop(id, None)
    return {"deleted": id}
```

| Aksi rel | Nexy |
|---|---|
| `index`, `create` | `GET`, `POST` di `notes/index.py` |
| `show`, `update`, `destroy` | `GET`, `PATCH`, `DELETE` di `notes/[id].py` |
| `new`, `edit` | `.nexy` halaman, `notes/new.nexy` dan `notes/[id]/edit.nexy` |

## `params` dan parameter kuat

```ruby filename="aplikasi/controllers/items_controller.rb"
def create
  item = params.require(:item).permit(:name, :price)
  render json: item, status: :created
end
```

Modelnya adalah daftar izin dan validasinya: bidang yang tidak diketahui dihilangkan, yang salah menjawab `422`.

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

Parameter string kueri, `params[:q]`, adalah parameter fungsi:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## `namespace` dan `before_action`

```ruby filename="config/routes.rb"
namespace :admin do
  get "stats", to: "stats#show"
end
```

```ruby filename="aplikasi/controllers/admin/base_controller.rb"
class Admin::BaseController < ApplicationController
  before_action :require_admin

  private

  def require_admin
    head :forbidden unless request.headers["X-Role"] == "admin"
  end
end
```

Namespace adalah foldernya, dan `dependencies.py`-nya adalah `before_action` dari setiap rute di dalamnya:

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

## `after_action` dan middleware Rak

```ruby filename="aplikasi/controllers/application_controller.rb"
after_action { response.set_header("X-App", "demo") }
```

```python filename="src/rute/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## pandangan ERB

```ruby filename="aplikasi/controllers/users_controller.rb"
def index
  @users = [{ name: "Ada" }, { name: "Alan" }]
end
```

```erb filename="app/views/users/index.html.erb"
<ul>
  <% @users.each do |user| %>
  <li><%= user[:name] %></li>
  <% end %>
</ul>
```

Tindakan dan tampilan adalah satu file `.nexy`; variabel instan menjadi nama biasa:

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

`<%= %>` lolos dan `{{ }}` tidak: lolos dari apa yang diketik pengunjung dengan `{{ value | e }}`. `<%== %>` dan `raw` adalah `| safe`.

## Tata letak dan `yield`

```erb filename="aplikasi/views/layouts/application.html.erb"
<!DOCTYPE html>
<html>
  <body><%= yield %></body>
</html>
```

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

A `layout.nexy` dalam subfolder bersarang di dalam subfolder ini, seperti yang dilakukan tata letak per pengontrol.

## Sebagian

```erb filename="aplikasi/views/shared/_card.html.erb"
<article><h2><%= title %></h2><%= yield %></article>
```

```erb
<%= render "shared/card", title: "Latest" do %><p>This week</p><% end %>
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

## `form_with` dan `redirect_to`

```erb filename="aplikasi/views/notes/index.html.erb"
<%= form_with url: notes_path do |form| %>
  <%= form.text_field :title %>
  <%= form.submit "Add" %>
<% end %>
```

```ruby filename="aplikasi/controllers/notes_controller.rb"
def create
  Note.create!(title: params[:title])
  redirect_to notes_path
end
```

Suatu tindakan adalah `create` tempat formulir diposkan. Parameternya adalah bidang, dan pengunjung diarahkan kembali ke halaman dengan `303`:

```python filename="src/aksi/catatan.py"
from nexy.decorators import Action

TITLES: list[str] = []


@Action
async def add_note(title: str) -> None:
    TITLES.append(title)
```

```nexy filename="src/rute/catatan.nexy"
---
from src.actions.notes import TITLES
---
<form method="post" action="{{ __actions_path['add_note'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
<ul>
  {% for title in TITLES %}
  <li>{{ title }}</li>
  {% endfor %}
</ul>
```

## Catatan Aktif dan migrasi

```ruby filename="aplikasi/model/post.rb"
class Post < ApplicationRecord
  scope :published, -> { where(published: true) }
end
```

Nexy tidak memiliki ORM sendiri; `nx new` dapat perancah SQLModel, SQLAlchemy atau Tortoise-ORM. Dengan SQLModel:

```python filename="src/model/post_model.py"
from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    published: bool = False
```

```python filename=""
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.post_model import Post


async def GET():
    with Session(engine) as session:
        posts = session.exec(select(Post).where(Post.published)).all()
    return {"titles": [post.title for post in posts]}
```

| Rel | Nexy |
|---|---|
| `rails generate migration AddPosts` | `nx migrate -m "add posts"` |
| `rails db:migrate` | `nx migrate --upgrade` |

## `ActiveRecord::RecordNotFound` dan `public/404.html`

```ruby filename="aplikasi/controllers/posts_controller.rb"
def show
  @post = POSTS.fetch(params[:slug]) { raise ActiveRecord::RecordNotFound }
end
```

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

`notfound.nexy` di root rute adalah `public/404.html`, dirender seperti halaman mana pun:

```nexy filename="src/rute/tidak ditemukan.nexy"
<h1>Not found</h1>
```

## Sesi

```ruby filename="aplikasi/controllers/sessions_controller.rb"
def create
  session[:user] = params[:name]
  render json: { user: session[:user] }
end
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

Sebuah halaman membacanya dengan `useSession()`.

## cache

```ruby filename="aplikasi/controllers/blog_controller.rb"
def index
  expires_in 1.minute, public: true
end
```

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

## Pekerjaan Aktif

```ruby filename="aplikasi/controllers/signups_controller.rb"
WelcomeMailerJob.perform_later(params[:email])
head :accepted
```

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse


def send_welcome(email: str) -> None: ...


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome, email)
    return JSONResponse({"queued": True}, status_code=202)
```

Untuk percobaan ulang dan pekerja terpisah, seperti Sidekiq, gunakan Seledri, RQ, atau arq.

## Kabel Aksi

```ruby filename="aplikasi/saluran/echo_channel.rb"
class EchoChannel < ApplicationCable::Channel
  def receive(data)
    transmit(data)
  end
end
```

```python filename="src/routes/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## kabel panas

Pertukaran halaman Turbo Drive cocok dengan router klien dari proyek mode klien, dan pengontrol Stimulus cocok dengan pulau: komponen kecil yang terhidrasi di dalam halaman server. Lihat [Pulau](../rendering/islands.md) dan [CSR](../rendering/csr.md).

## Tes

```ruby filename="spesifikasi/permintaan/hello_spec.rb"
RSpec.describe "Hello", type: :request do
  it "says hello" do
    get "/api/hello"
    expect(response.parsed_body).to eq("message" => "Hello")
  end
end
```

```python filename="tes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Berlari

| Rel | Nexy |
|---|---|
| `rails new` | `nx new` |
| `bin/rails server` | `nx dev` |
| `bin/rails routes` | `/docs` |
| `RAILS_ENV=production bin/rails server` | `nx build`, lalu `nx start` |
| `bin/rails test` / `rspec` | `nx test` |

## Langkah selanjutnya

- [Dari Django hingga Nexy](django.md)
- [Dari Laravel ke Nexy](laravel.md)
- [Tindakan](../guides/actions.md)
- [Basis Data](../guides/databases.md)
