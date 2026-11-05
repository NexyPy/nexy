# طرق ديناميكية

يتطابق مقطع المسار المكتوب بين قوسين مربعين مع أي قيمة ويسلمها إلى الصفحة أو المعالج.

## القطاعات الديناميكية

`blog/[slug].nexy` يخدم `/blog/{slug}`. في الصفحة، قم بتعريف المقطع كخاصية؛ في معالج Python، اعتبره وسيطة.

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

## المقاطع المكتوبة

الشرح يحدد النوع.

| حيث | التحويل |
|---|---|
| `.py` معالج | أي نوع FastAPI تعليق توضيحي (`int`، `UUID`، `Enum`...) |
| يتم تحويل `.nexy` صفحة | `int` و `float`؛ كل شيء آخر يبقى سلسلة |

القيمة التي لا تتطابق مع التعليق التوضيحي هي **لم يتم العثور عليها**: `/api/users/abc` تجيب على `404`، لأن المسار الديناميكي يلتقط أي عنوان URL وعنوان URL الذي لا يمكن تحويله ببساطة غير موجود. انظر [التحقق والأخطاء](../handlers/validation-and-errors.md).

## قطاعات شاملة

`docs/[...path].nexy` يخدم `/docs/{path:path}`. تصل الأجزاء المتبقية كسلسلة واحدة، بما في ذلك الخطوط المائلة.

```nexy filename="src/routes/docs/[...path].nexy"
---
path: prop[str]
---
<pre>{{ path }}</pre>
```

`/docs/a/b/c` يعطي `path == "a/b/c"`.

## مجموعات الطريق

يقوم الدليل الموجود بين قوسين بتنظيم الملفات دون الظهور في عنوان URL. ولا يزال يشارك في [الميراث](../inheritance.md): ينطبق `layout.*` و `dependencies.py` على ما في داخله.

```text
src/routes/
├─ (marketing)/
│  ├─ layout.nexy        applies to the pages in the group
│  ├─ pricing.nexy       /pricing
│  └─ about.nexy         /about
└─ (app)/
   └─ dashboard.nexy     /dashboard
```

استخدم المجموعات لمنح الأقسام المختلفة تخطيطات مختلفة دون تغيير عناوين URL الخاصة بها.

## الأولوية

تتفوق المسارات الثابتة على المسارات الديناميكية، والمسارات الديناميكية على رسائل الصيد الشاملة: `/blog/new` تتطابق مع `blog/new.nexy` قبل `blog/[slug].nexy`.

## ملف واحد لكل عنوان URL

يتم تسجيل ملفين يتم تحليلهما إلى نفس عنوان URL. لا تضع `blog.nexy` بجانب `blog/index.nexy`، ​​أو تخلط `index.nexy` و `index.py` لنفس المسار.

## الخطوات التالية

- [الصفحات](README.md)
- [صفحات الخطأ](../errors/README.md)
- [اصطلاحات الملف](../../../reference/file-conventions.md)
