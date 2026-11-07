# روبی آن ریلز سے لے کر نیکسی تک

Nexy میں ایک ریل روٹ اور اس کا کنٹرولر ایکشن `src/routes/` کے تحت ایک فائل بن جاتا ہے: ERB ویوز Jinja2 کے ساتھ `.nexy` صفحات بن جاتے ہیں، مضبوط پیرامیٹرز Pydantic ماڈل بن جاتے ہیں، اور `before_action` ایک `dependencies.py` بن جاتا ہے۔

ذیل میں ہر سیکشن ریلوں کی عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔

## ایک راستہ اور اس کا عمل

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

کوئی `routes.rb` نہیں ہے: فائل کا راستہ URL ہے، فنکشن کا نام HTTP طریقہ ہے۔

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `resources`

```ruby filename="config/routes.rb"
resources :notes, only: [:index, :create, :show, :destroy]
```

سات REST اعمال دو فائلوں پر پھیلے ہوئے ہیں، ایک فی URL:

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

| ریلوں کی کارروائی | نیکسی |
|---|---|
| `index`، `create` | `GET`، `POST` `notes/index.py` میں |
| `show`، `update`، `destroy` | `GET`، `PATCH`، `DELETE` `notes/[id].py` میں |
| `new`، `edit` | `.nexy` صفحات، `notes/new.nexy` اور `notes/[id]/edit.nexy` |

## `params` اور مضبوط پیرامیٹرز

```ruby filename="app/controllers/items_controller.rb"
def create
  item = params.require(:item).permit(:name, :price)
  render json: item, status: :created
end
```

ماڈل اجازت نامے کی فہرست اور توثیق ہے: نامعلوم فیلڈز چھوڑے گئے ہیں، غلط جوابات ہیں `422`۔

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

ایک سوال سٹرنگ پیرامیٹر، `params[:q]`، ایک فنکشن پیرامیٹر ہے:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## `namespace` اور `before_action`

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

نام کی جگہ فولڈر ہے، اور اس کا `dependencies.py` ہر راستے کا `before_action` ہے:

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

## `after_action` اور ریک مڈل ویئر

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

## ERB مناظر

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

ایکشن اور ویو ایک `.nexy` فائل ہیں۔ مثال کے متغیر سادہ نام بن جاتے ہیں:

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

`<%= %>` فرار ہوتا ہے اور `{{ }}` نہیں ہوتا: اس سے بچ جاتا ہے جسے ایک وزیٹر `{{ value | e }}` کے ساتھ ٹائپ کرتا ہے۔ `<%== %>` اور `raw` ہیں `| safe`۔

## ترتیب اور `yield`

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

ذیلی فولڈر میں ایک `layout.nexy` اس کے اندر گھوںسلا کرتا ہے، جیسا کہ ایک ترتیب فی کنٹرولر کرتا ہے۔

## جزوی

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

`@` ہے `src/`: `nx new` `nexyconfig.py` میں `useAliases = {"@": "src"}` لکھتے ہیں۔

## `form_with` اور `redirect_to`

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

ایک عمل `create` فارم پوسٹ کرتا ہے۔ اس کے پیرامیٹرز فیلڈز ہیں، اور وزیٹر کو `303` کے ساتھ صفحہ پر واپس بھیج دیا جاتا ہے:

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

## فعال ریکارڈ اور ہجرت

```ruby filename="app/models/post.rb"
class Post < ApplicationRecord
  scope :published, -> { where(published: true) }
end
```

Nexy کا اپنا کوئی ORM نہیں ہے۔ `nx new` سکیفولڈ SQLModel، SQLAlchemy یا کچھوا-ORM کر سکتے ہیں۔ کے ساتھ SQLModel:

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

| ریل | نیکسی |
|---|---|
| `rails generate migration AddPosts` | `nx migrate -m "add posts"` |
| `rails db:migrate` | `nx migrate --upgrade` |

## `ActiveRecord::RecordNotFound` اور `public/404.html`

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

روٹس روٹ پر `notfound.nexy` ہے `public/404.html`، کسی بھی صفحے کی طرح پیش کیا جاتا ہے:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

## سیشنز

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

ایک صفحہ اسے `useSession()` کے ساتھ پڑھتا ہے۔

## کیشنگ

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

## ایکٹو جاب

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

دوبارہ کوشش کرنے اور علیحدہ کارکنوں کے لیے، جیسا کہ Sidekiq کے ساتھ، Celery، RQ یا arq استعمال کریں۔

## ایکشن کیبل

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

## ہاٹ وائر

ٹربو ڈرائیو کے صفحہ کی تبدیلیاں کلائنٹ موڈ پروجیکٹ کے کلائنٹ روٹر سے ملتی ہیں، اور محرک کنٹرولرز جزیروں سے ملتے ہیں: ایک چھوٹا سا جزو جو سرور کے صفحے کے اندر ہائیڈریٹ ہوتا ہے۔ دیکھیں [جزیرے](../rendering/islands.md) اور [CSR](../rendering/csr.md)۔

## ٹیسٹ

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

## چل رہا ہے۔

| ریل | نیکسی |
|---|---|
| `rails new` | `nx new` |
| `bin/rails server` | `nx dev` |
| `bin/rails routes` | `/docs` |
| `RAILS_ENV=production bin/rails server` | `nx build`، پھر `nx start` |
| `bin/rails test` / `rspec` | `nx test` |

## اگلے اقدامات

- [سے Django سے Nexy](django.md)
- [لاراویل سے نیکسی تک](laravel.md)
- [اعمال](../guides/actions.md)
- [ڈیٹا بیس](../guides/databases.md)
