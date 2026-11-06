# From Ruby on Rails to Nexy

In Nexy a Rails route and its controller action become one file under `src/routes/`: ERB views
become `.nexy` pages with Jinja2, strong parameters become Pydantic models, and `before_action`
becomes a `dependencies.py`.

Each section below shows a Rails habit, then the same thing in Nexy.

## A route and its action

```ruby filename="config/routes.rb"
get "/api/hello", to: "hello#show"
```

```ruby filename="app/controllers/hello_controller.rb"
class HelloController < ApplicationController
  def show
    render json: { message: "Hello" }
  end
end
```

There is no `routes.rb`: the file path is the URL, the function name is the HTTP method.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `resources`

```ruby filename="config/routes.rb"
resources :notes, only: [:index, :create, :show, :destroy]
```

The seven REST actions are spread over two files, one per URL:

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

| Rails action | Nexy |
|---|---|
| `index`, `create` | `GET`, `POST` in `notes/index.py` |
| `show`, `update`, `destroy` | `GET`, `PATCH`, `DELETE` in `notes/[id].py` |
| `new`, `edit` | `.nexy` pages, `notes/new.nexy` and `notes/[id]/edit.nexy` |

## `params` and strong parameters

```ruby filename="app/controllers/items_controller.rb"
def create
  item = params.require(:item).permit(:name, :price)
  render json: item, status: :created
end
```

The model is the permit list and the validation: unknown fields are dropped, wrong ones answer
`422`.

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

A query string parameter, `params[:q]`, is a function parameter:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## `namespace` and `before_action`

```ruby filename="config/routes.rb"
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

The namespace is the folder, and its `dependencies.py` is the `before_action` of every route in it:

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

## `after_action` and Rack middleware

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

## ERB views

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

The action and the view are one `.nexy` file; instance variables become plain names:

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

`<%= %>` escapes and `{{ }}` does not: escape what a visitor typed with `{{ value | e }}`.
`<%== %>` and `raw` are `| safe`.

## Layouts and `yield`

```erb filename="app/views/layouts/application.html.erb"
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

A `layout.nexy` in a subfolder nests inside this one, as a layout per controller does.

## Partials

```erb filename="app/views/shared/_card.html.erb"
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

```nexy filename="src/routes/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest">
  <p>This week</p>
</Card>
```

`@` is `src/`: `nx new` writes `useAliases = {"@": "src"}` in `nexyconfig.py`.

## `form_with` and `redirect_to`

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

An action is the `create` the form posts to. Its parameters are the fields, and the visitor is
redirected back to the page with a `303`:

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

## Active Record and migrations

```ruby filename="app/models/post.rb"
class Post < ApplicationRecord
  scope :published, -> { where(published: true) }
end
```

Nexy has no ORM of its own; `nx new` can scaffold SQLModel, SQLAlchemy or Tortoise-ORM. With
SQLModel:

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

| Rails | Nexy |
|---|---|
| `rails generate migration AddPosts` | `nx migrate -m "add posts"` |
| `rails db:migrate` | `nx migrate --upgrade` |

## `ActiveRecord::RecordNotFound` and `public/404.html`

```ruby filename="app/controllers/posts_controller.rb"
def show
  @post = POSTS.fetch(params[:slug]) { raise ActiveRecord::RecordNotFound }
end
```

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

`notfound.nexy` at the routes root is `public/404.html`, rendered like any page:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

## Sessions

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

A page reads it with `useSession()`.

## Caching

```ruby filename="app/controllers/blog_controller.rb"
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

## Active Job

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

For retries and separate workers, as with Sidekiq, use Celery, RQ or arq.

## Action Cable

```ruby filename="app/channels/echo_channel.rb"
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

## Hotwire

Turbo Drive's page swaps match the client router of a client-mode project, and Stimulus
controllers match islands: a small component that hydrates inside a server page. See
[Islands](../rendering/islands.md) and [CSR](../rendering/csr.md).

## Tests

```ruby filename="spec/requests/hello_spec.rb"
RSpec.describe "Hello", type: :request do
  it "says hello" do
    get "/api/hello"
    expect(response.parsed_body).to eq("message" => "Hello")
  end
end
```

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Running

| Rails | Nexy |
|---|---|
| `rails new` | `nx new` |
| `bin/rails server` | `nx dev` |
| `bin/rails routes` | `/docs` |
| `RAILS_ENV=production bin/rails server` | `nx build`, then `nx start` |
| `bin/rails test` / `rspec` | `nx test` |

## Next steps

- [From Django to Nexy](django.md)
- [From Laravel to Nexy](laravel.md)
- [Actions](../guides/actions.md)
- [Databases](../guides/databases.md)
