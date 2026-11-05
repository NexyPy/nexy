# البرنامج التعليمي: إنشاء صفحة ملاحظات في 10 دقائق

ستقوم بإنشاء مشروع وإضافة صفحة وإضافة نقطة نهاية Python ومشاركة البيانات بينهما والإنشاء للإنتاج. تنتهي بقائمة واحدة من الملاحظات التي يتم تقديمها كصفحة وكJSON.

هل أنت جديد في نيكسي؟ قم بإجراء [البدء السريع](quick-start.md) أولاً: يستغرق الأمر ثلاث دقائق.

```diagram filename="البرنامج التعليمي كله في سطر واحد"
uvx nexy new notes ──► edit layout ──► add page ──► add endpoint ──► share data ──► nx build ──► nx start
```

## 1. قم بإنشاء المشروع

```bash
uvx nexy new notes
cd notes
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

`uvx` يأتي مع [uv](https://docs.astral.sh/uv/) ويقوم فقط بإنشاء المشروع. كل أمر بعد تشغيله داخل البيئة الافتراضية للمشروع (أو كـ `uv run nexy dev`).

اختر جهاز التوجيه المستند إلى الملف، ومشروع الويب، وأي إطار عمل للعميل (أو لا شيء). مفتوح
<http://localhost:3000>. الخطوات الطويلة تطبع سطراً واحداً مع مدته، كما يفعل `uv`.

<!-- router:modular -->
أجب `No` على موجه جهاز التوجيه المستند إلى الملف: `nx new` يدعم جهاز التوجيه المعياري في `src/apps/` بدلاً من `src/routes/`.
<!-- /router -->

<!-- router:custom -->
أجب `Yes` على موجه التوجيه المستند إلى الملف للصفحات، ثم قم بتثبيت `APIRouter` الموجود لديك في `nexyconfig.py`: يتواجد جهازا التوجيه معًا.
<!-- /router -->

## 2. قم بتحرير التخطيط

<!-- router:fbr,custom -->
يمتلك `src/routes/layout.nexy` مستند HTML (مع توجيه العميل React فهو `layout.tsx`). تغيير `<title>`:

```nexy
<title>Notes</title>
```

حفظ: يتم إعادة تحميل المتصفح. انظر [التخطيطات](../routing/fbr/layouts/README.md).
<!-- /router -->

<!-- router:modular -->
تعرض وحدة التحكم `src/apps/layout.nexy` حول العرض، ويمتلك هذا الملف مستند HTML. تغيير `<title>`:

```nexy
<title>Notes</title>
```

حفظ: يتم إعادة تحميل المتصفح. انظر [المشاهدات من وحدة التحكم](../routing/modular/README.md#views-from-a-controller).
<!-- /router -->

## 3. أضف صفحة

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

فتح <http://localhost:3000/notes>: يجب أن تشاهد رصاصتين. ويتم تقديمه في `/notes`. الجزء الذي بين `---` هو Python، والباقي Jinja2.
<!-- /router -->

<!-- router:modular -->
تقوم وحدة التحكم بإرجاع طريقة عرض. إنشاء `src/apps/notes_view.nexy`:

```nexy filename="src/apps/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

أعلن المسار في `src/apps/app_controller.py` وأضف وحدة التحكم إلى الوحدة:

```python filename="src/apps/app_controller.py"
@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/notes_view.nexy"),
        })
```

```python filename="src/apps/app_module.py"
from .app_controller import AppController, NotesController

controllers = [AppController, NotesController]
```

فتح <http://localhost:3000/notes>: يجب أن تشاهد رصاصتين. فما بين `---` هو Python، والباقي Jinja2.
<!-- /router -->

## 4. أضف نقطة نهاية

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes.py"
async def GET():
    return [{"id": 1, "text": "Buy milk"}]
```

```bash
curl http://localhost:3000/api/notes
```

يجب أن تحصل على `[{"id":1,"text":"Buy milk"}]`. اسم الوظيفة هو طريقة HTTP. توجد مستندات API التفاعلية في `/docs`.
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/app_controller.py"
@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": 1, "text": "Buy milk"}]
```

أضف `NotesApiController` إلى `controllers` في `src/apps/app_module.py`، ثم قم بتشغيل:

```bash
curl http://localhost:3000/api/notes
```

يجب أن تحصل على `[{"id":1,"text":"Buy milk"}]`. اسم الطريقة هو طريقة HTTP. توجد مستندات API التفاعلية في `/docs`.
<!-- /router -->

## 5. مشاركة البيانات

انقل القائمة إلى وحدة Python واستخدمها في كلا الملفين:

```python filename="src/notes.py"
NOTES = ["Buy milk", "Ship Nexy"]
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes_view.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/apps/app_controller.py"
from src.notes import NOTES


@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

## 6. البناء والخدمة

```bash
nx build
nx start
```

`nx build` يطبع كل مرحلة مع مدتها. `nx start` يخدم الإخراج المترجم مع Uvicorn: لا توجد عملية عقدة في وقت التشغيل.

## أين التالي

- [التوجيه](../routing/README.md)]: المقاطع والمجموعات الديناميكية
- [الإجراءات](../guides/actions.md): اتصل بـ Python من النموذج أو من العميل
- [الاختبار](../guides/testing.md)]: صفحات الاختبار ونقاط النهاية
- [نشر](../deployment/README.md): الحاويات والوكلاء العكسيين
