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

## دو موڈ

`useCSR` فیصلہ کرتا ہے کہ صفحات کیا ہیں۔ دونوں کو ایک پروجیکٹ میں ملایا نہیں جا سکتا: جب سرور کا صفحہ کلائنٹ کے راستے کے ساتھ بیٹھتا ہے تو Nexy شروع ہونے سے انکار کر دیتا ہے۔

| موڈ | صفحات | روٹ لے آؤٹ | دیکھیں |
|---|---|---|---|
| سرور (`useCSR = False`) | `.nexy`، `.md`، `.mdx` | `layout.nexy` | [سرور موڈ اور کلائنٹ موڈ](modes.md) |
| کلائنٹ (`useCSR = True`) | فریم ورک فائلیں | `layout.tsx` | [layout.tsx](../../views/react/differences.md) |

`.py` فائلیں دونوں طریقوں میں API ہینڈلر ہیں۔

## جو راستہ نہیں ہے۔

- محفوظ فائل کے نام: `layout.*`، `loading.nexy`، `errors.nexy`، `notfound.nexy`، `dependencies.py`، `middleware.py`، `__init__.py`۔
- فائلز اور فولڈرز جو `_` یا `.` سے شروع ہوتے ہیں: انہیں جزوی اور ڈرافٹ کے لیے استعمال کریں۔
- ایکسٹینشنز جو آپ کے پروجیکٹ کے لیے فعال نہیں ہیں۔ ایک فائل جس کی توسیع غیر فعال ہے ایک انتباہ کے ساتھ چھوڑ دیا جاتا ہے۔

## ایک فائل فی URL

دو فائلیں جو ایک ہی URL کو حل کرتی ہیں دونوں رجسٹر ہوتی ہیں۔ `blog/index.nexy` کے آگے `blog.nexy` نہ بنائیں، اور ایک ہی راستے کے لیے `index.nexy` اور `index.py` کو نہ ملا دیں۔ ایک چنو۔

## اس حصے میں

| فولڈر | اس میں کیا شامل ہے |
|---|---|
| [صفحات/](pages/README.md) | صفحات، [متحرک راستے](pages/dynamic-routes.md)، روٹ گروپس |
| [layouts/](layouts/README.md) | ایک صفحہ فی لے آؤٹ فائل کی قسم |
| [ہینڈلرز/](handlers/README.md) | `.py` ہینڈلرز، توثیق اور غلطیاں |
| [انحصارات/](dependencies/README.md) | `dependencies.py`، محافظ |
| [مڈل ویئر/](middleware/README.md) | `middleware.py` |
| [غلطیاں/](errors/README.md) | نہ ملے اور غلطی کے صفحات |
| [نیویگیشن/](navigation/linking-and-navigating.md) | لنکس، ہکس |
| [حقیقی وقت/](realtime/websocket.md) | WebSocket |
| [وراثت](inheritance.md) | ایک میز میں وراثت کے قواعد |

## اگلے اقدامات

- [سرور موڈ اور کلائنٹ موڈ](modes.md)
- [لے آؤٹ](layouts/README.md)
- [ماڈیولر روٹنگ ](../modular/README.md)
