# रूबी ऑन रेल्स से लेकर नेक्सी तक

नेक्सी में एक रेल मार्ग और उसकी नियंत्रक कार्रवाई `src/routes/` के अंतर्गत एक फ़ाइल बन जाती है: ईआरबी दृश्य Jinja2 के साथ `.nexy` पृष्ठ बन जाते हैं, मजबूत पैरामीटर Pydantic मॉडल बन जाते हैं, और `before_action` एक `dependencies.py` बन जाते हैं।

नीचे प्रत्येक अनुभाग एक रेल आदत दिखाता है, फिर नेक्सी में भी वही चीज़।

## एक मार्ग और उसकी क्रिया

```ruby filename="config/routes.rb"
get "/api/hello", to: "hello#show"
```

```ruby filename="ऐप/नियंत्रक/hello_controller.rb"
class HelloController < ApplicationController
  def show
    render json: { message: "Hello" }
  end
end
```

कोई `routes.rb` नहीं है: फ़ाइल पथ यूआरएल है, फ़ंक्शन नाम HTTP विधि है।

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `resources`

```ruby filename="config/routes.rb"
resources :notes, only: [:index, :create, :show, :destroy]
```

सात REST क्रियाएँ दो फ़ाइलों में फैली हुई हैं, प्रति URL एक:

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

| रेल कार्रवाई | नेक्सी |
|---|---|
| `index`, `create` | `GET`, `POST` में `notes/index.py` |
| `show`, `update`, `destroy` | `GET`, `PATCH`, `DELETE` में `notes/[id].py` |
| `new`, `edit` | `.nexy` पेज, `notes/new.nexy` और `notes/[id]/edit.nexy` |

## `params` और मजबूत पैरामीटर

```ruby filename="ऐप/नियंत्रक/आइटम_नियंत्रक.आरबी"
def create
  item = params.require(:item).permit(:name, :price)
  render json: item, status: :created
end
```

मॉडल परमिट सूची और सत्यापन है: अज्ञात फ़ील्ड हटा दिए जाते हैं, गलत उत्तर देते हैं `422`।

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

एक क्वेरी स्ट्रिंग पैरामीटर, `params[:q]`, एक फ़ंक्शन पैरामीटर है:

```python filename="src/routes/api/search.py"
async def GET(q: str = "", page: int = 1):
    return {"q": q, "page": page}
```

## `namespace` और `before_action`

```ruby filename="config/routes.rb"
namespace :admin do
  get "stats", to: "stats#show"
end
```

```ruby filename="ऐप/कंट्रोलर/एडमिन/बेस_कंट्रोलर.आरबी"
class Admin::BaseController < ApplicationController
  before_action :require_admin

  private

  def require_admin
    head :forbidden unless request.headers["X-Role"] == "admin"
  end
end
```

नेमस्पेस फ़ोल्डर है, और इसका `dependencies.py` इसमें प्रत्येक रूट का `before_action` है:

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

## `after_action` और रैक मिडलवेयर

```ruby filename="ऐप/नियंत्रक/एप्लिकेशन_कंट्रोलर.आरबी"
after_action { response.set_header("X-App", "demo") }
```

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## ईआरबी विचार

```ruby filename="ऐप/नियंत्रक/उपयोगकर्ता_नियंत्रक.आरबी"
def index
  @users = [{ name: "Ada" }, { name: "Alan" }]
end
```

```erb filename="ऐप/व्यू/यूजर्स/index.html.erb"
<ul>
  <% @users.each do |user| %>
  <li><%= user[:name] %></li>
  <% end %>
</ul>
```

क्रिया और दृश्य एक `.nexy` फ़ाइल हैं; उदाहरण चर सादे नाम बन जाते हैं:

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

`<%= %>` बच जाता है और `{{ }}` नहीं बचता: विज़िटर ने `{{ value | e }}` से जो टाइप किया है वह बच जाता है। `<%== %>` और `raw` `| safe` हैं।

## लेआउट और `yield`

