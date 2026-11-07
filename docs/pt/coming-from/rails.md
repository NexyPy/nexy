# De Ruby on Rails a Nexy

No Nexy, uma rota Rails e sua ação de controlador tornam-se um arquivo em `src/routes/`: visualizações ERB tornam-se `.nexy` páginas com Jinja2, parâmetros fortes tornam-se Pydantic modelos e `before_action` torna-se um `dependencies.py`.

Cada seção abaixo mostra um hábito do Rails e a mesma coisa no Nexy.

## Uma rota e sua ação

```ruby filename="config/rotas.rb"
get "/api/hello", to: "hello#show"
```

```ruby filename="app/controllers/hello_controller.rb"
class HelloController < ApplicationController
  def show
    render json: { message: "Hello" }
  end
end
```

Não existe `routes.rb`: o caminho do arquivo é a URL, o nome da função é o método HTTP.

```python filename="src/rotas/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `resources`

```ruby filename="config/rotas.rb"
resources :notes, only: [:index, :create, :show, :destroy]
```

As sete ações REST estão distribuídas em dois arquivos, um por URL:

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

```python filename="src/rotas/api/notes/[id].py"
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

| Ação de trilhos | Nexy |
|---|---|
| `index`, `create` | `GET`, `POST` em `notes/index.py` |
| `show`, `update`, `destroy` | `GET`, `PATCH`, `DELETE` em `notes/[id].py` |
| `new`, `edit` | `.nexy` páginas, `notes/new.nexy` e `notes/[id]/edit.nexy` |

## `params` e parâmetros fortes

```ruby filename="app/controllers/items_controller.rb"
def create
  item = params.require(:item).permit(:name, :price)
  render json: item, status: :created
end
```

O modelo é a lista de permissões e a validação: campos desconhecidos são descartados, os errados respondem `422`.

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

Um parâmetro de string de consulta, `params[:q]`, é um parâmetro de função:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## `namespace` e `before_action`

```ruby filename="config/rotas.rb"
namespace :admin do
  get "stats", to: "stats#show"
end
```

```ruby filename="app/controllers/admin/base_controller.rb"
class Admin::BaseController < ApplicationController
  before_action :require_admin

  private

  def require_admin
    head :forbidden unless request.headers["X-Role"] == "admin"
  end
end
```

O namespace é a pasta e seu `dependencies.py` é o `before_action` de cada rota nela:

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

## `after_action` e middleware Rack

```ruby filename="app/controllers/application_controller.rb"
after_action { response.set_header("X-App", "demo") }
```

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Visualizações ERB

```ruby filename="app/controllers/users_controller.rb"
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

A ação e a visualização são um arquivo `.nexy`; variáveis de instância tornam-se nomes simples:

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

`<%= %>` escapa e `{{ }}` não: escapa o que um visitante digitou com `{{ value | e }}`. `<%== %>` e `raw` são `| safe`.

## Layouts e `yield`

```erb filename="app/views/layouts/application.html.erb"
<!DOCTYPE html>
<html>
  <body><%= yield %></body>
</html>
```

```nexy filename="src/rotas/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

Um `layout.nexy` em uma subpasta se aninha dentro desta, como faz um layout por controlador.

## Parciais

```erb filename="app/views/shared/_card.html.erb"
<article><h2><%= title %></h2><%= yield %></article>
```

```erb
<%= render "shared/card", title: "Latest" do %><p>This week</p><% end %>
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

## `form_with` e `redirect_to`

```erb filename="app/views/notes/index.html.erb"
<%= form_with url: notes_path do |form| %>
  <%= form.text_field :title %>
  <%= form.submit "Add" %>
<% end %>
```

```ruby filename="app/controllers/notes_controller.rb"
def create
  Note.create!(title: params[:title])
  redirect_to notes_path
end
```

Uma ação é o `create` para o qual o formulário é postado. Seus parâmetros são os campos, e o visitante é redirecionado de volta à página com um `303`:

```python filename="src/actions/notes.py"
from nexy.decorators import Action

TITLES: list[str] = []


@Action
async def add_note(title: str) -> None:
    TITLES.append(title)
```

```nexy filename="src/routes/notes.nexy"
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

## Active Record e migrações

```ruby filename="app/models/post.rb"
class Post < ApplicationRecord
  scope :published, -> { where(published: true) }
end
```

Nexy não possui ORM próprio; `nx new` pode usar SQLModel, SQLAlchemy ou Tortoise-ORM. Com SQLModel:

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

| Trilhos | Nexy |
|---|---|
| `rails generate migration AddPosts` | `nx migrate -m "add posts"` |
| `rails db:migrate` | `nx migrate --upgrade` |

## `ActiveRecord::RecordNotFound` e `public/404.html`

```ruby filename="app/controllers/posts_controller.rb"
def show
  @post = POSTS.fetch(params[:slug]) { raise ActiveRecord::RecordNotFound }
end
```

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

`notfound.nexy` na raiz das rotas é `public/404.html`, renderizado como qualquer página:

```nexy filename="src/rotas/notfound.nexy"
<h1>Not found</h1>
```

## Sessões

```ruby filename="app/controllers/sessions_controller.rb"
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

Uma página lê com `useSession()`.

## Cache

```ruby filename="app/controllers/blog_controller.rb"
def index
  expires_in 1.minute, public: true
end
```

```nexy filename="src/rotas/blog/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

## Trabalho ativo

```ruby filename="app/controllers/signups_controller.rb"
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

Para novas tentativas e trabalhadores separados, como no Sidekiq, use Celery, RQ ou arq.

## Cabo de ação

```ruby filename="app/canais/echo_channel.rb"
class EchoChannel < ApplicationCable::Channel
  def receive(data)
    transmit(data)
  end
end
```

```python filename="src/rotas/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## Ligação direta

As trocas de páginas do Turbo Drive correspondem ao roteador cliente de um projeto no modo cliente, e os controladores de estímulo correspondem às ilhas: um pequeno componente que é hidratado dentro de uma página do servidor. Veja [Ilhas](../rendering/islands.md) e [CSR](../rendering/csr.md).

## Testes

```ruby filename="especificação/solicitações/hello_spec.rb"
RSpec.describe "Hello", type: :request do
  it "says hello" do
    get "/api/hello"
    expect(response.parsed_body).to eq("message" => "Hello")
  end
end
```

```python filename="testes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Correndo

| Trilhos | Nexy |
|---|---|
| `rails new` | `nx new` |
| `bin/rails server` | `nx dev` |
| `bin/rails routes` | `/docs` |
| `RAILS_ENV=production bin/rails server` | `nx build`, então `nx start` |
| `bin/rails test` / `rspec` | `nx test` |

## Próximas etapas

- [De Django para Nexy](django.md)
- [Do Laravel ao Nexy](laravel.md)
- [Ações](../guides/actions.md)
- [Bancos de dados](../guides/databases.md)
