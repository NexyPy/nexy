# پروجیکٹ کا ڈھانچہ

Nexy پروجیکٹ میں ہر فائل کا ایک کام ہوتا ہے، اور یہ کہاں جاتی ہے اس کا انحصار راؤٹر پر ہوتا ہے: `src/routes/` فائل پر مبنی روٹنگ کے لیے، `src/apps/` ماڈیولر روٹر کے لیے۔

## ٹاپ لیول

<!-- router:fbr -->
```text
my-app/
├─ src/
│  ├─ routes/            every file is a route
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

فولڈر کا انتخاب کرنے کے لیے پوچھیں کہ فائل کیا ہے:

- **کوئی چیز جسے براؤزر کھول سکتا ہے** - ایک راستہ: `src/routes/`۔
- **ایک ٹکڑا جو کئی راستوں سے استعمال ہوتا ہے** - ایک جزو یا ماڈیول: `src/components/`، `src/`۔
- **ایک فائل پیش کی گئی جیسا کہ یہ ہے** - `public/`۔
- **پیدا کردہ** - `__nexy__/`؛ کبھی اس میں ترمیم نہ کریں

> [!WARNING]
> `src/routes/` اسکین کیا جاتا ہے: وہاں رکھا ہوا مددگار راستہ بن جاتا ہے۔ ایک مددگار رکھیں جو باہر کا راستہ نہیں ہے `src/routes/`، یا اس کا نام `_` سے شروع کریں۔
<!-- /router -->

<!-- router:modular -->
```text
my-app/
├─ src/
│  ├─ apps/              controllers, modules and their views
│  │  ├─ app_module.py   the root module, given to useRouter
│  │  ├─ app_controller.py
│  │  ├─ app_view.nexy   a view a controller returns
│  │  ├─ layout.nexy     the frame the controllers pass their view to
│  │  └─ users/          one folder per feature: controller, module, service, model
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = AppModule
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

فولڈر کا انتخاب کرنے کے لیے پوچھیں کہ فائل کیا ہے:

- **یو آر ایل** - `src/apps/` میں کنٹرولر کا ایک طریقہ، اس کے ماڈیول کے ذریعے رجسٹرڈ۔
- **ایک صفحہ** - اس کے کنٹرولر کے ساتھ ایک `.nexy` منظر، `useViews` کے ساتھ واپس آیا۔
- **ایک ٹکڑا جو متعدد آراء سے استعمال ہوتا ہے** - `src/components/`۔
- **ایک فائل پیش کی گئی جیسا کہ یہ ہے** - `public/`۔
- **پیدا کردہ** - `__nexy__/`؛ کبھی اس میں ترمیم نہ کریں
<!-- /router -->