```erb filename="ऐप/व्यू/लेआउट/एप्लिकेशन.html.erb"
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

एक सबफ़ोल्डर में एक `layout.nexy` इसके अंदर घोंसला बनाता है, जैसा कि प्रति नियंत्रक एक लेआउट करता है।

## आंशिक

```erb filename="ऐप/व्यू/शेयर्ड/_कार्ड.html.erb"
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

`@` है `src/`: `nx new` `nexyconfig.py` में `useAliases = {"@": "src"}` लिखता है।

## `form_with` और `redirect_to`

```erb filename="ऐप/व्यू/नोट्स/index.html.erb"
<%= form_with url: notes_path do |form| %>
  <%= form.text_field :title %>
  <%= form.submit "Add" %>
<% end %>
```

```ruby filename="ऐप/कंट्रोलर/नोट्स_कंट्रोलर.आरबी"
def create
  Note.create!(title: params[:title])
  redirect_to notes_path
end
```

एक क्रिया वह है `create` प्रपत्र जिस पर पोस्ट किया जाता है। इसके पैरामीटर फ़ील्ड हैं, और विज़िटर को `303` के साथ पृष्ठ पर वापस भेज दिया जाता है:

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

## सक्रिय रिकॉर्ड और माइग्रेशन

```ruby filename="ऐप/मॉडल/पोस्ट.आरबी"
class Post < ApplicationRecord
  scope :published, -> { where(published: true) }
end
```

नेक्सी का अपना कोई ORM नहीं है; `nx new` मचान SQLModel, SQLAlchemy या कछुआ-ओआरएम कर सकता है। SQLModel के साथ:

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

| रेल | नेक्सी |
|---|---|
| `rails generate migration AddPosts` | `nx migrate -m "add posts"` |
| `rails db:migrate` | `nx migrate --upgrade` |

## `ActiveRecord::RecordNotFound` और `public/404.html`

```ruby filename="ऐप/कंट्रोलर/पोस्ट_कंट्रोलर.आरबी"
def show
  @post = POSTS.fetch(params[:slug]) { raise ActiveRecord::RecordNotFound }
end
```

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

`notfound.nexy` रूट रूट पर `public/404.html` है, जिसे किसी भी पेज की तरह प्रस्तुत किया गया है:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

## सत्र

```ruby filename="ऐप/नियंत्रक/सत्र_नियंत्रक.आरबी"
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

एक पृष्ठ इसे `useSession()` के साथ पढ़ता है।

## कैशिंग

```ruby filename="ऐप/कंट्रोलर/ब्लॉग_कंट्रोलर.आरबी"
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

## सक्रिय कार्य

```ruby filename="ऐप/नियंत्रक/signups_controller.rb"
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

पुनर्प्रयासों और अलग-अलग श्रमिकों के लिए, जैसे कि साइडकीक के साथ, सेलेरी, आरक्यू या आर्क का उपयोग करें।

## एक्शन केबल

```ruby filename="ऐप/चैनल/echo_channel.rb"
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

## हॉटवायर

टर्बो ड्राइव का पेज स्वैप क्लाइंट-मोड प्रोजेक्ट के क्लाइंट राउटर से मेल खाता है, और स्टिमुलस नियंत्रक द्वीपों से मेल खाते हैं: एक छोटा घटक जो सर्वर पेज के अंदर हाइड्रेट होता है। [द्वीप](../rendering/islands.md) और [सीएसआर](../rendering/csr.md) देखें।

## परीक्षण

```ruby filename="कल्पना/अनुरोध/hello_spec.rb"
RSpec.describe "Hello", type: :request do
  it "says hello" do
    get "/api/hello"
    expect(response.parsed_body).to eq("message" => "Hello")
  end
end
```

```python filename="परीक्षण/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## चल रहा है

| रेल | नेक्सी |
|---|---|
| `rails new` | `nx new` |
| `bin/rails server` | `nx dev` |
| `bin/rails routes` | `/docs` |
| `RAILS_ENV=production bin/rails server` | `nx build`, फिर `nx start` |
| `bin/rails test` / `rspec` | `nx test` |

## अगले चरण

- [से Django से नेक्सी](django.md)
- [लारवेल से नेक्सी तक](laravel.md)
- [क्रियाएँ](../guides/actions.md)
- [डेटाबेस](../guides/databases.md)
