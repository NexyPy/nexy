# التوجيه القائم على الملف

الطريق هو ملف. عنوان URL هو مسار الملف بالنسبة إلى `src/routes/`، بدون الامتداد.

## ملف إلى URL

| ملف | عنوان URL |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` يعين إلى دليله، وليس إلى `/index`. الدليل الموجود بين قوسين هو **مجموعة**: ينظم الملفات دون الظهور في عنوان URL.

في وضع العميل تكون ملفات الصفحة هي `.tsx` أو `.vue` أو `.svelte` بدلاً من `.nexy`؛ قواعد URL هي نفسها.

ملفان من هذا الجدول: صفحة تقرأ الجزء الخاص بها، ومعالج يجيب على JSON.

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/routes/api/users.py"
async def GET():
    return {"users": []}
```

## وضعين

`useCSR` يقرر ما هي الصفحات. لا يمكن الجمع بين الاثنين في مشروع واحد: يرفض Nexy البدء عندما تكون صفحة الخادم بجوار مسار العميل.

| الوضع | الصفحات | تخطيط الجذر | انظر |
|---|---|---|---|
| الخادم (`useCSR = False`) | `.nexy`، `.md`، `.mdx` | `layout.nexy` | [وضع الخادم ووضع العميل](modes.md) |
| العميل (`useCSR = True`) | ملفات الإطار | `layout.tsx` | [تخطيط.tsx](../../views/react/differences.md) |

`.py` الملفات هي معالجات API في كلا الوضعين.

التبديل عبارة عن سطر واحد من `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True  # client mode: src/routes/*.tsx are the pages
```

## ما ليس الطريق

- أسماء الملفات المحجوزة: `layout.*`، `loading.nexy`، `errors.nexy`، `notfound.nexy`، `dependencies.py`، `middleware.py`، `__init__.py`.
- الملفات والمجلدات التي تبدأ بـ `_` أو `.`: استخدمها للأجزاء والمسودات.
- الإضافات غير النشطة لمشروعك. يتم تخطي الملف الذي يكون امتداده غير نشط مع تحذير.

```text
src/routes/
├─ layout.nexy          wraps the pages, not a route
├─ middleware.py        wraps the requests, not a route
├─ index.nexy           /
├─ _card.nexy           a partial: no URL
└─ .draft.nexy          a draft: no URL
```

## ملف واحد لكل عنوان URL

يتم تسجيل ملفين يتم تحليلهما إلى نفس عنوان URL. لا تنشئ `blog.nexy` بجوار `blog/index.nexy`، ولا تخلط `index.nexy` و `index.py` لنفس المسار. اختر واحدة.

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: delete one of the two
```

## في هذا القسم

| مجلد | ما يغطيه |
|---|---|
| [الصفحات/](pages/README.md) | الصفحات، [المسارات الديناميكية](pages/dynamic-routes.md)، مجموعات المسار |
| [التخطيطات/](layouts/README.md) | صفحة واحدة لكل نوع ملف تخطيط |
| [المعالجات/](handlers/README.md) | `.py` المعالجات والتحقق والأخطاء |
| [التبعيات/](dependencies/README.md) | `dependencies.py`، حراس |
| [الوسيطة/](middleware/README.md) | `middleware.py` |
| [الأخطاء/](errors/README.md) | لم يتم العثور على وصفحات الخطأ |
| [الملاحة/](navigation/linking-and-navigating.md) | الروابط والسنانير |
| [الوقت الحقيقي/](realtime/websocket.md) | WebSocket |
| [الميراث](inheritance.md) | قواعد الميراث في جدول واحد |

## الخطوات التالية

- [وضع الخادم ووضع العميل](modes.md)
- [التخطيطات](layouts/README.md)
- [التوجيه المعياري](../modular/README.md)
