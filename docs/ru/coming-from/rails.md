# От Ruby on Rails до Nexy

В Nexy маршрут Rails и действие его контроллера становятся одним файлом в `src/routes/`: представления ERB становятся `.nexy` страницами с Jinja2, строгие параметры становятся Pydantic моделями, а `before_action` становится `dependencies.py`.

В каждом разделе ниже показаны привычки Rails, а затем то же самое в Nexy.

## Маршрут и его действие

```ruby filename="config/routes.rb"
get "/api/hello", to: "hello#show"
```

```ruby filename="приложение/контроллеры/hello_controller.rb"
class HelloController < ApplicationController
  def show
    render json: { message: "Hello" }
  end
end
```

Нет `routes.rb`: путь к файлу - URL-адрес, имя функции - метод HTTP.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `resources`

```ruby filename="config/routes.rb"
resources :notes, only: [:index, :create, :show, :destroy]
```

Семь действий REST распределены по двум файлам, по одному на каждый URL-адрес:

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

| Рельсовое действие | Некси |
|---|---|
| `index`, `create` | `GET`, `POST` в `notes/index.py` |
| `show`, `update`, `destroy` | `GET`, `PATCH`, `DELETE` в `notes/[id].py` |
| `new`, `edit` | Страницы `.nexy`, `notes/new.nexy` и `notes/[id]/edit.nexy` |

## `params` и сильные параметры

```ruby filename="приложение/контроллеры/items_controller.rb"
def create
  item = params.require(:item).permit(:name, :price)
  render json: item, status: :created
end
```

Моделью является список разрешений и проверка: неизвестные поля отбрасываются, неправильные отвечают `422`.

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

Параметр строки запроса `params[:q]` является параметром функции:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## `namespace` и `before_action`

```ruby filename="config/routes.rb"
namespace :admin do
  get "stats", to: "stats#show"
end
```

```ruby filename="приложение/контроллеры/admin/base_controller.rb"
class Admin::BaseController < ApplicationController
  before_action :require_admin

  private

  def require_admin
    head :forbidden unless request.headers["X-Role"] == "admin"
  end
end
```

Пространство имен - это папка, а ее `dependencies.py` - это `before_action` каждого маршрута в ней:

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

## `after_action` и промежуточное программное обеспечение Rack

```ruby filename="приложение/контроллеры/application_controller.rb"
after_action { response.set_header("X-App", "demo") }
```

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Просмотры Еврорадио

```ruby filename="приложение/контроллеры/users_controller.rb"
def index
  @users = [{ name: "Ada" }, { name: "Alan" }]
end
```

```erb filename="приложение/views/users/index.html.erb"
<ul>
  <% @users.each do |user| %>
  <li><%= user[:name] %></li>
  <% end %>
</ul>
```

Действие и представление представляют собой один `.nexy` файл; переменные экземпляра становятся простыми именами:

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

`<%= %>` экранируется, а `{{ }}` - нет: экранируйте то, что посетитель набрал с помощью `{{ value | e }}`. `<%== %>` и `raw` - это `| safe`.

## Макеты и `yield`

```erb filename="приложение/views/layouts/application.html.erb"
<!DOCTYPE html>
<html>
  <body><%= yield %></body>
</html>
```

```nexy filename="src/маршруты/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children | safe }}</body>
</html>
```

`layout.nexy` в подпапке вкладывается в эту, как и макет каждого контроллера.

## Частичные

```erb filename="приложение/views/shared/_card.html.erb"
<article><h2><%= title %></h2><%= yield %></article>
```

```erb
<%= render "shared/card", title: "Latest" do %><p>This week</p><% end %>
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

## `form_with` и `redirect_to`

```erb filename="приложение/views/notes/index.html.erb"
<%= form_with url: notes_path do |form| %>
  <%= form.text_field :title %>
  <%= form.submit "Add" %>
<% end %>
```

```ruby filename="приложение/контроллеры/notes_controller.rb"
def create
  Note.create!(title: params[:title])
  redirect_to notes_path
end
```

Действие - это `create`, куда отправляется форма. Его параметрами являются поля, и посетитель перенаправляется обратно на страницу с `303`:

```python filename="src/actions/notes.py"
from nexy.decorators import Action

TITLES: list[str] = []


@Action
async def add_note(title: str) -> None:
    TITLES.append(title)
```

```nexy filename="src/маршруты/notes.nexy"
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

## Активная запись и миграции

```ruby filename="приложение/модели/post.rb"
class Post < ApplicationRecord
  scope :published, -> { where(published: true) }
end
```

У Nexy нет собственного ORM; `nx new` может поддерживать SQLModel, SQLAlchemy или Tortoise-ORM. С SQLModel:

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

| Рельсы | Некси |
|---|---|
| `rails generate migration AddPosts` | `nx migrate -m "add posts"` |
| `rails db:migrate` | `nx migrate --upgrade` |

## `ActiveRecord::RecordNotFound` и `public/404.html`

```ruby filename="приложение/контроллеры/posts_controller.rb"
def show
  @post = POSTS.fetch(params[:slug]) { raise ActiveRecord::RecordNotFound }
end
```

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

`notfound.nexy` в корне маршрутов - `public/404.html`, отображается как любая страница:

```nexy filename="источник/маршруты/notfound.nexy"
<h1>Not found</h1>
```

## Сессии

```ruby filename="приложение/контроллеры/sessions_controller.rb"
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

Страница читает его с помощью `useSession()`.

## Кэширование

```ruby filename="приложение/контроллеры/blog_controller.rb"
def index
  expires_in 1.minute, public: true
end
```

```nexy filename="src/маршруты/блог/index.nexy"
---
revalidate = 60
---
<h1>Blog</h1>
```

## Активная работа

```ruby filename="приложение/контроллеры/signups_controller.rb"
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

Для повторных попыток и отдельных рабочих процессов, как в случае с Sidekiq, используйте Celery, RQ или arq.

## Кабель действия

```ruby filename="приложение/каналы/echo_channel.rb"
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

Смена страниц Turbo Drive соответствует клиентскому маршрутизатору проекта в клиентском режиме, а контроллеры Stimulus соответствуют островам: небольшому компоненту, который находится внутри серверной страницы. См. [Острова](../rendering/islands.md) и [CSR](../rendering/csr.md).

## Тесты

```ruby filename="спецификация/запросы/hello_spec.rb"
RSpec.describe "Hello", type: :request do
  it "says hello" do
    get "/api/hello"
    expect(response.parsed_body).to eq("message" => "Hello")
  end
end
```

```python filename="тесты/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Бег

| Рельсы | Некси |
|---|---|
| `rails new` | `nx new` |
| `bin/rails server` | `nx dev` |
| `bin/rails routes` | `/docs` |
| `RAILS_ENV=production bin/rails server` | `nx build`, затем `nx start` |
| `bin/rails test` / `rspec` | `nx test` |

## Следующие шаги

- [От Django до Некси](django.md)
- [От Laravel до Nexy](laravel.md)
- [Действия](../guides/actions.md)
- [Базы данных](../guides/databases.md)
