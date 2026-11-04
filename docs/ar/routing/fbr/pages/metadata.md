# البيانات التعريفية للصفحة

تقوم الصفحة بتسمية عنوانها وعلامات رأسها، ويقوم تخطيط الجذر بكتابتها مرة واحدة.

## قلها في الصفحة

بالنسبة للصفحة التي لا تتغير أبدًا، اكتب حرفيًا في أعلى المادة الأمامية:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

عندما يعتمد العنوان على البيانات، اتصل بـ `setMetadata` بدلاً من ذلك:

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound, setMetadata

from src.posts import find

slug: prop[str]
post = find(slug) or notFound()
setMetadata(title=post.title, description=post.summary, og={"image": post.cover})
---
<h1>{{ post.title }}</h1>
```

تستدعي وحدة التحكم المعيارية `setMetadata(...)` قبل أن تُرجع `useViews(...)`.

## اكتبها في التخطيط

يمتلك التخطيط الجذر `<head>`. سطر واحد يكتب ما قالته الصفحة، هرب:

```nexy filename="src/routes/layout.nexy"
---
from nexy import setMetadata, useMetadata

children: prop[NexyElement]
setMetadata(title_template="%s | My site")
---
<!DOCTYPE html>
<html>
  <head>
    {{ useMetadata().html() }}
  </head>
  <body>{{ children }}</body>
</html>
```

يتم تشغيل الصفحة قبل تخطيطاتها، بحيث يعثر التخطيط على ما طلبته الصفحة. صفحة تقول
لا شيء يحصل على `useTitle` من `nexyconfig.py` الخاص بك، ولا توجد علامة أخرى.

## الحقول

| الحقل | مكتوب كـ |
|---|---|
| `title` | `<title>`؛ مع `title_template="%s \| My site"` يتم وضع العنوان في `%s` |
| `description` | `<meta name="description">` |
| `canonical` | `<link rel="canonical">` |
| `robots` | `<meta name="robots">` مثلا `"noindex"` |
| `icon` | `<link rel="icon">` |
| `og` | واحد `<meta property="og:...">` لكل مفتاح: `{"image": "/cover.png"}` يعطي `og:image` |
| `twitter` | واحد `<meta name="twitter:...">` لكل مفتاح |
| `extra` | قائمة إملاءات السمات، واحد `<meta>` لكل منهما: `[{"name": "theme-color", "content": "#fff"}]` |

مكالمة لاحقة تستبدل القيمة؛ `og` و`twitter` و`extra` إضافة إلى ما هو موجود. المجال الذي يفعل
غير موجود يرفع `TypeError`، لذا فإن الخطأ المطبعي لا يفعل شيئًا بصمت.

## آمن افتراضيًا

يتم تخطي كل قيمة من خلال HTML، لذلك لا يمكن للعنوان الذي تم إنشاؤه من عنوان URL أو من قاعدة البيانات إغلاق العلامة
وحقن البرنامج النصي. يتم هروب القيمة مرة واحدة، عندما يستدعي التخطيط `html()`: لا تهرب منها
نفسك.

## الخطوات التالية

- [الصفحات](README.md)
- [التخطيطات](../layouts/README.md)
- [صفحات الخطأ](../errors/README.md)