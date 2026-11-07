# من روبي أون ريلز إلى Nexy

في Nexy، يصبح مسار Rails وإجراء وحدة التحكم الخاصة به ملفًا واحدًا ضمن `src/routes/`: تصبح عروض ERB صفحات `.nexy` مع Jinja2، وتصبح المعلمات القوية نماذج Pydantic، ويصبح `before_action` `dependencies.py`.

يعرض كل قسم أدناه عادة ريلز، ثم نفس الشيء في Nexy.

## الطريق وعمله

```ruby filename="التكوين/routes.rb"
get "/api/hello", to: "hello#show"
```

```ruby filename="app/controllers/hello_controller.rb"
class HelloController < ApplicationController
  def show
    render json: { message: "Hello" }
  end
end
```

لا يوجد `routes.rb`: مسار الملف هو عنوان URL، واسم الوظيفة هو طريقة HTTP.

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `resources`

```ruby filename="التكوين/routes.rb"
resources :notes, only: [:index, :create, :show, :destroy]
```

تتوزع إجراءات REST السبعة على ملفين، واحد لكل عنوان URL:

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

| عمل القضبان | نكسي |
|---|---|
| `index`، `create` | `GET`، `POST` في `notes/index.py` |
| `show`، `update`، `destroy` | `GET`، `PATCH`، `DELETE` في `notes/[id].py` |
| `new`، `edit` | `.nexy` صفحة، `notes/new.nexy` و `notes/[id]/edit.nexy` |

## `params` ومعلمات قوية

```ruby filename="app/controllers/items_controller.rb"
def create
  item = params.require(:item).permit(:name, :price)
  render json: item, status: :created
end
```

النموذج هو قائمة التصاريح والتحقق: يتم إسقاط الحقول غير المعروفة، والإجابة الخاطئة `422`.

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

معلمة سلسلة الاستعلام، `params[:q]`، هي معلمة دالة:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## `namespace` و `before_action`

```ruby filename="التكوين/routes.rb"
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

مساحة الاسم هي المجلد، و `dependencies.py` الخاص به هو `before_action` لكل مسار فيه:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

```python filename="src/routes/admin/dependeency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## `after_action` والبرمجيات الوسيطة Rack

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

## وجهات نظر ERB

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

فالفعل والعرض ملف واحد `.nexy`؛ تصبح متغيرات الحالة أسماء عادية:

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

`<%= %>` يهرب و `{{ }}` لا: يهرب مما كتبه الزائر بـ `{{ value | e }}`. `<%== %>` و `raw` هما `| safe`.

## التخطيطات و `yield`

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

يوجد `layout.nexy` في مجلد فرعي داخل هذا المجلد، كما يفعل التخطيط لكل وحدة تحكم.

## جزئيات

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

`@` هو `src/`: `nx new` يكتب `useAliases = {"@": "src"}` في `nexyconfig.py`.

## `form_with` و `redirect_to`

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

الإجراء هو `create` الذي يرسل إليه النموذج. معلماتها هي الحقول، ويتم إعادة توجيه الزائر مرة أخرى إلى الصفحة باستخدام `303`:

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

## السجل النشط والهجرات

```ruby filename="التطبيق/النماذج/post.rb"
class Post < ApplicationRecord
  scope :published, -> { where(published: true) }
end
```

لا يوجد لدى Nexy ORM خاص بها؛ `nx new` يمكن أن يكون سقالة SQLModel، SQLAlchemy أو سلحفاة-ORM. مع SQLModel:

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

| القضبان | نكسي |
|---|---|
| `rails generate migration AddPosts` | `nx migrate -m "add posts"` |
| `rails db:migrate` | `nx migrate --upgrade` |

## `ActiveRecord::RecordNotFound` و `public/404.html`

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

`notfound.nexy` في جذر المسارات هو `public/404.html`، ويتم عرضه مثل أي صفحة:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

## الجلسات

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

صفحة تقرأها بـ `useSession()`.

## التخزين المؤقت

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

## الوظيفة النشطة

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

لإعادة المحاولة وفصل العمال، كما هو الحال مع Sidekiq، استخدم Celery أو RQ أو arq.

## كابل العمل

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

## هوتواير

تتطابق مبادلات صفحات Turbo Drive مع جهاز توجيه العميل لمشروع وضع العميل، وتتوافق وحدات تحكم Stimulus مع الجزر: مكون صغير يتم ترطيبه داخل صفحة الخادم. انظر [الجزر](../rendering/islands.md) و [المسؤولية الاجتماعية للشركات](../rendering/csr.md).

## الاختبارات

```ruby filename="المواصفات/الطلبات/hello_spec.rb"
RSpec.describe "Hello", type: :request do
  it "says hello" do
    get "/api/hello"
    expect(response.parsed_body).to eq("message" => "Hello")
  end
end
```

```python filename="الاختبارات/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## الجري

| القضبان | نكسي |
|---|---|
| `rails new` | `nx new` |
| `bin/rails server` | `nx dev` |
| `bin/rails routes` | `/docs` |
| `RAILS_ENV=production bin/rails server` | `nx build`، ثم `nx start` |
| `bin/rails test` / `rspec` | `nx test` |

## الخطوات التالية

- [من Django إلى نكسي](django.md)
- [من لارافيل إلى نكسي](laravel.md)
- [الإجراءات](../guides/actions.md)
- [قواعد البيانات](../guides/databases.md)
