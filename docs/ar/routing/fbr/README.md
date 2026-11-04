# التوجيه القائم على الملف

الطريق هو ملف. عنوان URL هو مسار الملف بالنسبة إلى `src/routes/`، بدون الامتداد.

## ملف إلى URL

| الملف | عنوان URL |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` يعين إلى دليله، وليس إلى `/index`. الدليل الموجود بين قوسين هو **مجموعة**: it
ينظم الملفات دون الظهور في عنوان URL.

في وضع العميل تكون ملفات الصفحة هي `.tsx` أو `.vue` أو `.svelte` بدلاً من `.nexy`؛ قواعد URL هي
نفس الشيء.

## وضعين

`useCSR` يقرر ما هي الصفحات. لا يمكن الجمع بين الاثنين في مشروع واحد: Nexy يرفض البدء
عندما تكون صفحة الخادم بجوار مسار العميل.

| الوضع | الصفحات | تخطيط الجذر | انظر |
|---|---|---|---|
| الخادم (`useCSR = False`) | `.nexy`، `.md`، `.mdx` | `layout.nexy` | [وضع الخادم ووضع العميل](modes.md) |
| ملفات إطار العميل (`useCSR = True`) | | `layout.tsx` | [layout.tsx](../../views/react/differences.md) |

`.py` الملفات هي معالجات API في كلا الوضعين.

## ما ليس طريقا

- أسماء الملفات المحجوزة: `layout.*`، `loading.nexy`، `errors.nexy`، `notfound.nexy`،
  `dependencies.py`، `middleware.py`، `__init__.py`.
- الملفات والمجلدات التي تبدأ بـ `_` أو `.`: استخدمها للأجزاء والمسودات.
- الامتدادات غير النشطة لمشروعك. يتم تخطي الملف الذي يكون امتداده غير نشط
  تحذير.

## ملف واحد لكل عنوان URL

يتم تسجيل ملفين يتم تحليلهما إلى نفس عنوان URL. لا تنشئ `blog.nexy` بجوار
`blog/index.nexy`، ولا تخلط `index.nexy` و`index.py` في نفس المسار. اختر واحدة.

## في هذا الباب

| المجلد | ما يشمله |
|---|---|
| [الصفحات/](pages/README.md) | الصفحات، [المسارات الديناميكية](pages/dynamic-routes.md)، مجموعات المسار |
| [التخطيطات/](layouts/README.md) | صفحة واحدة لكل نوع ملف تخطيط |
| [المعالجات/](handlers/README.md) | `.py` المعالجات والتحقق من الصحة والأخطاء |
| [التبعيات/](dependencies/README.md) | `dependencies.py`، الحراس |
| [الوسيطة/](middleware/README.md) | `middleware.py` |
| [أخطاء/](errors/README.md) | صفحات غير موجودة وصفحات خطأ |
| [الملاحة/](navigation/linking-and-navigating.md) | الروابط، الخطافات |
| [الوقت الحقيقي/](realtime/websocket.md) | WebSocket |
| [الميراث](inheritance.md) | أحكام الميراث في جدول واحد |

## الخطوات التالية

-  [وضع الخادم ووضع العميل](modes.md)
- [التخطيطات](layouts/README.md)
-  [التوجيه المعياري](../modular/README.md)