<!-- router:custom -->
```text
my-app/
├─ src/
│  ├─ legacy/            the FastAPI router you include
│  │  └─ api.py          router = APIRouter(prefix="/api")
│  ├─ routes/            pages and route files, served next to it
│  │  └─ index.nexy      → /
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = router
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

فولڈر کا انتخاب کرنے کے لیے پوچھیں کہ فائل کیا ہے:

- **شامل ایپ کا روٹ** - جہاں یہ پہلے سے موجود ہے، یہاں `src/legacy/`۔
- **ایک نیا صفحہ یا راستہ** - `src/routes/`، شامل روٹر کے ساتھ۔
- **ایک فائل پیش کی گئی جیسا کہ یہ ہے** - `public/`۔
- **پیدا کردہ** - `__nexy__/`؛ کبھی اس میں ترمیم نہ کریں
<!-- /router -->

<!-- router:fbr,custom -->
## `src/routes/`

ہر فائل ایک راستہ بن جاتی ہے، سوائے ذیل کے محفوظ ناموں کے۔ فائل پاتھ مائنس ایکسٹینشن یو آر ایل ہے - دیکھیں [فائل پر مبنی روٹنگ](../routing/fbr/README.md)۔

| فائل | کردار |
|---|---|
| `layout.nexy` | بہن بھائی اور بچوں کے صفحات کو لپیٹتا ہے۔ |
| `errors.nexy` | ڈائریکٹری کے لیے 500 صفحہ |
| `notfound.nexy` | ڈائریکٹری کے لیے 404 صفحہ |
| `dependencies.py` | ڈائریکٹری کے لیے اشتراک کردہ FastAPI انحصار |
| `__init__.py` | Python پیکیج مارکر |
| `loading.nexy` | reserved - راستوں سے خارج، لیکن ابھی تک اس کا کوئی رن ٹائم اثر نہیں ہے۔ |

ہر صفحہ کا نام بھی فی فریم ورک موجود ہے۔ `react()` کنفیگر ہونے کے ساتھ، `layout.jsx` اور `layout.tsx` بالکل `layout.nexy` کی طرح محفوظ ہیں۔ فہرستیں `nexy/core/config.py` (`LAYOUT_FILE_NAMES`، `ERROR_FILE_NAMES`، `NOTFOUND_FILE_NAMES`، `LOADING_FILE_NAMES`) میں بنائی گئی ہیں۔

> [!NOTE]
> `notfound.nexy` اور `errors.nexy` صرف اس وقت انسٹال ہوتے ہیں جب روٹس روٹ پر ایک کاپی موجود ہو۔ ذیلی ڈائرکٹری میں ایک کاپی پھر اس سابقے کے لیے صفحہ کو بہتر بناتی ہے۔
<!-- /router -->

<!-- router:modular -->
## `src/apps/`

ایک کنٹرولر یو آر ایل کا جواب دیتا ہے، ایک ماڈیول گروپ کنٹرولرز اور فراہم کنندگان، اور روٹ ماڈیول `useRouter` کے ساتھ `nexyconfig.py` میں نصب ہوتا ہے:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller()
class AppController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/app_view.nexy")})
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    useAliases = {"@": "src"}  # the views import @/components/...
```

`src/apps/` میں کوئی فائل اس کے نام سے روٹ نہیں ہے: صرف کنٹرولرز ایک ماڈیول جواب دیتا ہے۔ دیکھیں [ماڈیولر روٹنگ](../routing/modular/README.md)۔
<!-- /router -->

## `public/`

یہاں فائلیں سائٹ روٹ سے پیش کی جاتی ہیں: `/favicon.ico`، `/robots.txt`، تصاویر، فونٹس۔

## `__nexy__/`

`nx build` (اور `nx dev` کے ذریعہ اس کی ضرورت کے حصوں کے لئے) کے ذریعہ تیار کردہ۔ اس میں شامل ہیں:

- مرتب کردہ `.nexy` فائلیں، بطور Python پیکیج (`__nexy__/src/...`)؛
- پیدا کردہ کلائنٹ کے اندراج پوائنٹس (`main.ts`، `vite.ts`، `*.auto.ts`؛
- `client/` ایک Vite تعمیر کے بعد - اثاثے، ظاہر، پہلے سے پیش کردہ HTML؛
- `build-cache.json`۔

پوری ڈائرکٹری کو ڈسپوزایبل سمجھیں: اسے حذف کریں، اسے دوبارہ بنائیں۔ ہاتھ سے اس میں ترمیم کرنے سے اگلی تعمیر میں تبدیلی ختم ہوجاتی ہے۔ اسے `.gitignore` میں شامل کریں۔

## اگلے اقدامات

<!-- router:fbr -->
- [فائل پر مبنی روٹنگ](../routing/fbr/README.md): راستہ یو آر ایل کیسے بنتا ہے۔
<!-- /router -->
<!-- router:modular -->
- [ماڈیولر روٹنگ](../routing/modular/README.md): کنٹرولرز، ماڈیولز اور فراہم کرنے والے
<!-- /router -->
<!-- router:custom -->
- [حسب ضرورت روٹنگ](../routing/custom/README.md): ایک موجودہ FastAPI روٹر شامل کریں۔
<!-- /router -->
- [کنفیگ ](../reference/config.md): ہر پروجیکٹ کا آپشن
- [فرنٹ اینڈ ](../guides/frontend.md): Vite، اسٹائلنگ اور کلائنٹ کی تعمیر
