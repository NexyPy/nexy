# فوری آغاز

آپ ایک Nexy پروجیکٹ بنائیں گے، اسے چلائیں گے، اور اس میں ترمیم کرتے ہی صفحہ کی تبدیلی دیکھیں گے۔ اس میں تین منٹ لگتے ہیں۔ [ٹیوٹوریل](tutorial.md) پھر ایک اختتامی نقطہ اور پیداوار کی تعمیر کا اضافہ کرتا ہے۔

## اس سے پہلے کہ آپ شروع کریں۔

| آپ کی ضرورت ہے۔ | کیوں |
|---|---|
| Python 3.12+ | `requires-python` میں `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | فراہم کرتا ہے `uvx`، پروجیکٹ بناتا ہے اور اس کے پیکجز کو انسٹال کرتا ہے۔ |
| Node.js 18+ | صرف اس صورت میں جب آپ کلائنٹ کا فریم ورک استعمال کرتے ہیں (React، Vue، Svelte، Solid، Preact) |

ابھی تک نہیں uv؟ دیکھیں [انسٹالیشن](installation.md)۔

## 1. پروجیکٹ بنائیں

```bash
uvx nexy new my-app
```

`uvx` uv کے ساتھ آتا ہے، لہذا پہلے uv کو انسٹال کریں۔ یہ Nexy کو ایک عارضی ماحول میں چلاتا ہے، جو پروجیکٹ کو **بنانے** کے لیے کافی ہے۔ `nexy new` پھر پروجیکٹ کو اپنا بناتا ہے `.venv` اور اس کے پیکج وہاں انسٹال کرتا ہے۔ چار اشارے وائرنگ کا فیصلہ کرتے ہیں:

| پرامپٹ | اثر |
|---|---|
| فائل پر مبنی روٹر؟ | `Yes` اسکین `src/routes/`؛ `No` ماڈیولر راؤٹر کو `src/apps/` |
| پروجیکٹ کی قسم | `Web` ایک لے آؤٹ اور کلائنٹ کے اثاثوں کو شامل کرتا ہے، `API` بغیر دیکھے شروع ہوتا ہے |
| کلائنٹ جزو؟ | ایک فریم ورک اور اس کا Vite سیٹ اپ شامل کرتا ہے۔ |
| ORM / ڈیٹا بیس | ایک ماڈل پرت، یا کچھ بھی نہیں شامل کرتا ہے۔ |

یقین نہیں ہے؟ جواب `Yes`، `Web`، اور کلائنٹ کا کوئی جزو نہیں۔ آپ ہر ایک کو بعد میں شامل کر سکتے ہیں۔

## 2. اسے چلائیں۔

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

کھولیں <http://localhost:3000>۔ آپ کو اسٹارٹر صفحہ دیکھنا چاہئے۔ بندرگاہ `usePort` (پہلے سے طے شدہ `3000`) سے آتی ہے۔ `--port` اور `--host` اسے فی رن اوور رائیڈ کرتے ہیں۔

> [!NOTE]
> پروجیکٹ کے ورچوئل ماحول کے اندر `new` اور `init` کے علاوہ ہر کمانڈ کو چلائیں، یا `uv run` کے ساتھ سابقہ ​​لگائیں، جیسا کہ `uv run nexy dev` میں ہے۔ اس کے باہر، ایک پروجیکٹ جس کی ضرورت ہے `sqlmodel` `No module named 'sqlmodel'` کے ساتھ ناکام ہو جاتی ہے۔

## 3. صفحہ تبدیل کریں۔

<!-- router:fbr,custom -->
`src/routes/` کے تحت فائل ایک راستہ ہے۔ بنائیں `src/routes/hello.nexy`:

```nexy filename="src/routes/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```
<!-- /router -->

<!-- router:modular -->
ایک کنٹرولر ایک منظر واپس کرتا ہے۔ بنائیں `src/apps/hello_view.nexy`:

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

پھر صفحہ کو `src/apps/app_controller.py` میں ڈیکلیئر کریں اور اسے ماڈیول میں شامل کریں:

```python filename="src/apps/app_controller.py"
@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/hello_view.nexy")})
```

```python filename="src/apps/app_module.py"
from .app_controller import AboutController, AppController, HelloController

controllers = [AppController, AboutController, HelloController]
```
<!-- /router -->

کھولیں <http://localhost:3000/hello>۔ `"Hello"` کو `"Bonjour"` میں تبدیل کریں اور محفوظ کریں: صفحہ دستی دوبارہ لوڈ کیے بغیر اپ ڈیٹ ہوجاتا ہے۔ اگر کوڈ غلط ہے تو، براؤزر خالی صفحہ کی بجائے غلطی دکھاتا ہے۔

`prop[str]` ٹائپ شدہ پراپرٹی کا اعلان کرتا ہے۔ فرنٹ میٹر کے تحت مارک اپ ہے Jinja2 - دیکھیں [.nexy فائلیں](../views/nexy/README.md)۔

## جہاں اگلا

| آپ چاہتے ہیں۔ | پڑھیں |
|---|---|
| ایک Python اختتامی نقطہ شامل کریں اور ایک تعمیر بھیجیں۔ | [ٹیوٹوریل](tutorial.md) |
| جانیں کہ ہر فائل کہاں سے تعلق رکھتی ہے۔ | [پروجیکٹ ڈھانچہ](project-structure.md) |
| سمجھیں کہ کون کیا بناتا ہے۔ | [Nexy کیسے کام کرتا ہے](how-nexy-works.md) |
| React، Vue، Svelte، Solid یا Preact استعمال کریں۔ | [ملاحظات](../views/README.md) |
