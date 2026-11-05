# سرور موڈ اور کلائنٹ موڈ

ایک Nexy پروجیکٹ یا تو **سرور سے رینڈرڈ** یا **کلائنٹ کے ذریعے روٹڈ** ہوتا ہے، جیسے Next.js پروجیکٹ یا تو سرور پر پیش کیے گئے صفحات ہیں یا کلائنٹ ایپ۔ `useCSR` میں `nexyconfig.py` کا انتخاب کرتا ہے۔

## سرور موڈ (`useCSR = False`)

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

- صفحات `.nexy`، `.md` یا `.mdx` فائلیں `src/routes/` کے تحت ہیں۔
- جڑ `layout.nexy` کا مالک ہے `<!DOCTYPE html>`، `<html>`، `<head>` اور `<body>`۔
- کلائنٹ کے اجزاء (React، Vue، Svelte، Solid یا Preact) کو **جزیروں** کے طور پر اجازت ہے: آپ ایک `.nexy` صفحہ سے درآمد کرتے ہیں اور یہ براؤزر میں ہائیڈریٹ ہوتا ہے۔ دیکھیں [جزیرے](../../rendering/islands.md)۔
- کلائنٹ کا جزو کبھی بھی راستہ نہیں ہوتا ہے۔ انہیں `src/components/` میں رکھیں۔
- ایک وقت میں ایک کلائنٹ فریم ورک۔

```text
src/
├─ routes/
│  ├─ layout.nexy         document
│  ├─ index.nexy          page
│  └─ api/users.py        API handler
└─ components/Counter.tsx island
```

## کلائنٹ موڈ (`useCSR = True`)

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

- صفحات آپ کے کلائنٹ فریم ورک کی فائلیں ہیں: `.tsx` React، `.vue`، `.svelte` کے لیے۔
- `.md` اور `.mdx` فائلیں درست روٹس رہتی ہیں: Nexy انہیں کلائنٹ لے آؤٹ کے اندر سرور پر پیش کرتا ہے، اور کلائنٹ راؤٹر وہاں سے نیویگیشن سنبھال لیتا ہے۔
- کسی بھی فریم ورک کا روٹ لے آؤٹ (`layout.tsx`، ​​`layout.vue`، `layout.svelte`) `<!DOCTYPE html>`، `<html>`، `<head>` اور `<body>` کا مالک ہوتا ہے، جیسا کہ Next.js ایپ راؤٹر کی روٹ لے آؤٹ۔ Nexy اسے پہلے جواب کے لیے نوڈ میں پیش کرتا ہے اور فریم ورک پوری دستاویز کو ہائیڈریٹ کرتا ہے۔ دیکھیں [layout.tsx](../../views/react/differences.md)۔
- `.py` فائلیں API ہینڈلر ہیں جو کلائنٹ کے راستوں کے ساتھ FastAPI کے ذریعہ پیش کی جاتی ہیں۔
- کوئی `.nexy` فائل بالکل نہیں ہے، اور کوئی `layout.nexy` نہیں۔
- صفحات کے درمیان نیویگیشن براؤزر میں ہوتا ہے۔

```text
src/routes/
├─ layout.tsx             document
├─ index.tsx              page
├─ users.tsx              page
└─ api/users.py           API handler
```

## جو رد کیا جاتا ہے۔

Nexy پروجیکٹ کو `nx dev`، `nx start` اور `nx build` سے پہلے چیک کرتا ہے اور فائلوں کی فہرست کے ساتھ رک جاتا ہے:

| موڈ | مسترد | پیغام |
|---|---|---|
| سرور | `.tsx`، `.jsx`، `.vue` یا `.svelte` `src/routes/` | کے تحت اجزاء کو `src/components/` پر منتقل کریں، یا `useCSR = True` | سیٹ کریں۔
| کلائنٹ | `src/routes/` | کے تحت کسی بھی `.nexy` فائل کو فریم ورک کے اجزاء کے طور پر لکھیں، یا سیٹ کریں `useCSR = False` |
| دونوں | `useFF` | `useFF must configure exactly one frontend framework` | میں ایک سے زیادہ فرنٹ اینڈ فریم ورک
| کلائنٹ | `useRouter` (ماڈیولر روٹر) | `useCSR requires file-based routing` |
| کلائنٹ | نہیں `useFF` | `useCSR requires a client framework` |

`_` یا `.` سے شروع ہونے والی فائلوں اور فولڈرز کو اس چیک سے نظر انداز کیا جاتا ہے۔

## کون سا

- **مواد، مارکیٹنگ، دستاویزات، SEO-پہلی سائٹس**: جزائر کے ساتھ سرور موڈ۔
- **بھرپور کلائنٹ نیویگیشن کے ساتھ ڈیش بورڈز اور ایپس**: کلائنٹ موڈ۔
- **ایک Python API جس کے اوپر کلائنٹ ایپ ہے**: کلائنٹ موڈ، صفحات کے آگے `.py` ہینڈلرز کے ساتھ۔

## اگلے اقدامات

- [لے آؤٹ](layouts/README.md)
- [رینڈرنگ](../../rendering/README.md)
- [ترتیب ](../../reference/config.md)
