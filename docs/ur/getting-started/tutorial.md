# سبق: 10 منٹ میں نوٹس کا صفحہ بنائیں

آپ ایک پروجیکٹ بنائیں گے، ایک صفحہ شامل کریں گے، ایک Python اختتامی نقطہ شامل کریں گے، ان کے درمیان ڈیٹا کا اشتراک کریں گے، اور پیداوار کے لیے تعمیر کریں گے۔ آپ نوٹوں کی ایک فہرست کے ساتھ ختم کرتے ہیں جو صفحہ کے طور پر اور JSON کے طور پر پیش کیے جاتے ہیں۔

Nexy میں نئے ہیں؟ پہلے [کوئیک اسٹارٹ](quick-start.md) کریں: اس میں تین منٹ لگتے ہیں۔

```diagram filename="ایک لائن میں پورا ٹیوٹوریل"
uvx nexy new notes ──► edit layout ──► add page ──► add endpoint ──► share data ──► nx build ──► nx start
```

## 1. پروجیکٹ بنائیں

```bash
uvx nexy new notes
cd notes
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

`uvx` [uv](https://docs.astral.sh/uv/) کے ساتھ آتا ہے اور صرف پروجیکٹ بناتا ہے۔ اس کے بعد ہر کمانڈ پروجیکٹ کے ورچوئل ماحول کے اندر چلتی ہے (یا بطور `uv run nexy dev`)۔

فائل پر مبنی روٹر، ایک ویب پروجیکٹ، اور کوئی بھی کلائنٹ فریم ورک (یا کوئی نہیں) چنیں۔ کھولیں۔
<http://localhost:3000>۔ لمبے قدم ہر ایک لائن کو اپنی مدت کے ساتھ پرنٹ کرتے ہیں، جیسا کہ `uv` کرتا ہے۔

<!-- router:modular -->
فائل پر مبنی روٹر پرامپٹ کا جواب `No`: `nx new` ماڈیولر راؤٹر کو `src/routes/` کے بجائے `src/apps/` میں ڈھال دیتا ہے۔
<!-- /router -->

<!-- router:custom -->
صفحات کے لیے فائل پر مبنی روٹر پرامپٹ کا جواب `Yes` دیں، پھر اپنے موجودہ `APIRouter` کو `nexyconfig.py` میں ماؤنٹ کریں: دونوں راؤٹرز ایک ساتھ رہتے ہیں۔
<!-- /router -->

## 2. ترتیب میں ترمیم کریں۔

<!-- router:fbr,custom -->
`src/routes/layout.nexy` HTML دستاویز کا مالک ہے (React کلائنٹ کی روٹنگ کے ساتھ یہ `layout.tsx` ہے)۔ تبدیل کریں `<title>`:

```nexy
<title>Notes</title>
```

محفوظ کریں: براؤزر دوبارہ لوڈ ہوتا ہے۔ دیکھیں [لے آؤٹس](../routing/fbr/layouts/README.md)۔
<!-- /router -->

<!-- router:modular -->
کنٹرولر منظر کے ارد گرد `src/apps/layout.nexy` رینڈر کرتا ہے، اور وہ فائل HTML دستاویز کی مالک ہے۔ تبدیل کریں `<title>`:

```nexy
<title>Notes</title>
```

محفوظ کریں: براؤزر دوبارہ لوڈ ہوتا ہے۔ دیکھیں [کنٹرولر سے آراء](../routing/modular/README.md#views-from-a-controller)۔
<!-- /router -->

## 3. ایک صفحہ شامل کریں۔

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

کھولیں <http://localhost:3000/notes>: آپ کو دو گولیاں نظر آنی چاہئیں۔ یہ `/notes` پر پیش کیا جاتا ہے۔ `---` کے درمیان کا حصہ Python ہے، باقی حصہ Jinja2 ہے۔
<!-- /router -->

<!-- router:modular -->
ایک کنٹرولر ایک منظر واپس کرتا ہے۔ بنائیں `src/apps/notes_view.nexy`:

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

روٹ کا اعلان `src/apps/app_controller.py` میں کریں اور کنٹرولر کو ماڈیول میں شامل کریں:

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

کھولیں <http://localhost:3000/notes>: آپ کو دو گولیاں نظر آنی چاہئیں۔ `---` کے درمیان کا حصہ Python ہے، باقی حصہ Jinja2 ہے۔
<!-- /router -->

## 4. ایک اختتامی نقطہ شامل کریں۔

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes.py"
async def GET():
    return [{"id": 1, "text": "Buy milk"}]
```

```bash
curl http://localhost:3000/api/notes
```

آپ کو `[{"id":1,"text":"Buy milk"}]` ملنا چاہئے۔ فنکشن کا نام HTTP طریقہ ہے۔ انٹرایکٹو API دستاویزات `/docs` پر ہیں۔
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/app_controller.py"
@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": 1, "text": "Buy milk"}]
```

`src/apps/app_module.py` میں `NotesApiController` کو `controllers` میں شامل کریں، پھر چلائیں:

```bash
curl http://localhost:3000/api/notes
```

آپ کو `[{"id":1,"text":"Buy milk"}]` ملنا چاہئے۔ طریقہ کا نام HTTP طریقہ ہے۔ انٹرایکٹو API دستاویزات `/docs` پر ہیں۔
<!-- /router -->

## 5. ڈیٹا کا اشتراک کریں۔

فہرست کو Python ماڈیول میں منتقل کریں اور اسے دونوں فائلوں میں استعمال کریں:

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

## 6. بنائیں اور پیش کریں۔

```bash
nx build
nx start
```

`nx build` ہر مرحلے کو اس کی مدت کے ساتھ پرنٹ کرتا ہے۔ `nx start` مرتب شدہ آؤٹ پٹ کو Uvicorn کے ساتھ پیش کرتا ہے: رن ٹائم پر نوڈ کا کوئی عمل نہیں۔

## جہاں اگلا

- [روٹنگ](../routing/README.md): متحرک طبقات اور گروپس
- [اعمال](../guides/actions.md): کسی فارم سے یا کلائنٹ سے Python کال کریں۔
- [ٹیسٹنگ](../guides/testing.md): جانچ کے صفحات اور اختتامی نکات
- [تعینات](../deployment/README.md): کنٹینرز اور ریورس پراکسی
