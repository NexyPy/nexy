# فائل پر مبنی روٹنگ

روٹ ایک فائل ہے۔ یو آر ایل فائل کا راستہ ہے `src/routes/`، مائنس ایکسٹینشن کی نسبت۔

## URL پر فائل کریں۔

| فائل | URL |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` اس کی ڈائرکٹری کے نقشے بناتا ہے، `/index` میں نہیں۔ قوسین میں ایک ڈائریکٹری ایک **گروپ** ہے: یہ فائلوں کو URL میں ظاہر کیے بغیر ترتیب دیتی ہے۔

کلائنٹ موڈ میں صفحہ کی فائلیں `.nexy` کے بجائے `.tsx`، `.vue` یا `.svelte` ہیں؛ یو آر ایل کے قوانین ایک جیسے ہیں۔

اس ٹیبل کی دو فائلیں: ایک صفحہ جو اس کے حصے کو پڑھتا ہے، اور ایک ہینڈلر جو JSON کا جواب دیتا ہے۔

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

## دو موڈ

`useCSR` فیصلہ کرتا ہے کہ صفحات کیا ہیں۔ دونوں کو ایک پروجیکٹ میں ملایا نہیں جا سکتا: جب سرور کا صفحہ کلائنٹ کے راستے کے ساتھ بیٹھتا ہے تو Nexy شروع ہونے سے انکار کر دیتا ہے۔

| موڈ | صفحات | روٹ لے آؤٹ | دیکھیں |
|---|---|---|---|
| سرور (`useCSR = False`) | `.nexy`، `.md`، `.mdx` | `layout.nexy` | [سرور موڈ اور کلائنٹ موڈ](modes.md) |
| کلائنٹ (`useCSR = True`) | فریم ورک فائلیں | `layout.tsx` | [layout.tsx](../../views/react/differences.md) |

`.py` فائلیں دونوں طریقوں میں API ہینڈلر ہیں۔

سوئچ کی ایک لائن ہے `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True  # client mode: src/routes/*.tsx are the pages
```

## جو راستہ نہیں ہے۔

- محفوظ فائل کے نام: `layout.*`، `loading.nexy`، `errors.nexy`، `notfound.nexy`، `dependencies.py`، `middleware.py`، `__init__.py`۔
- فائلز اور فولڈرز جو `_` یا `.` سے شروع ہوتے ہیں: انہیں جزوی اور ڈرافٹ کے لیے استعمال کریں۔
- ایکسٹینشنز جو آپ کے پروجیکٹ کے لیے فعال نہیں ہیں۔ ایک فائل جس کی توسیع غیر فعال ہے ایک انتباہ کے ساتھ چھوڑ دیا جاتا ہے۔

```text
src/routes/
├─ layout.nexy          wraps the pages, not a route
├─ middleware.py        wraps the requests, not a route
├─ index.nexy           /
├─ _card.nexy           a partial: no URL
└─ .draft.nexy          a draft: no URL
```

## ایک فائل فی URL

دو فائلیں جو ایک ہی URL کو حل کرتی ہیں دونوں رجسٹر ہوتی ہیں۔ `blog/index.nexy` کے آگے `blog.nexy` نہ بنائیں، اور ایک ہی راستے کے لیے `index.nexy` اور `index.py` کو مکس نہ کریں۔ ایک چنو۔

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: delete one of the two
```

## اس حصے میں

| فولڈر | یہ کیا احاطہ کرتا ہے |
|---|---|
| [صفحات/](pages/README.md) | صفحات، [متحرک راستے](pages/dynamic-routes.md)، روٹ گروپس |
| [ترتیب/](layouts/README.md) | ایک صفحہ فی لے آؤٹ فائل کی قسم |
| [سنبھالنے والے/](handlers/README.md) | `.py` ہینڈلر، توثیق اور غلطیاں |
| [انحصار/](dependencies/README.md) | `dependencies.py`، گارڈز |
| [مڈل ویئر/](middleware/README.md) | `middleware.py` |
| [غلطیاں/](errors/README.md) | نہ ملے اور خرابی والے صفحات |
| [نیویگیشن/](navigation/linking-and-navigating.md) | لنکس، ہکس |
| [حقیقی وقت/](realtime/websocket.md) | WebSocket |
| [وراثت](inheritance.md) | ایک میز میں وراثت کے قوانین |

## اگلے اقدامات

- [سرور موڈ اور کلائنٹ موڈ](modes.md)
- [لے آؤٹ](layouts/README.md)
- [ماڈیولر روٹنگ](../modular/README.md)
