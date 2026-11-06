# 从 Ruby on Rails 到 Nexy

在 Nexy 中，Rails 路由及其控制器操作成为 `src/routes/` 下的一个文件：ERB 视图成为带有 Jinja2 的 `.nexy` 页面，强参数成为 Pydantic 模型，`before_action` 成为 `dependencies.py`。

下面的每个部分都显示了 Rails 的习惯，然后是 Nexy 中的相同内容。

## 路线及其动作

```ruby filename="配置/routes.rb"
get "/api/hello", to: "hello#show"
```

```ruby filename="应用程序/控制器/hello_controller.rb"
class HelloController < ApplicationController
  def show
    render json: { message: "Hello" }
  end
end
```

没有 `routes.rb`：文件路径是URL，函数名称是HTTP方法。

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `resources`

```ruby filename="配置/routes.rb"
resources :notes, only: [:index, :create, :show, :destroy]
```

七个 REST 操作分布在两个文件中，每个 URL 一个：

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

| 轨道动作 | 内克西 |
|---|---|
| `index`，`create` | `GET`、`POST` 在 `notes/index.py` |
| `show`、`update`、`destroy` | `GET`、`PATCH`、`DELETE` 在 `notes/[id].py` |
| `new`，`edit` | `.nexy` 页，`notes/new.nexy` 和 `notes/[id]/edit.nexy` |

## `params` 和强大的参数

```ruby filename="应用程序/控制器/items_controller.rb"
def create
  item = params.require(:item).permit(:name, :price)
  render json: item, status: :created
end
```

该模型是许可列表和验证：未知字段被删除，错误的答案 `422`。

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

查询字符串参数 `params[:q]` 是一个函数参数：

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## `namespace` 和 `before_action`

```ruby filename="配置/routes.rb"
namespace :admin do
  get "stats", to: "stats#show"
end
```

```ruby filename="应用程序/控制器/管理/base_controller.rb"
class Admin::BaseController < ApplicationController
  before_action :require_admin

  private

  def require_admin
    head :forbidden unless request.headers["X-Role"] == "admin"
  end
end
```

命名空间就是文件夹，它的 `dependencies.py` 是其中每个路由的 `before_action`：

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

```python filename="src/routes/admin/dependency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `after_action` 和 Rack 中间件

```ruby filename="应用程序/控制器/application_controller.rb"
after_action { response.set_header("X-App", "demo") }
```

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## 雇员再培训局的意见

```ruby filename="应用程序/控制器/user_controller.rb"
def index
  @users = [{ name: "Ada" }, { name: "Alan" }]
end
```

```erb filename="应用程序/视图/用户/index.html.erb"
<ul>
  <% @users.each do |user| %>
  <li><%= user[:name] %></li>
  <% end %>
</ul>
```

动作和视图是一个 `.nexy` 文件；实例变量变成普通名称：

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

`<%= %>` 转义，而 `{{ }}` 不转义：转义访问者用 `{{ value | e }}` 键入的内容。 `<%== %>` 和 `raw` 是 `| safe`。

## 布局和 `yield`

```erb filename="应用程序/视图/布局/application.html.erb"
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

子文件夹中的 `layout.nexy` 嵌套在该文件夹内，就像每个控制器的布局一样。

## 偏音

```erb filename="应用程序/视图/共享/_card.html.erb"
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

`@` 是 `src/`：`nx new` 在 `nexyconfig.py` 中写入 `useAliases = {"@": "src"}`。

## `form_with` 和 `redirect_to`

```erb filename="应用程序/视图/笔记/index.html.erb"
<%= form_with url: notes_path do |form| %>
  <%= form.text_field :title %>
  <%= form.submit "Add" %>
<% end %>
```

```ruby filename="应用程序/控制器/notes_controller.rb"
def create
  Note.create!(title: params[:title])
  redirect_to notes_path
end
```

操作是表单发布到的 `create`。它的参数是字段，访问者被重定向回带有 `303` 的页面：

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

## Active Record 和迁移

```ruby filename="应用程序/模型/post.rb"
class Post < ApplicationRecord
  scope :published, -> { where(published: true) }
end
```

Nexy 没有自己的 ORM； `nx new` 可以搭建 SQLModel、SQLAlchemy 或Tortoise-ORM。与 SQLModel：

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

| 导轨 | 内克西 |
|---|---|
| `rails generate migration AddPosts` | `nx migrate -m "add posts"` |
| `rails db:migrate` | `nx migrate --upgrade` |

## `ActiveRecord::RecordNotFound` 和 `public/404.html`

```ruby filename="应用程序/控制器/posts_controller.rb"
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

路由根目录中的 `notfound.nexy` 是 `public/404.html`，像任何页面一样呈现：

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

## 会议

```ruby filename="应用程序/控制器/sessions_controller.rb"
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

页面用 `useSession()`读取它。

## 缓存

```ruby filename="应用程序/控制器/blog_controller.rb"
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

## 活跃工作

```ruby filename="应用程序/控制器/signups_controller.rb"
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

对于重试和单独的工作程序，与 Sidekiq 一样，使用 Celery、RQ 或 arq。

## 行动电缆

```ruby filename="应用程序/频道/echo_channel.rb"
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

## 热线

Turbo Drive 的页面交换与客户端模式项目的客户端路由器相匹配，而 Stimulus 控制器与岛屿相匹配：一个在服务器页面内水合的小组件。参见[岛屿](../rendering/islands.md) 和[CSR](../rendering/csr.md)。

## 测试

```ruby filename="规格/请求/hello_spec.rb"
RSpec.describe "Hello", type: :request do
  it "says hello" do
    get "/api/hello"
    expect(response.parsed_body).to eq("message" => "Hello")
  end
end
```

```python filename="测试/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## 跑步

| 导轨 | 内克西 |
|---|---|
| `rails new` | `nx new` |
| `bin/rails server` | `nx dev` |
| `bin/rails routes` | `/docs` |
| `RAILS_ENV=production bin/rails server` | `nx build`，然后 `nx start` |
| `bin/rails test` / `rspec` | `nx test` |

## 后续步骤

- [从 Django 到 Nexy](django.md)
- [从 Laravel 到 Nexy](laravel.md)
- [行动](../guides/actions.md)
- [数据库](../guides/databases.md)
