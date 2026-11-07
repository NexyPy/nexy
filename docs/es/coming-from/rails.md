# De Ruby on Rails a Nexy

En Nexy, una ruta Rails y su acción de controlador se convierten en un archivo en `src/routes/`: las vistas ERB se convierten en `.nexy` páginas con Jinja2, los parámetros fuertes se convierten en Pydantic modelos y `before_action` se convierte en un `dependencies.py`.

Cada sección a continuación muestra un hábito de Rails, luego lo mismo en Nexy.

## Una ruta y su acción

```ruby filename="config/rutas.rb"
get "/api/hello", to: "hello#show"
```

```ruby filename="aplicación/controladores/hello_controller.rb"
class HelloController < ApplicationController
  def show
    render json: { message: "Hello" }
  end
end
```

No hay `routes.rb`: la ruta del archivo es la URL, el nombre de la función es el método HTTP.

```python filename="src/rutas/api/hola.py"
async def GET():
    return {"message": "Hello"}
```

## `resources`

```ruby filename="config/rutas.rb"
resources :notes, only: [:index, :create, :show, :destroy]
```

Las siete acciones REST se distribuyen en dos archivos, uno por URL:

```python filename="src/rutas/api/notes/index.py"
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

```python filename="src/rutas/api/notes/[id].py"
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

| Acción de rieles | nexy |
|---|---|
| `index`, `create` | `GET`, `POST` en `notes/index.py` |
| `show`, `update`, `destroy` | `GET`, `PATCH`, `DELETE` en `notes/[id].py` |
| `new`, `edit` | `.nexy` páginas, `notes/new.nexy` y `notes/[id]/edit.nexy` |

## `params` y parámetros fuertes

```ruby filename="aplicación/controladores/items_controller.rb"
def create
  item = params.require(:item).permit(:name, :price)
  render json: item, status: :created
end
```

El modelo es la lista de permisos y la validación: los campos desconocidos se eliminan, los incorrectos responden `422`.

```python filename="src/rutas/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

Un parámetro de cadena de consulta, `params[:q]`, es un parámetro de función:

```python filename="src/rutas/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## `namespace` y `before_action`

```ruby filename="config/rutas.rb"
namespace :admin do
  get "stats", to: "stats#show"
end
```

```ruby filename="aplicación/controladores/admin/base_controller.rb"
class Admin::BaseController < ApplicationController
  before_action :require_admin

  private

  def require_admin
    head :forbidden unless request.headers["X-Role"] == "admin"
  end
end
```

El espacio de nombres es la carpeta y su `dependencies.py` es el `before_action` de cada ruta que contiene:

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

## `after_action` y middleware de bastidor

```ruby filename="aplicación/controladores/application_controller.rb"
after_action { response.set_header("X-App", "demo") }
```

```python filename="src/rutas/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Vistas de la ERB

```ruby filename="aplicación/controladores/users_controller.rb"
def index
  @users = [{ name: "Ada" }, { name: "Alan" }]
end
```

```erb filename="aplicación/vistas/usuarios/index.html.erb"
<ul>
  <% @users.each do |user| %>
  <li><%= user[:name] %></li>
  <% end %>
</ul>
```

La acción y la vista son un archivo `.nexy`; las variables de instancia se convierten en nombres simples:

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

`<%= %>` escapa y `{{ }}` no: escapa de lo que un visitante escribió con `{{ value | e }}`. `<%== %>` y `raw` son ​​`| safe`.

## Diseños y `yield`

```erb filename="aplicación/vistas/diseños/aplicación.html.erb"
<!DOCTYPE html>
<html>
  <body><%= yield %></body>
</html>
```

```nexy filename="src/rutas/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

Un `layout.nexy` en una subcarpeta se anida dentro de esta, como lo hace un diseño por controlador.

## Parciales

```erb filename="aplicación/vistas/compartido/_card.html.erb"
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

```nexy filename="src/rutas/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>This week</p>
</Card>
```

`@` es `src/`: `nx new` escribe `useAliases = {"@": "src"}` en `nexyconfig.py`.

## `form_with` y `redirect_to`

```erb filename="aplicación/views/notes/index.html.erb"
<%= form_with url: notes_path do |form| %>
  <%= form.text_field :title %>
  <%= form.submit "Add" %>
