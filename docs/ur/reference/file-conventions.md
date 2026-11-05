# فائل کنونشنز

`src/routes/` کے تحت مخصوص نام اور قواعد۔

## فائلوں کو روٹ کریں۔

| فائل | بن جاتی ہے |
|---|---|
| `index.nexy`، `index.md`، `index.mdx`، `index.py` | اس کی ڈائرکٹری کا روٹ |
| `about.nexy` | `/about` |
| `[slug].nexy` | متحرک طبقہ `{slug}` |
| `[...path].nexy` | کیچ آل `{path:path}` |
| `(group)/page.nexy` | `/page`: گروپ URL میں ظاہر نہیں ہوتا |
| `name.py` | API ہینڈلر؛ فنکشن کے نام `GET`، `POST`، ... طریقے ہیں |
| `name.tsx`، `.jsx`، `.vue`، `.svelte` | کلائنٹ کا راستہ جب فریم ورک `useFF` | کے ساتھ فعال ہوتا ہے۔

## محفوظ فائلیں۔

| فائل | کردار | تفصیلات |
|---|---|---|
| `layout.nexy` | سرور موڈ: اس کے نیچے ہر صفحے کو لپیٹتا ہے۔ جڑ HTML دستاویز کا مالک ہے | [layout.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | کلائنٹ موڈ (React): جڑ HTML دستاویز کا مالک ہے، نیسٹڈ والے صفحات کو لپیٹتے ہیں | [layout.tsx](../views/react/differences.md) |
| `layout.vue`، `layout.svelte` | کلائنٹ موڈ: نیسٹڈ لے آؤٹ | [layout.vue](../views/vue/differences.md)، [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | اس کی ڈائرکٹری کے لیے 404 صفحہ | [خرابی صفحات](../routing/fbr/errors/README.md) |
| `errors.nexy` | اس کی ڈائرکٹری کے لیے 500 صفحہ | [خرابی صفحات](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | اس کی ڈائرکٹری کے لیے 403 صفحہ | [خرابی صفحات فی فولڈر](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | اس کی ڈائرکٹری کے لیے 401 صفحہ | [خرابی صفحات فی فولڈر](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | محفوظ؛ ابھی تک کوئی رن ٹائم اثر نہیں ہے | [خرابی صفحات](../routing/fbr/errors/README.md) |
| `middleware.py` | ایک `async def middleware(request, call_next)` ڈائریکٹری کی درخواستوں کو لپیٹنا اور نیچے | [مڈل ویئر فائلیں](../routing/fbr/middleware/README.md) |
| `dependencies.py` | ڈائریکٹری اور اس کے بچوں | [انحصارات](../routing/fbr/dependencies/README.md) | پر لاگو ایک `dependencies = [fn, ...]` فہرست
| `__init__.py` | Python پیکیج مارکر | |
| `favicon.ico` | `/favicon.ico` | | میں خدمات انجام دیں۔

`useLayoutExtensions`، `useNotFoundExtensions`، `useErrorsExtensions`، `useForbiddenExtensions`، `useUnauthorizedExtensions` اور `useLoadingExtensions` ان ناموں کے لیے مزید توسیعات محفوظ کرتے ہیں۔ دیکھیں [تشکیل](config.md)۔

## نظر انداز فائلیں۔

- `_` یا `.` سے شروع ہونے والی فائل یا فولڈر: اسے جزوی، ڈرافٹ اور مددگار کے لیے استعمال کریں۔
- ایک فائل جس کی توسیع پروجیکٹ کے لیے فعال نہیں ہے: اسے ایک انتباہ کے ساتھ چھوڑ دیا گیا ہے۔

## ایک فائل فی URL

دو فائلیں جو ایک ہی URL کو حل کرتی ہیں دونوں رجسٹر ہوتی ہیں۔ `blog.nexy` کو `blog/index.nexy` کے آگے مت لگائیں۔

## باہر `src/routes/`

| فولڈر | مقصد |
|---|---|
| `src/components/` | صفحات کے ذریعے درآمد شدہ اجزاء کبھی راستے نہیں |
| `src/apps/` | [ماڈیولر روٹر](../routing/modular/README.md) کے کنٹرولرز اور ماڈیولز |
| `public/` | جامد فائلیں، جڑ میں پیش کی جاتی ہیں: `public/logo.svg` ہے `/logo.svg` (بھی `/public/`] کے تحت) |
| `__nexy__/` | پیدا شدہ پیداوار؛ ارتکاب نہ کریں |

## اگلے اقدامات

- [روٹنگ](../routing/README.md)
- [پروجیکٹ ڈھانچہ](../getting-started/project-structure.md)
