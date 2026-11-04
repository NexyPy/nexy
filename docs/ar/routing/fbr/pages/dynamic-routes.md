# الطرق الديناميكية

يتطابق مقطع المسار المكتوب بين قوسين مربعين مع أي قيمة ويسلمها إلى الصفحة أو المعالج.

## القطاعات الديناميكية

`blog/[slug].nexy` يخدم `/blog/{slug}`. في الصفحة، قم بتعريف المقطع كخاصية؛ في بايثون
المعالج، اعتبره حجة.

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

## الأجزاء المكتوبة

الشرح يحدد النوع.

| حيث | التحويل |
|---|---|
| `.py` معالج | أي تعليق توضيحي من نوع FastAPI (`int`، `UUID`، `Enum`...) |
يتم تحويل | `.nexy` صفحة | `int` و `float`؛ كل شيء آخر يبقى سلسلة |

القيمة التي لا تتطابق مع التعليق التوضيحي هي **لم يتم العثور عليها**: `/api/users/abc` الإجابات `404`، لأن
يلتقط المسار الديناميكي أي عنوان URL وعنوان URL الذي لا يمكن تحويله ببساطة غير موجود. انظر
[التصديق والأخطاء](../handlers/validation-and-errors.md).

## أجزاء شاملة

`docs/[...path].nexy` يخدم `/docs/{path:path}`. الأجزاء المتبقية تصل كسلسلة واحدة،
مائلة المدرجة.

```nexy filename="src/routes/docs/[...path].nexy"
---
path: prop[str]
---
<pre>{{ path }}</pre>
```

`/docs/a/b/c` يعطي `path == "a/b/c"`.

## مجموعات الطريق

يقوم الدليل الموجود بين قوسين بتنظيم الملفات دون الظهور في عنوان URL. ولا يزال يشارك فيها
[[الميراث](../inheritance.md)]: ينطبق `layout.*` و `dependencies.py` على ما في داخله.

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

تتفوق المسارات الثابتة على المسارات الديناميكية، والمسارات الديناميكية على طرق التقاط الكل:
`/blog/new` يطابق `blog/new.nexy` قبل `blog/[slug].nexy`.

## ملف واحد لكل عنوان URL

يتم تسجيل ملفين يتم تحليلهما إلى نفس عنوان URL. لا تضع `blog.nexy` بجانب
`blog/index.nexy`، أو مزج `index.nexy` و `index.py` لنفس المسار.

## الخطوات التالية

- [الصفحات](README.md)
- [صفحات الخطأ](../errors/README.md)
- [اصطلاحات الملف](../../../reference/file-conventions.md)