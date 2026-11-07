# أنشئ تطبيق ملاحظات باستخدام Nexy، الجزء 3: المسارات الديناميكية وواجهة برمجة التطبيقات

يمنح الجزء 3 كل ملاحظة عنوان URL الخاص بها، `/notes/1`، ويقدم نفس الملاحظات مثل JSON في `/api/notes`، وكلاهما يُقرأ من وحدة Python واحدة.

**قبل أن تبدأ:** تطبيق [الجزء 2](pages-and-layouts.md).

## احتفظ بالملاحظات في وحدة واحدة

ستقرأ الصفحة وواجهة برمجة التطبيقات نفس القائمة. انقله إلى وحدة نمطية خاصة به، باستخدام وظيفة تعثر على ملاحظة واحدة:

```python filename="src/notes.py"
NOTES = {1: "Buy milk", 2: "Ship Nexy"}


def find(note_id: int) -> str | None:
    return NOTES.get(note_id)
```

## ربط كل ملاحظة بصفحتها

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

## أضف صفحة لكل ملاحظة

<!-- router:fbr,custom -->
اسم المجلد أو الملف الموجود بين قوسين هو جزء من عنوان URL: `[id].nexy` يجيب على `/notes/1`، `/notes/2`، ويمرر المقطع إلى الصفحة كدعم. `id: prop[int]` يحولها إلى رقم، فيجيب `/notes/abc` على `404` قبل تشغيل الصفحة.

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
`{id}` في مسار وحدة التحكم هو جزء من عنوان URL، تم تمريره إلى الطريقة تحت هذا الاسم. `id: int` يحوله إلى رقم، لذلك يجيب `/notes/abc` على `404` قبل تشغيل الطريقة.

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

`notFound()` يوقف الطلب بـ `404`: ملاحظة غير موجودة تجيب مثل عنوان URL غير موجود.

## قم بتقديم الملاحظات كـ JSON

<!-- router:fbr,custom -->
الملف `.py` ضمن `src/routes/` هو مسار API. كل دالة مسماة على اسم طريقة HTTP تجيب على تلك الطريقة:

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": id, "text": text} for id, text in NOTES.items()]
```
<!-- /router -->

<!-- router:modular -->
وحدات التحكم الثلاثة للملاحظات، في ملف واحد. كل طريقة تحمل اسم طريقة HTTP تجيب على هذه الطريقة:

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

تحقق من عناوين URL الثلاثة:

- <http://localhost:3000/notes/1> يظهر *شراء الحليب*؛
- <http://localhost:3000/notes/9> الإجابات *لم يتم العثور على الصفحة*;
- `curl http://localhost:3000/api/notes` المطبوعات `[{"id":1,"text":"Buy milk"},{"id":2,"text":"Ship Nexy"}]`.

تم إدراج واجهة برمجة التطبيقات (API) مع مخططها في <http://localhost:3000/docs>.

## ما تعلمته

<!-- router:fbr,custom -->
- `[id].nexy` هو جزء ديناميكي؛ `id: prop[int]` يقرأه ويحوله.
- يجيب الملف `.py` ضمن `src/routes/` على JSON، وهي وظيفة واحدة لكل طريقة HTTP.
<!-- /router -->
<!-- router:modular -->
- `{id}` في مسار وحدة التحكم يوجد مقطع ديناميكي؛ `id: int` يحوله.
- طريقة تحكم تقوم بإرجاع البيانات تجيب على JSON؛ واحد يرجع `useViews` يجيب على صفحة.
<!-- /router -->
- `notFound()` الإجابات `404` من أي مكان؛ تحافظ الوحدة المشتركة على الصفحات وواجهة برمجة التطبيقات (API) في الخطوة.

## الخطوات التالية

- [الجزء الرابع: المكونات](components.md)
- [الاستثناءات والأخطاء](../reference/exceptions.md): `notFound`، `redirect` والمخارج الأخرى