<% end %>
```

```ruby filename="aplicación/controladores/notes_controller.rb"
def create
  Note.create!(title: params[:title])
  redirect_to notes_path
end
```

Una acción es el `create` en el que se publica el formulario. Sus parámetros son los campos y el visitante es redirigido de regreso a la página con un `303`:

```python filename="src/acciones/notas.py"
from nexy.decorators import Action

TITLES: list[str] = []


@Action
async def add_note(title: str) -> None:
    TITLES.append(title)
```

```nexy filename="src/rutas/notas.nexy"
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

## Registro Activo y migraciones

```ruby filename="aplicación/modelos/post.rb"
class Post < ApplicationRecord
  scope :published, -> { where(published: true) }
end
```

Nexy no tiene ORM propio; `nx new` puede usar andamiaje SQLModel, SQLAlchemy o Tortoise-ORM. Con SQLModel:

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

| Rieles | nexy |
|---|---|
| `rails generate migration AddPosts` | `nx migrate -m "add posts"` |
| `rails db:migrate` | `nx migrate --upgrade` |

## `ActiveRecord::RecordNotFound` y `public/404.html`

```ruby filename="aplicación/controladores/posts_controller.rb"
def show
  @post = POSTS.fetch(params[:slug]) { raise ActiveRecord::RecordNotFound }
end
```

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

`notfound.nexy` en la raíz de rutas es `public/404.html`, representado como cualquier página:

```nexy filename="src/rutas/notfound.nexy"
<h1>Not found</h1>
```

## Sesiones

```ruby filename=""
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

```python filename="src/rutas/api/login.py"
from pydantic import BaseModel

from nexy.http import Request


class Login(BaseModel):
    name: str


async def POST(request: Request, body: Login):
    request.session["user"] = body.name
    return {"user": body.name}
```

Una página lo lee con `useSession()`.

## Almacenamiento en caché

```ruby filename="aplicación/controladores/blog_controller.rb"
def index
  expires_in 1.minute, public: true
end
```

```nexy filename="src/rutas/blog/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

## Trabajo activo

```ruby filename="aplicación/controladores/signups_controller.rb"
WelcomeMailerJob.perform_later(params[:email])
head :accepted
```

```python filename="src/rutas/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse


def send_welcome(email: str) -> None: ...


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome, email)
    return JSONResponse({"queued": True}, status_code=202)
```

Para reintentos y trabajadores separados, como con Sidekiq, use Celery, RQ o arq.

## Cable de acción

```ruby filename="aplicación/canales/echo_channel.rb"
class EchoChannel < ApplicationCable::Channel
  def receive(data)
    transmit(data)
  end
end
```

```python filename="src/rutas/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## Cable caliente

Los intercambios de páginas de Turbo Drive coinciden con el enrutador del cliente de un proyecto en modo cliente, y los controladores Stimulus coinciden con las islas: un pequeño componente que se hidrata dentro de una página de servidor. Ver [Islas](../rendering/islands.md) y [CSR](../rendering/csr.md).

## Pruebas

```ruby filename="especificación/solicitudes/hola_spec.rb"
RSpec.describe "Hello", type: :request do
  it "says hello" do
    get "/api/hello"
    expect(response.parsed_body).to eq("message" => "Hello")
  end
end
```

```python filename="pruebas/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## corriendo

| Rieles | nexy |
|---|---|
| `rails new` | `nx new` |
| `bin/rails server` | `nx dev` |
| `bin/rails routes` | `/docs` |
| `RAILS_ENV=production bin/rails server` | `nx build`, luego `nx start` |
| `bin/rails test` / `rspec` | `nx test` |

## Próximos pasos

- [De Django a Nexy](django.md)
- [De Laravel a Nexy](laravel.md)
- [Acciones](../guides/actions.md)
- [Bases de datos](../guides/databases.md)
