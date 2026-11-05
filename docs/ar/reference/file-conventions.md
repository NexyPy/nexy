# اتفاقيات الملف

الأسماء والقواعد المحجوزة تحت `src/routes/`.

## ملفات الطريق

| ملف | يصبح |
|---|---|
| `index.nexy`، `index.md`، `index.mdx`، `index.py` | مسار الدليل الخاص به |
| `about.nexy` | `/about` |
| `[slug].nexy` | الجزء الديناميكي `{slug}` |
| `[...path].nexy` | الشامل `{path:path}` |
| `(group)/page.nexy` | `/page`: المجموعة لا تظهر في URL |
| `name.py` | معالج واجهة برمجة التطبيقات؛ أسماء الوظائف `GET`، `POST`، ... هي الطرق |
| `name.tsx`، `.jsx`، `.vue`، `.svelte` | مسار العميل عند تمكين إطار العمل باستخدام `useFF` |

## الملفات المحجوزة

| ملف | الدور | التفاصيل |
|---|---|---|
| `layout.nexy` | وضع الخادم: يغلف كل صفحة تحتها؛ يمتلك الجذر مستند HTML | [تخطيط.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | وضع العميل (React): يمتلك الجذر مستند HTML، ويمتلك الصفحات المتداخلة | [تخطيط.tsx](../views/react/differences.md) |
| `layout.vue`، `layout.svelte` | وضع العميل: تخطيطات متداخلة | [Layout.vue](../views/vue/differences.md), [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | 404 صفحة لدليلها | [صفحات الخطأ](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 صفحة لدليلها | [صفحات الخطأ](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | 403 صفحة لدليلها | [صفحات الخطأ لكل مجلد](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | 401 صفحة لدليلها | [صفحات الخطأ لكل مجلد](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | محفوظة؛ لا يوجد تأثير وقت التشغيل حتى الآن | [صفحات الخطأ](../routing/fbr/errors/README.md) |
| `middleware.py` | `async def middleware(request, call_next)` تغليف طلبات الدليل وأدناه | [ملفات الوسيطة](../routing/fbr/middleware/README.md) |
| `dependencies.py` | قائمة `dependencies = [fn, ...]` مطبقة على الدليل وأبناءه | [التبعيات](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python علامة الحزمة | |
| `favicon.ico` | خدم في `/favicon.ico` | |

`useLayoutExtensions`، `useNotFoundExtensions`، `useErrorsExtensions`، `useForbiddenExtensions`، `useUnauthorizedExtensions` و `useLoadingExtensions` يحجزون المزيد من الامتدادات لهذه الأسماء. انظر [التكوين](config.md).

## الملفات التي تم تجاهلها

- ملف أو مجلد يبدأ بـ `_` أو `.`: استخدمه للأجزاء والمسودات والمساعدين.
- ملف لا يكون امتداده نشطًا للمشروع: يتم تخطيه مع تحذير.

## ملف واحد لكل عنوان URL

يتم تسجيل ملفين يتم تحليلهما إلى نفس عنوان URL. ولا تضع `blog.nexy` بجانب `blog/index.nexy`.

## خارج `src/routes/`

| مجلد | الغرض |
|---|---|
| `src/components/` | المكونات المستوردة عن طريق الصفحات؛ الطرق أبدا |
| `src/apps/` | وحدات التحكم والوحدات النمطية لـ [modular جهاز التوجيه](../routing/modular/README.md) |
| `public/` | الملفات الثابتة، التي يتم تقديمها في الجذر: `public/logo.svg` هو `/logo.svg` (أيضًا ضمن `/public/`) |
| `__nexy__/` | الناتج المتولد؛ لا ترتكب |

## الخطوات التالية

- [التوجيه](../routing/README.md)
- [هيكل المشروع](../getting-started/project-structure.md)
