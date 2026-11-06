# Nexy کیا ہے؟

Nexy فل اسٹیک ویب ایپلیکیشنز کے لیے ایک Python فریم ورک ہے: آپ کے صفحات اور آپ کا API ایک پروجیکٹ میں رہتے ہیں اور ایک سرور کے ذریعے پیش کیا جاتا ہے۔

## جو آپ کو ملتا ہے۔

- **میں صفحات Python** ایک `.nexy` فائل HTML ہے جس کے اوپر Python کی چند لائنیں ہیں۔ ایک `.md` فائل بھی ایک صفحہ ہے۔ صفحہ کو رینڈر کرنے کے لیے کسی JavaScript کی ضرورت نہیں ہے۔
<!-- router:fbr -->
- **اسی میں ایک API پروجیکٹ** `src/routes/` کے تحت ایک `.py` فائل HTTP درخواستوں کا جواب دیتی ہے: `GET` نامی فنکشن جواب دیتا ہے `GET`، `POST` نامی فنکشن `POST` کا جواب دیتا ہے۔
<!-- /router -->
<!-- router:modular -->
- **اسی میں ایک API پروجیکٹ** ایک کنٹرولر HTTP درخواستوں کا جواب دیتا ہے: اس کا طریقہ `get` جوابات `GET`، اس کا طریقہ `post` جوابات `POST`، اور ایک ماڈیول گروپ کنٹرولرز اور ان کی خدمات۔
<!-- /router -->
<!-- router:custom -->
- **اسی میں ایک API پروجیکٹ** آپ کے پاس پہلے سے موجود FastAPI راؤٹر جواب دیتا رہتا ہے، اور `src/routes/` کے جوابات کے صفحات اور روٹ فائلیں اس کے ساتھ ہیں۔
<!-- /router -->
- **API دستاویزات برائے مفت** ہر API روٹ ایک OpenAPI اسکیما میں ظاہر ہوتا ہے، اور اسکیلر اسے `/docs` پر ایک انٹرایکٹو حوالہ کے طور پر دکھاتا ہے۔
- **فارم جو کال کرتے ہیں۔ Python.** ایک فارم، یا براؤزر سے ٹائپ شدہ کال، اسی Python فنکشن تک پہنچتی ہے۔
- **جب آپ چاہیں فرنٹ اینڈ فریم ورک ایک** React، Vue، Svelte، Solid یا Preact، ایک جزو یا پوری سائٹ کے لیے۔
- **کام کرنے کا ایک حکم، ایک کو جہاز** `nx dev` جب آپ بچاتے ہیں تو دوبارہ لوڈ ہوتا ہے۔ `nx build` پیداوار تیار کرتا ہے۔

## جس پر بنایا گیا ہے۔

موجودہ ورژن، 2.2، ان ٹولز پر کھڑا ہے جو آپ کو پہلے سے معلوم ہو سکتا ہے:

| حصہ | پر بنایا گیا۔ | آپ کے لیے اس کا کیا مطلب ہے۔ |
|---|---|---|
| سرور اور API | [FastAPI](https://fastapi.tiangolo.com/) | API روٹ ایک FastAPI راستہ ہے: Pydantic توثیق اور انحصار معمول کے مطابق کام کرتے ہیں |
| API حوالہ | OpenAPI اور [Scalar](https://scalar.com/) | اسکیما `/openapi.json` پر ہے، حوالہ `/docs` پر ہے |
| صفحات | Jinja2 | ایک `.nexy` صفحہ Jinja2 ٹیگ استعمال کرتا ہے جیسے `{{ title }}` |
| فرنٹ اینڈ (اختیاری) | [Vite](https://vite.dev/) | صرف ایک فرنٹ اینڈ فریم ورک کے ساتھ، جس کی بھی ضرورت ہے Node.js |

## پہلا صفحہ اور پہلا اختتامی نقطہ

<!-- router:fbr,custom -->
ایک صفحہ، `/hello` پر:

```nexy filename="src/routes/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

ایک اختتامی نقطہ، `GET /api/items` پر، بغیر کسی اضافی کوڈ کے `/docs` پر درج ہے:

```python filename="src/routes/api/items.py"
from nexy.http import Request


async def GET(request: Request):
    return {"items": []}
```
<!-- /router -->

<!-- router:modular -->
ایک منظر، اور کنٹرولرز جو جواب دیتے ہیں `/hello/` اور `GET /api/items/`۔ اختتامی نقطہ بغیر کسی اضافی کوڈ کے `/docs` پر درج ہے، اور یو آر ایل اس کی آخری سلیش کے بغیر اس کی طرف ری ڈائریکٹ کرتا ہے:

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

```python filename="src/apps/hello_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews("src/apps/hello_view.nexy", context={"title": "Hello"})


@Controller("/api/items")
class ItemsController:
    async def get(self):
        return {"items": []}
```

روٹ ماڈیول ان کی فہرست دیتا ہے، اور `useRouter = AppModule` `nexyconfig.py` میں اسے ماؤنٹ کرتا ہے:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .hello_controller import HelloController, ItemsController


@Module()
class AppModule:
    controllers = [HelloController, ItemsController]
```
<!-- /router -->

## Nexy آپ کے لیے کیا چھوڑتا ہے۔

ڈیٹابیس، لاگ ان اور اس بارے میں قواعد جو آپ کی درخواست سے تعلق رکھتے ہیں کون کر سکتا ہے، لہذا آپ لائبریریوں کا انتخاب کرتے ہیں۔ [ڈیٹا بیس](../guides/databases.md) اور [مڈل ویئر اور سیکیورٹی](../guides/middleware-and-security.md) دکھاتے ہیں کہ ہر ایک کہاں پلگ ان ہوتا ہے۔

## اگلے اقدامات

- [انسٹالیشن](installation.md): انسٹال کریں uv اور ایک پروجیکٹ بنائیں
- [فوری آغاز](quick-start.md): اسے چلائیں، صفحہ تبدیل کریں، اسے بنائیں
- [بنیادی تصورات](core-concepts.md): چند الفاظ جو باقی دستاویزات استعمال کرتے ہیں۔
