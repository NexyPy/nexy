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

```text
src/routes/
├─ index.nexy           /
├─ about.nexy           /about
├─ (marketing)/
│  └─ pricing.nexy      /pricing
├─ blog/
│  ├─ index.md          /blog
│  └─ [slug].nexy       /blog/{slug}
├─ docs/
│  └─ [...path].nexy    /docs/{path:path}
└─ api/
   └─ users.py          GET /api/users, POST /api/users
```

```python filename="src/routes/api/users.py"
async def GET():
    return {"users": []}


async def POST():
    return {"created": True}
```

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

ملفي الجدول Python جنبًا إلى جنب في مجلد واحد:

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

```python filename="src/routes/admin/dependeency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

وصفحة تجيب على 404 من مجلدها:

```nexy filename="src/routes/notfound.nexy"
<h1>Page not found</h1>
<p><a href="/">Back home</a></p>
```

## الملفات التي تم تجاهلها

- ملف أو مجلد يبدأ بـ `_` أو `.`: استخدمه للأجزاء والمسودات والمساعدين.
- ملف لا يكون امتداده نشطًا للمشروع: يتم تخطيه مع تحذير.

```text
src/routes/
├─ index.nexy           /
├─ _card.nexy           ignored: a partial the pages include
├─ _helpers/            ignored, with everything inside
│  └─ format.py
└─ .draft.nexy          ignored: a draft
```

## ملف واحد لكل عنوان URL

يتم تسجيل ملفين يتم تحليلهما إلى نفس عنوان URL. ولا تضع `blog.nexy` بجانب `blog/index.nexy`.

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: keep only one of the two
```

## خارج `src/routes/`

| مجلد | الغرض |
|---|---|
| `src/components/` | المكونات المستوردة عن طريق الصفحات؛ الطرق أبدا |
| `src/apps/` | وحدات التحكم والوحدات النمطية لـ [modular جهاز التوجيه](../routing/modular/README.md) |
| `public/` | الملفات الثابتة، التي يتم تقديمها في الجذر: `public/logo.svg` هو `/logo.svg` (أيضًا ضمن `/public/`) |
| `__nexy__/` | الناتج المتولد؛ لا ترتكب |

```text
my-app/
├─ nexyconfig.py
├─ public/
│  └─ logo.svg          /logo.svg
├─ src/
│  ├─ routes/           the routes
│  ├─ components/
│  │  └─ Counter.tsx    imported by pages, never served on its own
│  └─ apps/             the modular router, when you use it
└─ __nexy__/            generated: add it to .gitignore
```

## الخطوات التالية

- [التوجيه](../routing/README.md)
- [هيكل المشروع](../getting-started/project-structure.md)
