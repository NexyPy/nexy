# ماڈیولر روٹنگ

ماڈیولر روٹنگ `src/routes/` کے تحت فائلوں کے بجائے ڈیکوریٹرز کے ساتھ کلاسز کا استعمال کرتی ہے: کنٹرولرز درخواستوں کو ہینڈل کرتے ہیں، ماڈیولز ان کو گروپ کرتے ہیں، اور فراہم کنندگان کو انجکشن لگایا جاتا ہے۔ نتیجے میں `APIRouter` کو `useRouter` کے ساتھ `nexyconfig.py` میں ماؤنٹ کریں۔

**شروع کرنے سے پہلے:** ایک Nexy پروجیکٹ اور ایک ورکنگ پیج۔ ماڈیولر راؤٹر فائل پر مبنی روٹر کی جگہ لے لیتا ہے، لہذا اگر آپ نے ابھی تک روٹر کا انتخاب نہیں کیا ہے تو پہلے [روٹنگ](../README.md) کو پڑھیں۔

| صفحہ | یہ کیا احاطہ کرتا ہے |
|---|---|
| یہ صفحہ | ایک ماڈیول ماؤنٹ کریں، کنٹرولر لکھیں، گروپ کنٹرولرز |
| [انحصار انجکشن](dependency-injection.md) | `@Injectable`، اسکوپس، کنٹینر |
| [گارڈز اور میٹا ڈیٹا](guards-and-metadata.md) | `@UseGuard`، `@Middleware`، `@UseRoute`، `@UseResponse` |
| [Nexy اور NestJS](vs-nestjs.md) | کیا میچ NestJS اور کیا نہیں؟ |

## راؤٹر سیٹ اپ کریں۔

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!NOTE]
> فائل پر مبنی روٹنگ کام کرتی رہتی ہے۔ اگر `src/routes/` موجود ہے تو اسے `useRouter` سیٹ ہونے پر بھی اسکین کیا جاتا ہے۔

## ایک کنٹرولر لکھیں۔

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

طریقے نام کے ساتھ مماثل ہیں، کیس غیر حساس: `get`، `post`، `put`، `patch`، `delete`، `options`، `head`، `trace`۔

ایک کنٹرولر ایک ہینڈلر فی HTTP طریقہ کا اعلان کرتا ہے۔ ایک ڈپلیکیٹ اسٹارٹ اپ پر اٹھتا ہے۔ `@Controller("/users")` کی پہلی دلیل وہ راستہ ہے جس پر ہر ہینڈلر جواب دیتا ہے، `/users/`۔ ایک کنٹرولر پر `async def SOCKET(...)` اسی راستے پر ایک WebSocket کو رجسٹر کرتا ہے۔

## ایک ماڈیول میں گروپ کنٹرولرز

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` ایک `APIRouter` لوٹاتا ہے۔ `controllers` درکار ہے۔ `providers`، `imports` اور `exports` اختیاری ہیں۔ درآمد شدہ ماڈیولز کو سب روٹرز کے طور پر نصب کیا جاتا ہے، اور ان کے برآمد شدہ فراہم کنندگان کو آغاز پر حل کیا جاتا ہے۔

## ایک کنٹرولر سے ملاحظات

ایک کنٹرولر ایک صفحہ واپس کر سکتا ہے۔ `useViews` ایک `.nexy` منظر پیش کرتا ہے۔ لے آؤٹ میں لپیٹنے کے لیے ایک دوسرے کے اندر گھونسلا:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller()
class AppController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/app_view.nexy"),
        })
```

دیکھیں [لے آؤٹس](../fbr/layouts/README.md)۔

## مثال

دیکھئے `examples/Modular/api/minimal/`۔

## اگلے اقدامات

- [انحصار انجیکشن](dependency-injection.md): خدمات اور دائرہ کار
- [گارڈز اور میٹا ڈیٹا](guards-and-metadata.md): راستوں کی حفاظت اور دستاویز کریں۔
- [روٹنگ](../README.md): فائل پر مبنی روٹر
- [ترتیب ](../../reference/config.md): ہر آپشن، بشمول `useRouter`
