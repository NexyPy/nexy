# اصطلاحات الملف

الأسماء والقواعد المحجوزة تحت `src/routes/`.

## ملفات التوجيه

| الملف | يصبح |
|---|---|
| `index.nexy`، `index.md`، `index.mdx`، `index.py` | مسار دليله |
| `about.nexy` | `/about` |
| `[slug].nexy` | الجزء الديناميكي `{slug}` |
| `[...path].nexy` | جامع `{path:path}` |
| `(group)/page.nexy` | `/page`: المجموعة لا تظهر في عنوان URL |
| `name.py` | معالج واجهة برمجة التطبيقات؛ أسماء الوظائف `GET`، `POST`، ... هي الطرق |
| `name.tsx`، `.jsx`، `.vue`، `.svelte` | مسار العميل عند تمكين إطار العمل مع `useFF` |

## الملفات المحجوزة

| الملف | الدور | التفاصيل |
|---|---|---|
| `layout.nexy` | وضع الخادم: يغلف كل صفحة أسفله؛ يمتلك الجذر مستند HTML | [layout.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | وضع العميل (React): يمتلك الجذر مستند HTML، أما تلك المتداخلة فتغلف الصفحات | [layout.tsx](../views/react/differences.md) |
| `layout.vue`، `layout.svelte` | وضع العميل: تخطيطات متداخلة | [layout.vue](../views/vue/differences.md)، [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | 404 صفحة لدليلها | [صفحات الخطأ](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 صفحة لدليلها | [صفحات الخطأ](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | 403 صفحة لدليله | [صفحات الخطأ في كل مجلد](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | 401 صفحة لدليلها | [صفحات خطأ في كل مجلد](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | محفوظة؛ لا يوجد تأثير لوقت التشغيل حتى الآن | [صفحات الخطأ](../routing/fbr/errors/README.md) |
| `middleware.py` | و`async def middleware(request, call_next)` تغليف طلبات الدليل وأدناه | [ملفات البرامج الوسيطة](../routing/fbr/middleware/README.md) |
| `dependencies.py` | قائمة `dependencies = [fn, ...]` مطبقة على الدليل وأبناءه | [التبعيات](../routing/fbr/dependencies/README.md) |
| `__init__.py` | علامة حزمة بايثون | |
| `favicon.ico` | خدم في `/favicon.ico` | |

`useLayoutExtensions`، `useNotFoundExtensions`، `useErrorsExtensions`، `useForbiddenExtensions`،
`useUnauthorizedExtensions` و `useLoadingExtensions` يحجزون المزيد من الامتدادات لهذه الأسماء. انظر
[التكوين](config.md).

## الملفات التي تم تجاهلها

- ملف أو مجلد يبدأ بـ `_` أو `.`: استخدمه للأجزاء والمسودات والمساعدين.
- ملف لا يكون امتداده نشطًا للمشروع: يتم تخطيه مع تحذير.

## ملف واحد لكل عنوان URL

يتم تسجيل ملفين يتم تحليلهما إلى نفس عنوان URL. ولا تضع `blog.nexy` بجانبه
`blog/index.nexy`.

## خارج `src/routes/`

| المجلد | الغرض |
|---|---|
| `src/components/` | المكونات المستوردة بالصفحات؛ أبدا الطرق |
| `src/apps/` | وحدات التحكم والوحدات النمطية لجهاز التوجيه المعياري](../routing/modular/README.md) |
| `public/` | ملفات ثابتة، يتم تقديمها في الجذر: `public/logo.svg` هو `/logo.svg` (أيضًا ضمن `/public/`) |
| `__nexy__/` | المخرجات المولدة؛ لا ترتكب |

## الخطوات التالية

-  [التوجيه](../routing/README.md)
- [هيكل المشروع](../getting-started/project-structure.md)