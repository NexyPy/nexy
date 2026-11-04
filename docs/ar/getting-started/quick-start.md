# بداية سريعة

ستقوم بإنشاء مشروع Nexy وتشغيله ورؤية تغيير الصفحة أثناء تحريره. يستغرق ثلاثة
دقائق. يضيف [البرنامج التعليمي](tutorial.md) بعد ذلك نقطة نهاية وبناء إنتاج.

## قبل أن تبدأ

| أنت بحاجة | لماذا |
|---|---|
| بايثون 3.12+ | `requires-python` في `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | يوفر `uvx` ويقوم بإنشاء المشروع وتثبيت حزمه |
| Node.js 18+ | فقط إذا كنت تستخدم إطار عمل العميل (React، Vue، Svelte، Solid، Preact) |

لا الأشعة فوق البنفسجية حتى الآن؟ انظر [التثبيت](installation.md).

## 1. إنشاء المشروع

```bash
uvx nexy new my-app
```

`uvx` يأتي مع الأشعة فوق البنفسجية، لذا قم بتثبيت الأشعة فوق البنفسجية أولاً. يقوم بتشغيل Nexy في بيئة مؤقتة، وهو ما يكفي **لإنشاء** المشروع. `nexy new` ثم يجعل
المشروع الخاص `.venv` وتثبيت حزمه هناك. أربعة مطالبات تقرر الأسلاك:

| موجه | مفعوله |
|---|---|
| جهاز توجيه يعتمد على الملف؟ | `Yes` مسح `src/routes/`؛ `No` يدعم جهاز التوجيه المعياري في `src/apps/` |
| نوع المشروع | `Web` يضيف تخطيطًا وأصول العميل، `API` يبدأ بدون مشاهدات |
| مكون العميل؟ | يضيف إطار العمل وإعداد Vite الخاص به |
| ORM / قاعدة البيانات | تضيف طبقة نموذج، أو لا شيء |

لست متأكدا؟ الإجابة `Yes`، `Web`، ولا يوجد مكون عميل. يمكنك إضافة كل في وقت لاحق.

## 2. تشغيله

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

فتح <http://localhost:3000>. يجب أن تشاهد صفحة البداية. ويأتي الميناء من `usePort`
(الافتراضي `3000`)؛ `--port` و `--host` يتجاوزانه في كل مرة.

> [!ملاحظة]
> تشغيل كل أمر باستثناء `new` و `init` داخل البيئة الافتراضية للمشروع، أو البادئة به
> ب`uv run`، كما في `uv run nexy dev`. وخارجها يفشل مشروع يحتاج إلى `sqlmodel` مع
> `No module named 'sqlmodel'`.

## 3. تغيير صفحة

<!-- router:fbr,custom -->
الملف الموجود تحت `src/routes/` هو مسار. إنشاء `src/routes/hello.nexy`:

```nexy filename="src/routes/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```
<!-- /router -->

<!-- router:modular -->
تقوم وحدة التحكم بإرجاع طريقة عرض. إنشاء `src/apps/hello_view.nexy`:

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

ثم أعلن عن الصفحة في `src/apps/app_controller.py` وأضفها إلى الوحدة:

```python filename="src/apps/app_controller.py"
@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/hello_view.nexy")})
```

```python filename="src/apps/app_module.py"
from .app_controller import AboutController, AppController, HelloController

controllers = [AppController, AboutController, HelloController]
```
<!-- /router -->

فتح <http://localhost:3000/hello>. غيّر `"Hello"` إلى `"Bonjour"` واحفظ: تحديثات الصفحة
بدون إعادة التحميل اليدوي. إذا كان الرمز خاطئًا، فسيعرض المتصفح الخطأ بدلاً من صفحة فارغة.

`prop[str]` يعلن عن خاصية مكتوبة. العلامة الموجودة أسفل المادة الأمامية هي Jinja2 - انظر
[ملفات .nexy](../views/nexy/README.md).

## إلى أين بعد ذلك

| تريد | القراءة |
|---|---|
| إضافة نقطة نهاية بايثون وشحن البنية | [البرنامج التعليمي](tutorial.md) |
| معرفة أين ينتمي كل ملف | [بنية المشروع](project-structure.md) |
| فهم من يبني ماذا | [كيف يعمل Nexy](how-nexy-works.md) |
| استخدم React أو Vue أو Svelte أو Solid أو Preact | [Views](../views/README.md) |