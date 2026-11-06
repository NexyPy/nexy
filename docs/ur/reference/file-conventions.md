# فائل کنونشنز

`src/routes/` کے تحت مخصوص نام اور قواعد۔

## فائلوں کو روٹ کریں۔

| فائل | بن جاتا ہے۔ |
|---|---|
| `index.nexy`، `index.md`، `index.mdx`، `index.py` | اس کی ڈائرکٹری کا راستہ |
| `about.nexy` | `/about` |
| `[slug].nexy` | متحرک طبقہ `{slug}` |
| `[...path].nexy` | تمام کو پکڑنا `{path:path}` |
| `(group)/page.nexy` | `/page`: گروپ URL میں ظاہر نہیں ہوتا |
| `name.py` | API ہینڈلر؛ فنکشن کے نام `GET`، `POST`، ... طریقے ہیں۔ |
| `name.tsx`، `.jsx`، `.vue`، `.svelte` | کلائنٹ کا راستہ جب فریم ورک کو `useFF` کے ساتھ فعال کیا جاتا ہے |

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

## محفوظ فائلیں۔

| فائل | کردار | تفصیلات |
|---|---|---|
| `layout.nexy` | سرور موڈ: ہر صفحے کو اس کے نیچے لپیٹ دیتا ہے۔ جڑ HTML دستاویز کا مالک ہے۔ | [layout.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | کلائنٹ موڈ (React): جڑ HTML دستاویز کا مالک ہے، نیسٹڈ والے صفحات لپیٹتے ہیں | [layout.tsx](../views/react/differences.md) |
| `layout.vue`، `layout.svelte` | کلائنٹ موڈ: نیسٹڈ لے آؤٹ | [layout.vue](../views/vue/differences.md)، [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | اس کی ڈائرکٹری کے لیے 404 صفحہ | [خرابی کے صفحات](../routing/fbr/errors/README.md) |
| `errors.nexy` | اس کی ڈائرکٹری کے لیے 500 صفحہ | [خرابی کے صفحات](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | اس کی ڈائرکٹری کے لیے 403 صفحہ | [خامی صفحات فی فولڈر](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | اس کی ڈائرکٹری کے لیے 401 صفحہ | [خامی صفحات فی فولڈر](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | محفوظ ابھی تک کوئی رن ٹائم اثر نہیں ہے۔ | [خرابی صفحات](../routing/fbr/errors/README.md) |
| `middleware.py` | ایک `async def middleware(request, call_next)` ڈائریکٹری اور نیچے کی درخواستوں کو لپیٹنا | [مڈل ویئر فائلیں](../routing/fbr/middleware/README.md) |
| `dependencies.py` | ڈائرکٹری اور اس کے بچوں پر لاگو ایک `dependencies = [fn, ...]` فہرست | [انحصار](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python پیکیج مارکر | |
| `favicon.ico` | میں خدمت کی `/favicon.ico` | |

`useLayoutExtensions`، `useNotFoundExtensions`، `useErrorsExtensions`، `useForbiddenExtensions`، `useUnauthorizedExtensions` اور `useLoadingExtensions` ان ناموں کے لیے مزید توسیعات محفوظ کرتے ہیں۔ دیکھیں [تشکیل](config.md)۔

ٹیبل کی دو Python فائلیں، ایک فولڈر میں ساتھ ساتھ:

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

اور ایک صفحہ جو اس کے فولڈر کے 404 کا جواب دیتا ہے:

```nexy filename="src/routes/notfound.nexy"
<h1>Page not found</h1>
<p><a href="/">Back home</a></p>
```

## نظر انداز فائلیں۔

- `_` یا `.` سے شروع ہونے والی فائل یا فولڈر: اسے جزوی، ڈرافٹ اور مددگار کے لیے استعمال کریں۔
- ایک فائل جس کی توسیع پروجیکٹ کے لیے فعال نہیں ہے: اسے ایک انتباہ کے ساتھ چھوڑ دیا گیا ہے۔

```text
src/routes/
├─ index.nexy           /
├─ _card.nexy           ignored: a partial the pages include
├─ _helpers/            ignored, with everything inside
│  └─ format.py
└─ .draft.nexy          ignored: a draft
```

## ایک فائل فی URL

دو فائلیں جو ایک ہی URL کو حل کرتی ہیں دونوں رجسٹر ہوتی ہیں۔ `blog/index.nexy` کے آگے `blog.nexy` نہ لگائیں۔

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: keep only one of the two
```

## باہر `src/routes/`

| فولڈر | مقصد |
|---|---|
| `src/components/` | صفحات کے ذریعے درآمد کردہ اجزاء؛ کبھی راستے نہیں |
| `src/apps/` | [ماڈیولر روٹر](../routing/modular/README.md) کے کنٹرولرز اور ماڈیولز |
| `public/` | جامد فائلیں، جڑ میں پیش کی جاتی ہیں: `public/logo.svg` ہے `/logo.svg` (`/public/`] کے تحت بھی) |
| `__nexy__/` | پیدا شدہ پیداوار؛ ارتکاب نہ کرو |

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

## اگلے اقدامات

- [روٹنگ](../routing/README.md)
- [پروجیکٹ ساخت](../getting-started/project-structure.md)
