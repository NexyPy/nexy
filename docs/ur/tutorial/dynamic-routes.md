# Nexy کے ساتھ ایک نوٹس ایپ بنائیں، حصہ 3: متحرک راستے اور ایک API

حصہ 3 ہر ایک نوٹ کو اس کا اپنا URL دیتا ہے، `/notes/1`، اور JSON کی طرح `/api/notes` پر وہی نوٹس پیش کرتا ہے، دونوں ایک Python ماڈیول سے پڑھے جاتے ہیں۔

**شروع کرنے سے پہلے:** [پارٹ 2](pages-and-layouts.md) کی ایپ۔

## نوٹوں کو ایک ماڈیول میں رکھیں

صفحہ اور API ایک ہی فہرست کو پڑھیں گے۔ اسے اس کے اپنے ماڈیول میں منتقل کریں، اس فنکشن کے ساتھ جس میں ایک نوٹ ملتا ہے:

```python filename="src/notes.py"
NOTES = {1: "Buy milk", 2: "Ship Nexy"}


def find(note_id: int) -> str | None:
    return NOTES.get(note_id)
```

## ہر نوٹ کو اس کے صفحہ سے جوڑیں۔

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

## فی نوٹ ایک صفحہ شامل کریں۔

<!-- router:fbr,custom -->
بریکٹ میں فولڈر یا فائل کا نام یو آر ایل کا ایک حصہ ہے: `[id].nexy` جوابات `/notes/1`، `/notes/2`، اور اس حصے کو ایک سہارے کے طور پر صفحہ پر منتقل کرتا ہے۔ `id: prop[int]` اسے نمبر میں بدل دیتا ہے، لہذا صفحہ چلنے سے پہلے `/notes/abc` جواب `404` دیتا ہے۔

```nexy filename="src/routes/notes/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
text = find(id)
if text is None:
    notFound()
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
کنٹرولر کے راستے میں A `{id}` URL کا ایک حصہ ہے، جو اس نام کے تحت طریقہ کو منتقل کیا جاتا ہے۔ `id: int` اسے ایک عدد میں بدل دیتا ہے، لہذا `/notes/abc` طریقہ چلنے سے پہلے `404` جواب دیتا ہے۔

```nexy filename="src/apps/notes/note_view.nexy"
---
text: prop[str]
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

`notFound()` درخواست کو ایک `404` کے ساتھ روکتا ہے: ایک نوٹ جو موجود نہیں ہے اس طرح کے یو آر ایل جو موجود نہیں ہے۔

## JSON کے بطور نوٹس پیش کریں۔

<!-- router:fbr,custom -->
`src/routes/` کے تحت ایک `.py` فائل ایک API روٹ ہے۔ HTTP طریقہ کے نام سے منسوب ہر فنکشن اس طریقہ کا جواب دیتا ہے:

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": id, "text": text} for id, text in NOTES.items()]
```
<!-- /router -->

<!-- router:modular -->
نوٹوں کے تین کنٹرولرز، ایک فائل میں۔ HTTP طریقہ کے نام سے منسوب ہر طریقہ اس طریقہ کا جواب دیتا ہے:

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
from src.notes import NOTES, find

LAYOUT = "src/apps/layout.nexy"


def page(view: str, **context: object):
    return useViews(LAYOUT, context={"children": useViews(view, context=context)})


@Controller("/notes")
class NotesController:
    async def get(self):
        return page("src/apps/notes/notes_view.nexy")


@Controller("/notes/{id}")
class NoteController:
    async def get(self, id: int):
        text = find(id)
        if text is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", text=text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [{"id": id, "text": text} for id, text in NOTES.items()]
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NoteController, NotesApiController, NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController, NoteController, NotesApiController]
```
<!-- /router -->

تین URL چیک کریں:

- <http://localhost:3000/notes/1> شوز *دودھ خریدیں*؛
- <http://localhost:3000/notes/9> جوابات *صفحہ نہیں ملا*؛
- `curl http://localhost:3000/api/notes` پرنٹس `[{"id":1,"text":"Buy milk"},{"id":2,"text":"Ship Nexy"}]`۔

API درج ہے، اسکیما کے ساتھ، <http://localhost:3000/docs> پر۔

## جو آپ نے سیکھا۔

<!-- router:fbr,custom -->
- `[id].nexy` ایک متحرک طبقہ ہے۔ `id: prop[int]` پڑھتا ہے اور اسے تبدیل کرتا ہے۔
- `.py` فائل `src/routes/` کے تحت JSON کا جواب دیتی ہے، ایک فنکشن فی HTTP طریقہ۔
<!-- /router -->
<!-- router:modular -->
- `{id}` ایک کنٹرولر کے راستے میں ایک متحرک طبقہ ہے؛ `id: int` اسے تبدیل کرتا ہے۔
- ایک کنٹرولر طریقہ جو ڈیٹا جواب دیتا ہے JSON؛ ایک جو واپس آتا ہے `useViews` ایک صفحہ کا جواب دیتا ہے۔
<!-- /router -->
- `notFound()` جوابات `404` کہیں سے بھی۔ ایک مشترکہ ماڈیول صفحات اور API کو مرحلہ وار رکھتا ہے۔

## اگلے اقدامات

- [حصہ 4: اجزاء](components.md)
- [مستثنیات اور غلطیاں](../reference/exceptions.md): `notFound`، `redirect` اور دیگر اخراج
